---
title: Continuous-Space Dependency PIBT Blueprint
created: 2026-04-13
last_researched: 2026-04-13
tags: [algorithm-sketch, continuous-space-dependency-pibt, priority-inheritance, backtracking, implementation]
sources: [S01, S02, S04, S05, S06, S07, S08, S09, S10, S13, S14, S15, S16]
---

# Continuous-Space Dependency PIBT Blueprint

Working name: Continuous-Space Dependency PIBT, or `CSD-PIBT`.

## Goal

Design a real-time collision shield that accepts nominal actions for continuous-space agents and outputs a safe short-horizon control prefix. It should retain PIBT's practical strengths: local reasoning, priority inheritance, backtracking, adaptive priorities, and bounded per-tick computation (`S01`). It should replace grid-specific occupancy with swept-volume/time constraints from continuous-time MAPF (`S07`) and candidate generation from sampling-based or safety-filtered methods (`S10`, `S13`, `S14`).

## State

```text
AgentRuntime {
  id
  state
  goal
  priority_age
  epsilon_tie_breaker
  progress_debt
  previous_safe_candidate
  nominal_input
}

Candidate {
  id
  agent_id
  trajectory
  control_prefix
  time_window
  swept_volume
  endpoint_state
  score
  provenance
  constraints_satisfied
}

Dependency {
  requester
  blocker
  requester_candidate
  blocker_candidate_or_current_state
  conflict_interval
  conflict_geometry
  inherited_priority
  relation
}
```

## Priority Rule

Use a PIBT-like priority:

```text
priority_i = priority_age_i + epsilon_i + boost_i
```

- `priority_age_i`: grows while the agent lacks meaningful progress.
- `epsilon_i`: unique stable tie-breaker.
- `boost_i`: temporary inherited priority token inside the current recursive dependency search.

Reset or reduce `priority_age_i` when the agent reaches a goal, enters a target region, or makes a certified progress step. The exact "progress" definition must be domain-specific; for roadmap tasks it can be distance-to-goal reduction, and for kinodynamic tasks it can be advancement along a global reference trajectory.

## Main Cycle

```text
CSD_PIBT_step(agents, nominal_inputs, constraints, world):
    for each agent:
        candidates[agent] = sample_candidates(agent, nominal_inputs, constraints)

    reservations = empty
    dependency_log = empty

    for root in agents sorted by descending priority:
        if root not in reservations:
            ok = reserve_agent(root, inherited_context=None)
            if not ok:
                fallback_or_safe_stop(root)

    return first_controls(reservations), diagnostics
```

## Recursive Reservation

```text
reserve_agent(i, inherited_context):
    ordered = ordered_candidates(i, inherited_context)
    for c_i in ordered:
        if violates_static_or_hard_constraints(c_i):
            continue

        conflicts = conflicts_with_reservations_and_current_states(c_i)
        lower_conflicts = conflicts where blocker priority < inherited_priority_of_i
        higher_conflicts = conflicts where blocker priority >= inherited_priority_of_i

        if higher_conflicts:
            continue

        if lower_conflicts is empty:
            commit(i, c_i)
            return true

        snapshot = save(reservations, dependency_log)
        all_cleared = true

        for dep in choose_dependency_order(lower_conflicts):
            j = dep.blocker
            context_j = make_inherited_context(dep, priority_of_i)
            uncommit_if_needed(j)
            if not reserve_agent(j, context_j):
                all_cleared = false
                break

        if all_cleared and c_i still conflict_free_with(reservations):
            commit(i, c_i)
            return true

        restore(snapshot)

    return false
```

This is a blueprint, not final pseudocode. Two implementation details matter:

- If one candidate conflicts with multiple lower-priority agents, use MD-PIBT-style dependency reasoning (`S05`) rather than assuming a single blocker.
- If a lower-priority agent is already committed, uncommitting it must trigger revalidation of downstream dependencies.

## Conflict Detection

At minimum:

```text
conflict(c_i, c_j):
    return exists t in overlap(c_i.time_window, c_j.time_window)
           such that distance(swept_shape_i(t), swept_shape_j(t)) < margin
```

For efficiency:

