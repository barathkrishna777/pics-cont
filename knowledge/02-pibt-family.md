---
title: PIBT Family Notes
created: 2026-04-13
last_researched: 2026-04-13
tags: [PIBT, CS-PIBT, EPIBT, MD-PIBT, priority-inheritance, backtracking]
sources: [S01, S02, S03, S04, S05]
---

# PIBT Family Notes

## Why PIBT Works So Well in Grid MAPF

PIBT is effective because it turns conflict resolution into a local dependency protocol:

- Unique dynamic priorities break symmetry.
- A high-priority agent can temporarily transfer priority to a lower-priority blocker.
- The blocker attempts to move while preserving the inherited priority chain.
- If the blocker cannot find a valid move, failure is backtracked and the upstream agent tries another candidate.
- Priority ages with time since goal/progress and resets after reaching the goal, so the highest-priority role rotates (`S01`).

The finite-time reachability theorem is tied to topology. In PIBT, if every adjacent pair of graph nodes belongs to a simple cycle of length at least 3, then the highest-priority agent can make progress and all agents reach their destinations within a bounded number of timesteps after assignment (`S01`). This should be treated as a proof pattern, not as a fact that automatically survives in continuous space.

## Transfer Principle

For continuous space, do not map "priority inheritance" to "a lower-priority agent just gets a higher scalar priority". Map it to:

> The blocker receives a temporary constraint-conditioned subproblem: find a safe short-horizon candidate that clears the high-priority agent's requested swept volume/time interval, or return failure so the parent can backtrack.

This turns priority inheritance into constrained resampling, retiming, or local replanning.

## CS-PIBT Lessons

CS-PIBT uses PIBT as a smart collision shield for learned local policies (`S02`). The critical insight is that a shield should use the full action distribution, not only the argmax action. Naive shields that freeze agents on conflict can create deadlocks. CS-PIBT instead converts each agent's action distribution into an ordering, then lets PIBT search alternatives.

Continuous-space implication:

- A policy/sampler should output a ranked candidate set, not a single command.
- Candidate ordering can be deterministic or sampled without replacement from a biased distribution.
- "Wait" or "brake" should be a candidate, but should not be the only conflict resolution.
- The shield should be evaluated against a greedy nominal policy plus a strong collision shield (`S03`), not only against unshielded policies.

## EPIBT Lessons

EPIBT adds multi-action operations to address action models where one discrete move is too weak, such as rotation actions or delayed actions (`S04`). It also uses revisiting and operation inheritance to preserve speed while supporting richer short-horizon behavior.

Continuous-space implication:

- One control tick is often too small to clear a swept-volume conflict.
- Candidate actions should include short macro-actions: brake-then-turn, sidestep arc, wait-then-go, reverse-then-turn, micro-loop, or time-scaled segment.
- Operation inheritance can be adapted as "reuse the previous safe short-horizon trajectory prefix unless it conflicts with new inherited constraints."

## MD-PIBT Lessons

MD-PIBT reframes PIBT and EPIBT as planning over agent dependencies (`S05`). This is a direct hint for continuous space because one continuous candidate can conflict with multiple agents or multiple time intervals. Instead of forcing PIBT's one-conflict-at-a-time rule, maintain a dependency set:

```text
Dependency {
  requester_agent
  blocker_agent
  requested_candidate_id
  conflict_interval
  conflict_geometry
  inherited_priority_token
  required_relation: avoid | vacate | retime | yield | coupled-plan
}
```

Continuous-space implication:

- Use a dependency graph rather than a single recursive call stack when candidates create multiple conflicts.
- Backtracking can search over dependency subsets or priorities, not just over agent actions.
- If dependency graph width grows beyond the real-time budget, escalate the connected component to local coupled planning.

## What to Borrow

- Dynamic unique priorities with progress aging and reset (`S01`).
- Recursive blocker resolution and backtracking (`S01`).
- Full candidate distribution/order, not just selected command (`S02`).
- Multi-action operations for richer dynamics (`S04`).
- Dependency graph representation for multi-conflict candidates (`S05`).

## What Not to Assume

- Do not assume discrete node occupancy.
- Do not assume a one-step move can always clear a conflict.
- Do not assume all conflicts are vertex or edge conflicts.
- Do not assume liveness from safety.
- Do not assume local reactive methods solve bottlenecks without a topology/progress condition.

## LLM Retrieval Cues

If asked "how to make PIBT continuous", retrieve:

- "priority inheritance as constraint-conditioned resampling"
- "candidate = swept volume over time"
- "backtracking over candidate choices"
- "liveness requires continuous analog of graph cycle condition"
- "use MD-PIBT dependency graph when conflicts are not one-to-one"

