---
title: Roadmap Disk CSD-PIBT Restricted Spec
created: 2026-04-13
last_researched: 2026-04-13
tags: [roadmap, disk-agents, prototype, safety-invariant, progress-condition]
sources: [S01, S05, S07, S09]
---

# Roadmap Disk CSD-PIBT Restricted Spec

This note defines the first executable slice of the CSD-PIBT proposal: 2D disk
agents on a clearance-valid roadmap. It is a proof harness, not a full robotics
stack.

## Model

An `Agent` has an id, disk radius, current roadmap vertex, goal vertex, priority
age, and progress debt. The prototype treats each tick as a single-integrator
roadmap motion over straight vertex-to-vertex segments.

A `Candidate` is a finite roadmap primitive with:

- requester agent id
- start and endpoint roadmap vertices
- closed time window `[t0, t1]`
- swept disk capsule induced by the roadmap segment and radius
- scalar score for deterministic ordering
- provenance such as `wait`, `traverse`, `delayed_traverse`, `speed_scaled`,
  `continue_previous`, `inherited_clear`, or `fallback_hold`

A `Dependency` records a conflict-induced request from one candidate to another
agent:

- requester and blocker ids
- requester candidate id
- blocker candidate or current hold id
- conflict interval
- representative conflict geometry
- relation: `avoid`, `vacate_by`, or `retime`

## Candidate Bank

Every tick builds a finite deterministic bank:

- previous safe-prefix continuation when applicable
- wait or hold
- nominal neighbor traversal toward the goal
- delayed traversal
- speed-scaled traversal
- inherited clearing candidate biased away from the inherited conflict geometry

The ablation flags remove inheritance, backtracking, retiming candidates, or
priority aging without changing the surrounding API.

## Safety Invariant

The shield commits only dynamically feasible roadmap candidates whose swept
disk capsules have no sampled time-overlap conflict under a fixed clearance
margin against all already committed reservations and non-reserved current
safety envelopes.

For this v1 harness, "dynamically feasible" means the candidate either waits at
the current vertex or traverses an adjacent roadmap edge inside its declared
time window. Collision checks are conservative sampled disk-distance checks
over the overlapping time interval.

## Progress Condition

The restricted progress certificate is intentionally local:

> A highest-priority agent may progress when its requested local adjacency lies
> on a clearance cycle and the candidate bank contains wait, traverse, retiming,
> and inherited clearing maneuvers for that cycle.

If a blocker is already at its goal and there is no local clearance cycle, v1
keeps that blocker sticky and reports progress debt rather than inventing an
unsafe or globally unjustified clearing motion.

## Diagnostics

The prototype reports collisions, minimum sampled clearance, deadlock/livelock
flags, time-to-progress debt, backtrack count, dependency component size,
candidate rejection reasons, fallback trigger count, per-agent candidate counts,
dependency logs, no-progress-certificate status, and per-step runtime.
