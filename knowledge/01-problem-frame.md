---
title: Problem Frame for a Continuous-Space Collision Shield
created: 2026-04-13
last_researched: 2026-04-13
tags: [continuous-space-mapf, collision-shield, safety, liveness, interfaces]
sources: [S01, S02, S05, S06, S07, S09, S10, S12, S13, S14, S15, S16, S17]
---

# Problem Frame

## Working Definition

A continuous-space MAPF collision shield is a fast online module that transforms each agent's nominal next action into a jointly safe set of short-horizon trajectories or controls. The nominal action source can be a learned policy, a global planner, ORCA, an MPC controller, a roadmap action, or a sampler.

For this project, the shield should be PIBT-like: it should not merely freeze colliding agents. It should use priority inheritance and backtracking to recursively move or retime lower-priority blockers, while preserving explicit safety constraints and a credible route to liveness.

## Core Objects

Use these as a common vocabulary across implementation and theory:

- Agent state: current pose, velocity, dynamic mode, radius/shape, goal, nominal control, priority age.
- Candidate: a short-horizon trajectory or control sequence with start time, duration, swept volume, endpoint, progress score, and provenance.
- Constraint: a condition that invalidates candidates, usually over time and swept geometry. Example: "agent i cannot occupy swept region R during [t0, t1]" or "agent i must vacate blocker j's requested corridor by time t_clear".
- Reservation: a committed candidate for an agent in the current shield cycle.
- Dependency: "candidate c_i for agent i conflicts with current or candidate occupancy of agent j." Dependencies should be directed and annotated with conflict time, conflict geometry, and priority token.
- Backtracking state: a finite stack of candidate choices and inherited constraints, used to recover when a push chain fails.

## Safety vs Liveness

Safety means the shield only commits trajectories that are collision-free under the modeled geometry, time, and tracking error assumptions. Sources `S07`, `S09`, `S13`, and `S14` suggest several ways to encode this:

- Exact or conservative swept-volume collision checks.
- Continuous-time unsafe intervals, as in CCBS.
- Delay-robust intervals or inflated geometry, as in robust continuous-time MAPF.
- A control barrier function or ORCA-style velocity-space safety filter.

Liveness means all agents eventually make task progress. PIBT's liveness result is not "priority magic"; it relies on a structural graph condition and a priority aging/reset rule (`S01`). A continuous-space analog needs an equivalent progress condition. Plausible forms:

- A roadmap/cover condition: each local adjacency in the roadmap lies on a cycle with clearance larger than agent diameter plus tracking margin.
- A clearing-maneuver condition: for any local dependency chain, at least one lower-priority agent has a feasible candidate that clears the requested swept volume without creating an unresolved higher-priority conflict.
- An escalation condition: if local candidates cannot certify progress, a bounded neighborhood is handed to a complete/probabilistically complete fallback such as local CBS/K-CBS or coupled sampling (`S10`, `S12`).

## Continuous-Space Complications

The discrete PIBT "node" becomes a region or swept volume over time. This creates design choices:

- Space representation: roadmap vertices/edges, convex cells, velocity commands, splines, or kinodynamic trajectories.
- Time representation: fixed control tick, variable-duration actions, safe intervals, or event times.
- Collision predicate: disks, convex bodies, differential-drive footprints, uncertainty-inflated footprints, or arbitrary collision checker.
- Candidate finiteness: backtracking requires finite candidate sets per cycle, even if the underlying control space is continuous. Sampling should produce a bounded, ranked list with diversity guarantees.
- Constraint propagation: inherited priority should impose constraints on the blocker, not just boost its scalar priority. In continuous space, the blocker must know what swept region or time interval it is being asked to clear.

## Minimum Useful Interface

```text
shield_step(states, nominal_inputs, global_hints, previous_reservations):
    candidate_sets = sample_candidates(states, nominal_inputs, global_hints)
    reservations = resolve_with_dependency_pibt(candidate_sets, states)
    safe_reservations = safety_filter(reservations, states)
    return first_controls(safe_reservations), diagnostics
```

Diagnostics should include unresolved dependency cycles, number of backtracks, fallback invocations, minimum clearance, number of candidate samples per agent, and progress debt per agent.

## Design Constraints to Preserve

- Preserve explicit safety: never rely on priority to "probably" avoid collisions.
- Preserve finite local search: each shield cycle must terminate within a real-time budget.
- Preserve asymmetry: unique priorities or deterministic/sampled tie-breaking are essential for avoiding symmetric deadlocks (`S01`, `S15`).
- Preserve progress debt: priority should increase with time since last meaningful progress and reset when progress is made (`S01`).
- Preserve fallback path: when local inheritance fails, escalate rather than freezing forever (`S05`, `S10`, `S16`).
