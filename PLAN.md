# Roadmap-Disk CSD-PIBT Proof + Prototype Plan

## Summary
Build the first restricted version around **2D disk agents on a clearance-valid roadmap**. The goal is to make the proposal real by pairing a small formal model with a minimal executable prototype that tests whether priority inheritance as constraint-conditioned retiming/clearing actually reduces deadlock versus simpler shields.

## Key Changes
- Add a concise formal spec note defining:
  - Agent: disk radius, roadmap vertex/edge state, goal, priority age, progress debt.
  - Candidate: finite roadmap motion primitive with `[t0, t1]`, swept capsule, endpoint, score, and provenance.
  - Dependency: requester, blocker, candidate, conflict interval, conflict geometry, and relation: `avoid`, `vacate_by`, or `retime`.
  - Safety invariant: commit only dynamically feasible candidates with no swept-volume conflict under fixed clearance margin.
  - Progress condition: highest-priority agent can progress if its local adjacency lies on a clearance cycle and the candidate bank includes wait, traverse, and clearing/retiming maneuvers for that cycle.
- Add a minimal Python prototype rather than a full robotics stack:
  - `shield_step(states, goals, roadmap, previous_reservations) -> controls, diagnostics`
  - finite candidate bank: continue previous safe prefix, nominal edge traversal, wait/hold, delayed traversal, speed-scaled traversal, and inherited clearing candidate.
  - recursive reservation/backtracking over candidates, with dependency graph logging and visited-state bounds.
  - exact-enough disk-on-segment swept collision checks using conservative capsule/time-overlap checks for v1.
- Add diagnostics required to evaluate the claim:
  - collisions, min clearance, deadlock/livelock, time-to-progress, backtrack count, dependency SCC size, candidate rejection reasons, fallback trigger count, and p95/p99 step time.
- Keep out of scope for v1:
  - free-space arbitrary splines, ORCA/CBF/NMPC, differential-drive dynamics, K-CBS fallback, and probabilistic sampling liveness.

## Test Plan
- Unit tests:
  - candidate finiteness and deterministic ordering.
  - swept-capsule conflict detection for same-edge, crossing-edge, and delayed traversal.
  - recursion terminates with bounded candidates and visited-state guards.
  - committed reservations are pairwise collision-free.
- Scenario tests:
  - two-agent swap on a cycle succeeds.
  - head-on corridor without a side cycle safely stalls and reports no progress certificate.
  - three-agent ring rotation progresses with priority aging.
  - four-way crossing resolves without collision.
  - cul-de-sac goal blocker fails gracefully and records progress debt.
- Ablations:
  - no inheritance.
  - inheritance without backtracking.
  - no retiming candidates.
  - no priority aging.
  - freeze-on-conflict baseline.

## Assumptions
- Use Python for the prototype because the repo is currently notes-only and no existing implementation stack is present.
- Use a roadmap/cell-decomposition model first, not continuous free-space disks.
- Treat v1 as a **research prototype and proof harness**, not a deployable collision shield.
- The first publishable target is: per-cycle termination + modeled safety + restricted highest-priority progress on clearance-cycle roadmap instances, backed by ablations showing fewer deadlocks than freeze, greedy priority, and no-retiming variants.