- Broad phase: bounding boxes/capsules over candidate intervals.
- Narrow phase: exact collision checker or conservative swept-volume check.
- Interval extraction: return conflict interval, not just boolean.
- Robustness: inflate shapes and pad time windows for delay/tracking error (`S09`).

## Candidate Sampling

Every agent should have a mixed bank:

- previous safe prefix continuation
- nominal policy/control action
- goal-directed action
- wait/brake
- retiming variants
- lateral or tangent detours
- inherited clearing maneuvers
- ORCA/CBF-projected control
- short kinodynamic samples

For inherited blockers, change the score so clearing the inherited conflict geometry matters more than self-progress. This is the key continuous-space translation of priority inheritance.

## Safety Invariant

Commit rule:

> A candidate can be committed only if it is dynamically feasible, satisfies static constraints, and has no unhandled hard conflict with all already committed reservations plus non-reserved agents' current safety envelopes.

This produces a per-cycle safety invariant if the final executed prefix is short enough for replanning and the collision model includes tracking/sensing margins. If the safety filter modifies a committed control, re-run conflict checks on the modified trajectory.

## Liveness Proof Sketch

The proof should be staged. Do not attempt to prove full continuous liveness first.

Stage 1: Termination per shield cycle.

- Candidate sets are finite.
- Recursive calls either commit an agent, remove a candidate from consideration, or backtrack.
- Dependency recursion is bounded by number of agents times candidate count, with visited-state guards.

Stage 2: Safety.

- All committed candidates pass a conservative collision predicate.
- Execution uses only the prefix covered by the reservation and margin model.

Stage 3: Progress under local topology assumption.

Hypothesis to prove or falsify:

> In a clearance-valid roadmap or cell decomposition where every local adjacency used by a highest-priority agent lies on a cycle with sufficient clearance, and where candidate sets include a complete-enough clearing maneuver basis for that cycle, the highest-priority agent can make bounded progress after finite backtracking.

This mirrors PIBT's graph-cycle condition (`S01`) but adds clearance, dynamics, and sampling coverage assumptions.

Stage 4: Probabilistic progress under sampling.

If candidate sets are sampled rather than exhaustive, the claim becomes probabilistic:

> Given nonzero probability of sampling a valid clearing maneuver whenever one exists, repeated attempts with priority aging and fallback produce progress with probability approaching 1 within bounded escalation windows.

Tie this to K-CBS or RRT-style probabilistic completeness only if the fallback actually uses a planner with such guarantees (`S10`).

## Fallback Ladder

1. Try more candidates for inherited blockers.
2. Widen horizon for the dependency component.
3. Switch to safe retiming and safe intervals.
4. Run local K-CBS or coupled RRT/dRRT on the dependency component.
5. Run small-cluster NMPC for nonholonomic dynamics.
6. Request a global replan or traffic-management intervention.
7. If no motion is safe, execute safe stop and increase progress debt.

## Diagnostics to Log

- number of candidates per agent
- number of conflicts detected
- number of dependency edges
- backtracking depth
- dependency component sizes
- conflict interval widths
- safety margin minima
- progress debt before/after
- fallback level used
- repeated-conflict pair counts
- false-blocking suspicion: conservative broad phase rejects but narrow phase would pass

## Minimal Experiment

Implement first on disk agents in 2D continuous space with double-integrator or single-integrator dynamics:

- Environments: open swap, narrow corridor, ring/cycle, four-way crossing, warehouse-like aisles, cul-de-sac.
- Baselines: naive freeze shield, ORCA, greedy sampler plus CBF, grid PIBT on a roadmap, local CBS/K-CBS fallback.
- Metrics: collision rate, deadlock rate, throughput, average delay, min clearance, compute time, fallback rate.
- Ablations: no inheritance, no backtracking, no priority aging, no retiming candidates, no clearing candidates, no fallback.

## Important Negative Result to Remember

Safety filters alone are not enough. ORCA and CBFs are excellent local safety tools, but deadlock/livelock is a planning and symmetry problem (`S13`, `S15`). The point of a PIBT-like shield is to add dynamic asymmetry and structured backtracking on top of continuous safety.

