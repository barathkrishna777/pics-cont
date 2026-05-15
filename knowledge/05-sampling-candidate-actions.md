---
title: Sampling Candidate Actions for a Continuous-Space PIBT-Like Shield
created: 2026-04-13
last_researched: 2026-04-13
tags: [sampling, candidate-actions, RRT, K-CBS, retiming, velocity-sampling, diversity]
sources: [S02, S04, S05, S06, S07, S10, S11, S12, S13, S14, S16]
---

# Sampling Candidate Actions

## Candidate Requirements

Each agent needs a finite, ranked candidate set per shield cycle. Each candidate must be cheap to compare and safe to reject:

```text
Candidate {
  id
  agent_id
  trajectory_or_control_sequence
  start_time
  horizon
  swept_volume_ref
  endpoint_state
  progress_score
  comfort_or_energy_cost
  clearance_score
  provenance
  hard_constraints_satisfied
}
```

Backtracking terminates only if candidate sets are finite. Continuous controls should be sampled into a bounded list.

## Candidate Sources

Use a mixture, not one sampler:

- Nominal candidate: the action proposed by the policy/global planner/controller.
- Goal-progress candidates: controls that reduce distance-to-goal or follow a global path.
- Stop/brake candidates: dynamically feasible stop, controlled wait, or hold-at-safe-point.
- Retiming candidates: wait-then-go, speed-scale, delay within safe interval (`S06`, `S07`).
- Lateral/escape candidates: sidestep, tangent arc around blocker, local detour through adjacent free space.
- Priority-clearing candidates: maneuvers that clear another agent's requested swept volume, even if they do not maximize own progress.
- ORCA/CBF-projected candidates: project nominal velocity into a safe velocity/control set (`S13`, `S14`).
- Roadmap candidates: follow one of several nearby roadmap edges with timing.
- Tree-search candidates: short RRT/KPIECE branches for difficult dynamics (`S10`).
- Coupled-cluster candidates: local dRRT or K-CBS fallback for unresolved dependency components (`S10`, `S12`).

## Ranking

Candidate order should depend on both self progress and social effect:

```text
score =
  w_goal * progress
  - w_safety * risk_margin_penalty
  - w_control * control_effort
  - w_delay * delay
  + w_clear * clears_inherited_dependency
  - w_block * blocks_high_priority_corridor
  + w_random * tie_break_noise
```

For CS-PIBT-like behavior (`S02`), convert candidate probabilities into a strict ordering. Biased sampling without replacement is useful to avoid repeatedly choosing the same locally attractive action.

## Constraint Conditioning Under Priority Inheritance

When agent `i` wants candidate `c_i` and it conflicts with lower-priority agent `j`, inheritance should generate a new candidate set for `j` conditioned on the dependency:

```text
resample(j, inherited_context):
    avoid c_i's conflict geometry during [t0, t1]
    prefer clearing the requested corridor by t_clear
    keep hard obstacle/dynamics constraints
    preserve j's own goal progress as a secondary objective
```

This is the continuous analog of a blocker "moving out of the way".

## Diversity

Candidate sets should not collapse to tiny variations of the same velocity. Include diversity across:

- timing: now, delayed, slowed, stopped
- geometry: left, right, reverse, hold, through bottleneck
- dynamics: low acceleration, high clearance, short-horizon aggressive
- dependency role: self-progress, clear blocker, yield, retreat

Use diagnostics:

```text
diversity = count(distinct topological side classes) + count(distinct arrival intervals)
```

If diversity is low during repeated failures, widen the sampler or escalate.

## Real-Time Budget Strategy

Suggested per-agent candidate budget:

- Normal state: 5 to 15 candidates.
- Inherited-priority blocker: 10 to 30 candidates focused on clearing.
- Repeated local failure: widen horizon and candidate budget for the dependency component.
- Budget exhausted: fall back to a conservative safe stop if safety allows, and mark progress debt.

## Escalation Triggers

Escalate when any of these occur:

- Dependency graph has a strongly connected component above a threshold.
- Same agents backtrack together for multiple ticks.
- Conservative collision intervals eliminate all clearing candidates.
- Safety filter rejects every moving candidate for the highest-priority agent.
- Progress debt grows beyond threshold.

Escalation options:

- Run local K-CBS with sampling-based low-level planner (`S10`).
- Run local dRRT over individual roadmaps (`S12`).
- Run NMPC for a small nonholonomic cluster (`S16`).
- Ask global planner for a new corridor or traffic rule.
