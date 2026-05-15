---
title: Research Agenda and Open Questions
created: 2026-04-13
last_researched: 2026-04-13
tags: [research-agenda, experiments, proof-obligations, failure-modes, benchmarks]
sources: [S01, S05, S07, S08, S09, S10, S13, S14, S15, S16, S17]
---

# Research Agenda and Open Questions

## Research Questions

1. What continuous topology condition can replace PIBT's graph-cycle condition?
2. What finite candidate basis is sufficient for clearing maneuvers in disk-agent 2D space?
3. How should inherited priority be encoded: as a scalar priority, a hard avoidance constraint, a soft clearing objective, or all three?
4. Can dependency-graph search from MD-PIBT be made real-time for continuous candidates with multi-agent conflicts?
5. When should the shield escalate to local coupled planning, and how small can that fallback neighborhood be?
6. How conservative can unsafe intervals or CBF margins be before liveness collapses?
7. Is there a useful probabilistic liveness theorem when candidates are sampled rather than enumerated?

## Proof Obligations

For a paper-quality algorithm, separate proof claims:

- Per-cycle termination: finite candidate sets and bounded backtracking.
- Safety: conservative collision checking and robust execution margins.
- Progress of highest-priority agent: only under explicit local topology and candidate-coverage assumptions.
- System liveness: priority aging/reset plus progress lemma, or fallback completeness.
- Probabilistic completeness: only if a sampling-based fallback with the right assumptions is actually invoked.

Do not claim CCBS-level optimality unless the algorithm really performs best-first search with sound continuous-time branching; `S08` is a warning here.

## Failure Modes to Test

- Symmetric swap in open space.
- Head-on corridor conflict.
- Three-agent rotation around a small obstacle.
- Four-agent cross intersection.
- Goal blockers in a cul-de-sac.
- Dense ring where everyone must rotate.
- Mixed-size agents where a large agent blocks a narrow passage.
- Differential-drive agents that must rotate before clearing.
- Tracking delay causing unsafe retiming.
- Conservative safety margins eliminating all clearing candidates.

## Baselines

Use at least these:

- Naive shield: freeze colliding candidates.
- ORCA/RVO local avoidance.
- CBF/QP projection of nominal controls.
- Greedy priority without inheritance.
- Priority inheritance without backtracking.
- CSD-PIBT without fallback.
- CSD-PIBT with local K-CBS or NMPC fallback.
- Roadmap/grid PIBT on a discretized version of the same instance.

## Metrics

- Hard safety: collisions, minimum separation, margin violations.
- Liveness: completed tasks, throughput, deadlocks, livelocks, time-to-progress.
- Search behavior: backtracks per tick, dependency graph size, fallback invocations.
- Real-time behavior: median/p95/p99 shield step time.
- Candidate behavior: rejection reasons, diversity, retiming usage, clearing candidate usage.
- Robustness: success under delay, tracking error, sensing noise.

## Implementation Milestones

1. Disk agents, single-integrator, fixed horizon, exact pairwise continuous collision check.
2. Add finite candidate bank with nominal, brake, retime, sidestep, and ORCA-projected candidates.
3. Add recursive priority inheritance/backtracking over candidate reservations.
4. Add dependency graph logging and repeated-conflict counters.
5. Add priority aging/reset and progress debt.
6. Add safe interval retiming for roadmap/cell candidates.
7. Add fallback to local K-CBS or small-cluster NMPC.
8. Add robust margins for bounded delay/tracking error.
9. Run ablation suite and failure-mode suite.
10. Attempt proof for a restricted roadmap-with-clearance setting.

## Notes for Future LLM Agents

When extending this knowledge base:

- Add new papers under the next available `SNN` ID in `sources.md`.
- Put implementation-specific design decisions in a new file, e.g. `08-implementation-decisions.md`.
- Keep source-grounded claims tagged with source IDs.
- If a paper is only used as inspiration, mark it as "inference" rather than direct support.
- Prefer small, retrievable chunks over long pasted abstracts.
