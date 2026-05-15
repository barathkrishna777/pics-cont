"""Minimal disk-on-roadmap CSD-PIBT prototype.

This module intentionally models a restricted problem: disk agents occupy
roadmap vertices, candidate motions are finite linear primitives over one
shield tick, and safety is checked by conservative time-sampled capsules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot, inf
from time import perf_counter
from typing import Mapping


Point = tuple[float, float]
AgentId = str
VertexId = str


@dataclass(frozen=True)
class Roadmap:
    vertices: Mapping[VertexId, Point]
    edges: Mapping[VertexId, tuple[VertexId, ...]]

    def neighbors(self, vertex: VertexId) -> tuple[VertexId, ...]:
        return tuple(sorted(self.edges.get(vertex, ())))

    def distance(self, a: VertexId, b: VertexId) -> float:
        ax, ay = self.vertices[a]
        bx, by = self.vertices[b]
        return hypot(ax - bx, ay - by)

    def has_edge(self, a: VertexId, b: VertexId) -> bool:
        return b in self.edges.get(a, ()) or a == b

    def on_clearance_cycle(self, start: VertexId, through: VertexId | None = None) -> bool:
        """Return whether the local adjacency has an alternate route cycle."""
        if through is None or start == through:
            neighbors = self.neighbors(start)
            if len(neighbors) < 2:
                return False
            for idx, left in enumerate(neighbors):
                for right in neighbors[idx + 1 :]:
                    if self._connected_without(left, right, banned_vertex=start):
                        return True
            return False
        banned = {tuple(sorted((start, through)))}
        frontier = [start]
        seen = {start}
        while frontier:
            node = frontier.pop()
            for nxt in self.neighbors(node):
                if tuple(sorted((node, nxt))) in banned:
                    continue
                if nxt == through:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        return False

    def _connected_without(self, start: VertexId, goal: VertexId, banned_vertex: VertexId) -> bool:
        frontier = [start]
        seen = {start, banned_vertex}
        while frontier:
            node = frontier.pop()
            for nxt in self.neighbors(node):
                if nxt == goal:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        return False


@dataclass(frozen=True)
class AgentState:
    vertex: VertexId
    radius: float = 0.2
    priority_age: float = 0.0
    progress_debt: int = 0


@dataclass(frozen=True)
class Candidate:
    id: str
    agent_id: AgentId
    start: VertexId
    end: VertexId
    t0: float
    t1: float
    score: float
    provenance: str
    feasible: bool = True

    @property
    def duration(self) -> float:
        return max(0.0, self.t1 - self.t0)

    def position_at(self, roadmap: Roadmap, t: float) -> Point:
        sx, sy = roadmap.vertices[self.start]
        ex, ey = roadmap.vertices[self.end]
        if self.duration == 0 or t <= self.t0:
            return (sx, sy)
        if t >= self.t1:
            return (ex, ey)
        ratio = (t - self.t0) / self.duration
        return (sx + (ex - sx) * ratio, sy + (ey - sy) * ratio)


@dataclass(frozen=True)
class Reservation:
    agent_id: AgentId
    candidate: Candidate


@dataclass(frozen=True)
class Dependency:
    requester: AgentId
    blocker: AgentId
    requester_candidate: str
    blocker_candidate: str
    conflict_interval: tuple[float, float]
    conflict_geometry: Point
    relation: str


@dataclass
class Diagnostics:
    collisions: int = 0
    min_clearance: float = inf
    deadlock: bool = False
    livelock: bool = False
    time_to_progress: dict[AgentId, int] = field(default_factory=dict)
    backtrack_count: int = 0
    dependency_scc_size: int = 0
    candidate_rejection_reasons: dict[str, int] = field(default_factory=dict)
    fallback_trigger_count: int = 0
    step_time_ms: float = 0.0
    candidate_count: dict[AgentId, int] = field(default_factory=dict)
    dependency_log: list[Dependency] = field(default_factory=list)
    no_progress_certificate: bool = False

    def reject(self, reason: str) -> None:
        self.candidate_rejection_reasons[reason] = (
            self.candidate_rejection_reasons.get(reason, 0) + 1
        )


@dataclass(frozen=True)
class ShieldConfig:
    tick: float = 1.0
    margin: float = 0.05
    collision_samples: int = 16
    max_visits: int = 10_000
    enable_inheritance: bool = True
    enable_backtracking: bool = True
    enable_retiming: bool = True
    enable_priority_aging: bool = True


def _dist(a: Point, b: Point) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def conflict_between(
    left: Candidate,
    right: Candidate,
    states: Mapping[AgentId, AgentState],
    roadmap: Roadmap,
    config: ShieldConfig = ShieldConfig(),
) -> tuple[bool, tuple[float, float], Point, float]:
    """Conservative sampled swept-disk collision check."""
    lo = max(left.t0, right.t0)
    hi = min(left.t1, right.t1)
    if lo > hi:
        return False, (lo, hi), (0.0, 0.0), inf

    threshold = states[left.agent_id].radius + states[right.agent_id].radius + config.margin
    min_clearance = inf
    first: float | None = None
    last: float | None = None
    geometry = (0.0, 0.0)
    samples = max(2, config.collision_samples)
    for idx in range(samples + 1):
        t = lo + (hi - lo) * idx / samples
        lp = left.position_at(roadmap, t)
        rp = right.position_at(roadmap, t)
        clearance = _dist(lp, rp) - threshold
        min_clearance = min(min_clearance, clearance)
        if clearance < 0:
            first = t if first is None else first
            last = t
            geometry = ((lp[0] + rp[0]) / 2, (lp[1] + rp[1]) / 2)
    return first is not None, (first or lo, last or hi), geometry, min_clearance


def _goal_distance(roadmap: Roadmap, vertex: VertexId, goal: VertexId) -> float:
    return _dist(roadmap.vertices[vertex], roadmap.vertices[goal])


def _candidate_bank(
    agent_id: AgentId,
    state: AgentState,
    goal: VertexId,
    roadmap: Roadmap,
    previous: Candidate | None,
    inherited: Dependency | None,
    config: ShieldConfig,
) -> list[Candidate]:
    tick = config.tick
    candidates: list[Candidate] = []

    def add(end: VertexId, t0: float, t1: float, provenance: str, bonus: float = 0.0) -> None:
        if not roadmap.has_edge(state.vertex, end):
            return
        score = _goal_distance(roadmap, end, goal) + t0 * 0.1 - bonus
        candidates.append(
            Candidate(
                id=f"{agent_id}:{provenance}:{state.vertex}->{end}@{t0:.2f}-{t1:.2f}",
                agent_id=agent_id,
                start=state.vertex,
                end=end,
                t0=t0,
                t1=t1,
                score=score,
                provenance=provenance,
            )
        )

    if previous and previous.end == state.vertex:
        add(previous.end, 0.0, tick, "continue_previous", bonus=0.05)

    add(state.vertex, 0.0, tick, "wait", bonus=-0.25)
    if state.vertex == goal and inherited is not None and not roadmap.on_clearance_cycle(state.vertex):
        return sorted(candidates, key=lambda c: (c.score, c.t0, c.end, c.provenance))

    neighbors = roadmap.neighbors(state.vertex)
    ordered = sorted(neighbors, key=lambda v: (_goal_distance(roadmap, v, goal), v))
    for neighbor in ordered:
        add(neighbor, 0.0, tick, "traverse", bonus=0.3)
        if config.enable_retiming:
            add(neighbor, tick * 0.35, tick * 1.35, "delayed_traverse", bonus=0.1)
            add(neighbor, 0.0, tick * 1.4, "speed_scaled", bonus=0.05)
    if inherited is not None:
        blocker_end = inherited.conflict_geometry
        clearing = sorted(
            neighbors,
            key=lambda v: _dist(roadmap.vertices[v], blocker_end),
            reverse=True,
        )
        for neighbor in clearing[:2]:
            add(neighbor, 0.0, tick, "inherited_clear", bonus=0.8)

    dedup: dict[tuple[VertexId, float, float, str], Candidate] = {}
    for candidate in candidates:
        dedup[(candidate.end, candidate.t0, candidate.t1, candidate.provenance)] = candidate
    return sorted(dedup.values(), key=lambda c: (c.score, c.t0, c.end, c.provenance))


def shield_step(
    states: Mapping[AgentId, AgentState],
    goals: Mapping[AgentId, VertexId],
    roadmap: Roadmap,
    previous_reservations: Mapping[AgentId, Candidate] | None = None,
    config: ShieldConfig = ShieldConfig(),
) -> tuple[dict[AgentId, Candidate], Diagnostics]:
    """Reserve one finite candidate per agent with PIBT-style inheritance."""
    started = perf_counter()
    previous_reservations = previous_reservations or {}
    diagnostics = Diagnostics()
    candidates: dict[AgentId, list[Candidate]] = {}
    reservations: dict[AgentId, Candidate] = {}
    visits: set[tuple[AgentId, str, tuple[tuple[AgentId, str], ...]]] = set()

    def priority(agent_id: AgentId, inherited_priority: float | None = None) -> float:
        age = states[agent_id].priority_age if config.enable_priority_aging else 0.0
        base = age - sorted(states).index(agent_id) * 1e-6
        return max(base, inherited_priority if inherited_priority is not None else -inf)

    for agent_id, state in states.items():
        bank = _candidate_bank(
            agent_id,
            state,
            goals[agent_id],
            roadmap,
            previous_reservations.get(agent_id),
            None,
            config,
        )
        candidates[agent_id] = bank
        diagnostics.candidate_count[agent_id] = len(bank)

    def blocking_conflicts(agent_id: AgentId, candidate: Candidate, inherited_prio: float) -> list[Dependency]:
        deps: list[Dependency] = []
        for other_id in sorted(states):
            if other_id == agent_id:
                continue
            other = reservations.get(
                other_id,
                Candidate(
                    id=f"{other_id}:current_hold",
                    agent_id=other_id,
                    start=states[other_id].vertex,
                    end=states[other_id].vertex,
                    t0=0.0,
                    t1=config.tick,
                    score=0.0,
                    provenance="current_hold",
                ),
            )
            has_conflict, interval, geometry, clearance = conflict_between(
                candidate, other, states, roadmap, config
            )
            diagnostics.min_clearance = min(diagnostics.min_clearance, clearance)
            if has_conflict:
                relation = "retime" if config.enable_retiming else "vacate_by"
                deps.append(
                    Dependency(agent_id, other_id, candidate.id, other.id, interval, geometry, relation)
                )
        return deps

    def reserve(agent_id: AgentId, inherited: Dependency | None, inherited_prio: float | None) -> bool:
        if len(visits) > config.max_visits:
            diagnostics.reject("visited_bound")
            return False
        bank = candidates[agent_id]
        if inherited is not None:
            bank = _candidate_bank(
                agent_id,
                states[agent_id],
                goals[agent_id],
                roadmap,
                previous_reservations.get(agent_id),
                inherited,
                config,
            )
        my_priority = priority(agent_id, inherited_prio)
        for candidate in bank:
            snapshot = dict(reservations)
            key = (
                agent_id,
                candidate.id,
                tuple(sorted((aid, cand.id) for aid, cand in reservations.items() if aid != agent_id)),
            )
            if key in visits:
                diagnostics.reject("visited_state")
                continue
            visits.add(key)
            deps = blocking_conflicts(agent_id, candidate, my_priority)
            higher = [dep for dep in deps if priority(dep.blocker) >= my_priority]
            lower = [dep for dep in deps if dep not in higher]
            if higher:
                diagnostics.reject("higher_priority_conflict")
                continue
            if not lower:
                reservations[agent_id] = candidate
                return True
            if not config.enable_inheritance:
                diagnostics.reject("inheritance_disabled")
                continue
            cleared = True
            for dep in lower:
                diagnostics.dependency_log.append(dep)
                reservations.pop(dep.blocker, None)
                if not reserve(dep.blocker, dep, my_priority):
                    cleared = False
                    break
            if cleared and not blocking_conflicts(agent_id, candidate, my_priority):
                reservations[agent_id] = candidate
                return True
            diagnostics.backtrack_count += 1
            if not config.enable_backtracking:
                return False
            reservations.clear()
            reservations.update(snapshot)
        return False

    roots = sorted(states, key=lambda aid: (-priority(aid), aid))
    for root in roots:
        if root not in reservations and not reserve(root, None, None):
            diagnostics.fallback_trigger_count += 1
            fallback = Candidate(
                id=f"{root}:fallback_hold",
                agent_id=root,
                start=states[root].vertex,
                end=states[root].vertex,
                t0=0.0,
                t1=config.tick,
                score=999.0,
                provenance="fallback_hold",
            )
            if not blocking_conflicts(root, fallback, priority(root)):
                reservations[root] = fallback
            else:
                diagnostics.deadlock = True

    progressed = {
        aid
        for aid, candidate in reservations.items()
        if _goal_distance(roadmap, candidate.end, goals[aid])
        < _goal_distance(roadmap, states[aid].vertex, goals[aid])
    }
    diagnostics.time_to_progress = {
        aid: 0 if aid in progressed else states[aid].progress_debt + 1 for aid in states
    }
    diagnostics.deadlock = diagnostics.deadlock or not progressed
    diagnostics.livelock = any(debt >= 3 for debt in diagnostics.time_to_progress.values())
    diagnostics.dependency_scc_size = _largest_component_size(diagnostics.dependency_log)
    diagnostics.no_progress_certificate = any(
        not roadmap.on_clearance_cycle(states[aid].vertex, goals[aid]) for aid in states if aid not in progressed
    )

    for left_id, left in reservations.items():
        for right_id, right in reservations.items():
            if left_id >= right_id:
                continue
            has_conflict, _, _, clearance = conflict_between(left, right, states, roadmap, config)
            diagnostics.min_clearance = min(diagnostics.min_clearance, clearance)
            diagnostics.collisions += int(has_conflict)
    diagnostics.step_time_ms = (perf_counter() - started) * 1000.0
    return reservations, diagnostics


def _largest_component_size(dependencies: list[Dependency]) -> int:
    graph: dict[AgentId, set[AgentId]] = {}
    for dep in dependencies:
        graph.setdefault(dep.requester, set()).add(dep.blocker)
        graph.setdefault(dep.blocker, set()).add(dep.requester)
    largest = 0
    seen: set[AgentId] = set()
    for node in graph:
        if node in seen:
            continue
        stack = [node]
        size = 0
        seen.add(node)
        while stack:
            cur = stack.pop()
            size += 1
            for nxt in graph[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        largest = max(largest, size)
    return largest
