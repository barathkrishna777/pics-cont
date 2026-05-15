---
title: Local Avoidance and Safety Filters
created: 2026-04-13
last_researched: 2026-04-13
tags: [ORCA, RVO, velocity-obstacles, CBF, barrier-certificates, NMPC, deadlock]
sources: [S13, S14, S15, S16]
---

# Local Avoidance and Safety Filters

## ORCA and RVO

RVO and ORCA are fast decentralized velocity-space collision avoidance methods (`S13`). ORCA constructs pairwise half-plane-like velocity constraints and selects a velocity through a low-dimensional linear program. It is attractive for a collision shield because it is fast, local, and has strong pairwise safety intuition.

Good uses:

- Generate safe candidate velocities.
- Provide a final "least change" projection from nominal velocity into a safe set.
- Produce baseline local-avoidance behavior.
- Provide fallback behavior when no sampled candidate is safe and braking is possible.

Bad use:

- Do not treat ORCA as a liveness guarantee. It is reactive and can be trapped by bottlenecks, symmetry, or global-goal conflicts.

## Control Barrier Functions

CBF/barrier-certificate methods (`S14`) formulate safety as an optimization problem:

```text
minimize ||u - u_nominal||
subject to safety inequalities for each relevant pair/obstacle
```

This is useful as a control-level guard after a candidate trajectory has been selected. It can also generate candidate controls by projecting nominal controls into the safe set.

Risks:

- Pairwise CBF constraints can become infeasible.
- Conservative constraints can freeze agents.
- Reactive CBF controllers can deadlock, especially in symmetric arrangements (`S15`).
- CBF safety does not imply task progress.

## Deadlock Evidence

Deadlock analysis work (`S15`) is important because it rules out a tempting but insufficient design: "just make every agent safe with a CBF and let goals pull them forward." Symmetry and reciprocal constraints can make zero-progress equilibria stable. PIBT's dynamic priorities and backtracking are precisely the kind of asymmetry and search that a pure reactive controller lacks.

## NMPC

Nonlinear MPC for multiple nonholonomic robots (`S16`) can include collision constraints, goal progress, and dynamics in one finite-horizon optimization. It is not likely to scale as a per-tick shield for thousands of agents, but it is a strong fallback for small coupled clusters:

- Use when dependency graph component size <= small threshold.
- Use when dynamics are nonholonomic and candidate sampling repeatedly fails.
- Use as a local proof-of-concept for deadlock-free maneuvers.

## Recommended Composition

Use local avoidance and safety filters as layers:

1. Candidate generator: ORCA/CBF/MPC proposes velocities or controls.
2. Dependency resolver: continuous-space PIBT chooses and backtracks over candidates.
3. Safety checker: swept-volume or robust collision checking rejects unsafe reservations.
4. Control guard: CBF or tracking MPC enforces safety during execution.
5. Escalation: K-CBS, local coupled sampling, or NMPC if the dependency resolver cannot find progress.

## Retrieval Cues

- "ORCA is a fast local sampler/filter, not a MAPF solver."
- "CBF safety can deadlock; add priority asymmetry and backtracking."
- "Use NMPC for small clusters, not as the global shield."

