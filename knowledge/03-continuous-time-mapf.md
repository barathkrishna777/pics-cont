---
title: Continuous-Time MAPF Constraint Notes
created: 2026-04-13
last_researched: 2026-04-13
tags: [continuous-time, CCBS, SIPP, unsafe-intervals, constraints, robust-mapf]
sources: [S06, S07, S08, S09, S17]
---

# Continuous-Time MAPF Constraint Notes

## What Continuous-Time MAPF Contributes

Continuous-time MAPF work gives the geometry and time language that PIBT lacks. CCBS (`S07`) adapts CBS with a SIPP-like low-level search so it can represent non-uniform action durations, agent volume, roadmaps, and continuous waiting. It resolves conflicts by imposing constraints over action-time pairs and unsafe intervals, rather than by forbidding discrete vertex/edge conflicts.

For a shield, this suggests that every candidate should expose:

- time interval: `[t_start, t_end]`
- swept volume or collision checker handle
- optional safe intervals for start/end states
- dynamic feasibility metadata
- conflict intervals against other candidates or current occupancies

## Safe Intervals

SIPP (`S06`) plans with states of the form `(configuration, safe interval)`. For a collision shield, use safe intervals as compact memory:

- "Agent i can enter region/cell/roadmap vertex v during [a, b]."
- "Agent i can execute motion primitive m from time tau if tau lies outside these unsafe intervals."
- "Wait is safe only within a safe interval, not universally."

This is especially useful for retiming candidates. If a straight trajectory conflicts, the shield can try:

- delayed execution within the next safe interval
- speed scaling
- wait-then-go
- brake to a safe hold point

## Unsafe Intervals

CCBS uses unsafe intervals to describe times at which one action conflicts with another. In continuous geometry, computing exact unsafe intervals can be nontrivial and model-specific (`S07`). Conservative over-approximations are acceptable for a shield if they preserve safety, but they can harm liveness by falsely eliminating clearing maneuvers.

Implementation rule:

```text
unsafe_interval(candidate_i, candidate_j, margin):
    return conservative time intervals where swept_volume_i(t) intersects swept_volume_j(t) inflated by margin
```

Keep both the exact/conservative flag and the margin in diagnostics. Liveness experiments should distinguish true deadlocks from conservative false negatives.

## CCBS Warning

Recent work (`S08`) argues that CCBS-style algorithms need careful branching rules for soundness and termination; reference implementations can be suboptimal or non-terminating on some examples. For this shield:

- Do not claim optimality from using CCBS-like constraints.
- If using unsafe interval branching, record which branch rule is used.
- Treat aggressive pruning as a performance heuristic unless proved safe.
- Prefer a conservative safety invariant with a separate empirical liveness claim.

## Robustness to Delay and Tracking Error

Robust continuous-time MAPF (`S09`) models bounded delays with T-robust plans. For a physical collision shield, include a tracking margin:

```text
effective_shape_i(t) =
    nominal_shape_i(t)
    inflated_by(position_error_bound + delay_error_bound * max_speed + sensing_latency_bound)
```

This can be implemented with:

- geometry inflation
- time padding around unsafe intervals
- delay-aware collision checking
- robust safe intervals for hold points

The price is conservativeness. Use adaptive margins when possible: larger for high-speed or poorly tracked agents, smaller for slow or well-controlled agents.

## Constraint Record for a Shield

Recommended minimal structure:

```text
Constraint {
  owner_agent
  forbidden_agent
  time_window: [t0, t1]
  geometry_ref: swept_volume | capsule | convex_region | roadmap_edge
  relation: avoid | yield | vacate_by | do_not_start_in_interval | must_arrive_in_interval
  margin
  source_dependency_id
  hardness: hard | soft
}
```

Hard constraints preserve safety. Soft constraints encode liveness preferences such as "clear this corridor if possible".

## Design Implications

- A continuous PIBT-like shield should commit reservations, not just endpoint states.
- Backtracking should remove or replace reservations and recompute conflicts.
- Priority inheritance should propagate constraints describing what must be cleared.
- Safe waiting should be checked, not assumed.
- Conservative unsafe intervals are useful for safety but dangerous for liveness; track false-blocking rates.

