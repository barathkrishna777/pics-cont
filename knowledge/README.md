---
title: Continuous-Space PIBT-Style Collision Shield Knowledge Base
created: 2026-04-13
last_researched: 2026-04-13
audience: LLM agents and researchers designing collision shields for continuous-space MAPF
---

# Continuous-Space PIBT-Style Collision Shield Knowledge Base

This folder is a compact, source-grounded knowledge base for designing a PIBT-like collision shield in continuous space. It is organized for retrieval by LLMs: each note has YAML frontmatter, stable source IDs, tags, takeaways, design implications, and explicit "open questions" rather than long paper summaries.

## Start Here

1. Read `06-design-blueprint.md` for a concrete continuous-space priority inheritance and backtracking shield design.
2. Read `02-pibt-family.md` to understand what should transfer from PIBT, CS-PIBT, EPIBT, and MD-PIBT.
3. Read `03-continuous-time-mapf.md` for continuous-time constraints, unsafe intervals, and robust-delay ideas.
4. Read `05-sampling-candidate-actions.md` for candidate action generation strategies.
5. Use `sources.md` as the source index; every claim in the synthesis points back to source IDs such as `S01`, `S05`, or `S08`.
6. Read `08-roadmap-disk-spec.md` for the first restricted formal model and proof-harness contract.

## Core Synthesis

The likely useful abstraction is not "run PIBT on continuous controls". It is:

> Treat each agent's short-horizon trajectory or control sequence as a candidate resource claim over swept volume and time. Use PIBT-style priority inheritance to recursively ask lower-priority blockers to resample or retime under added constraints. Use backtracking to reject local choices when those induced constraints cannot be satisfied. Preserve safety by committing only candidates that pass continuous collision checks or a formal safety filter.

For liveness, a continuous-space version needs more than pairwise collision avoidance. It needs a progress certificate analogous to PIBT's graph-cycle condition: a local topology or sampled candidate set must guarantee that the currently highest-priority agent can eventually obtain a feasible clearing maneuver, or the shield must escalate to horizon widening, local coupled planning, K-CBS, or a meta-agent fallback.

## Retrieval Map

- `01-problem-frame.md`: vocabulary, assumptions, safety vs liveness, data model.
- `02-pibt-family.md`: PIBT, CS-PIBT, EPIBT, MD-PIBT, and transfer principles.
- `03-continuous-time-mapf.md`: SIPP, CCBS, robust continuous-time MAPF, unsafe intervals, constraint representation.
- `04-local-avoidance-safety-filters.md`: ORCA, velocity obstacles, CBF/barrier certificates, NMPC, deadlock caveats.
- `05-sampling-candidate-actions.md`: action samplers, ranking, constraint conditioning, diversity, escalation.
- `06-design-blueprint.md`: a concrete algorithm sketch for Continuous-Space Dependency PIBT.
- `07-research-agenda.md`: experiments, proof obligations, and failure modes.
- `08-roadmap-disk-spec.md`: restricted roadmap-disk model implemented by the Python prototype.
- `manifest.yml`: machine-readable inventory.
- `sources.md`: source cards and stable IDs.

## Design North Star

Use PIBT's mechanism as the conflict-resolution policy, not as the geometry engine. Use continuous-time MAPF and motion-planning work for geometry, safety, and constraints. Use sampling-based planning for action generation. Use safety filters such as ORCA or CBFs as fast candidate generators or final guards, but do not rely on them alone for liveness in congested cases.
