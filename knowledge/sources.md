---
title: Source Cards
created: 2026-04-13
last_researched: 2026-04-13
tags: [sources, bibliography, claim-index]
---

# Source Cards

Use these IDs in notes and code comments. The "Use For" field says how the source should inform a continuous-space PIBT-like shield.

## S01 - PIBT Original and Journal Version

- Title: Priority Inheritance with Backtracking for Iterative Multi-agent Path Finding
- Authors: Keisuke Okumura, Manao Machida, Xavier Defago, Yasumasa Tamura
- Venues: IJCAI 2019; Artificial Intelligence 2022
- Links:
  - https://www.ijcai.org/proceedings/2019/0076.pdf
  - https://kei18.github.io/pibt2/
  - https://doi.org/10.1016/j.artint.2022.103752
- Key Claims: PIBT assigns unique dynamic priorities each timestep; priority inheritance handles priority inversion; backtracking prevents local push chains from getting stuck. The finite-time reachability theorem depends on graph topology: every adjacent pair must belong to a simple cycle of length at least 3, including biconnected undirected graphs.
- Use For: Mechanism template; liveness proof shape; priority aging and reset; local dependency recursion; bounded one-step computation.
- Caveat: Discrete graph, short horizon, and exact graph topology assumptions do not directly apply to continuous geometry.

## S02 - CS-PIBT for Collision Shielding Learned Policies

- Title: Improving Learnt Local MAPF Policies with Heuristic Search
- Authors: Rishi Veerapaneni, Qian Wang, Kevin Ren, Arthur Jakobsson, Jiaoyang Li, Maxim Likhachev
- Venue: ICAPS 2024
- Links:
  - https://arxiv.org/abs/2403.20300
  - https://openreview.net/forum?id=6JEBeiztNT
  - https://doi.org/10.1609/icaps.v34i1.31522
- Key Claims: A PIBT-based collision shield can post-process a local policy's action distribution, using the full action distribution rather than only the argmax action. CS-PIBT returns collision-free one-step actions in grid MAPF and outperforms naive shields that freeze colliding agents.
- Use For: Shield interface pattern: nominal policy/sampler proposes ordered actions, PIBT resolves collisions. Also useful for biased sampling from a distribution instead of strict probability ordering.
- Caveat: Still grid/discrete; one-step shield alone does not provide full-horizon completeness.

## S03 - CS-PIBT as a Strong Baseline for ML MAPF

- Title: Work Smarter Not Harder: Simple Imitation Learning with CS-PIBT Outperforms Large Scale Imitation Learning for MAPF
- Authors: Rishi Veerapaneni, Arthur Jakobsson, Kevin Ren, Samuel Kim, Jiaoyang Li, Maxim Likhachev
- Venue: ICRA 2025
- Links:
  - https://arxiv.org/abs/2409.14491
  - https://arthurjakobsson.github.io/ssil_mapf/
- Key Claims: Smart one-step collision shields such as CS-PIBT can dominate complex learned local policies in MAPF. Future learned policies should compare against greedy policies plus a strong collision shield.
- Use For: Evaluation baseline discipline and warning that candidate generation and collision shielding should be separately ablated.
- Caveat: Again grid MAPF; use for evaluation philosophy, not continuous proofs.

## S04 - EPIBT and Multi-Action Operations

- Title: Enhancing PIBT via Multi-Action Operations
- Authors: Egor Yukhnevich, Anton Andreychuk
- Link: https://arxiv.org/abs/2511.09193
- Key Claims: Short-horizon PIBT struggles with action models that include rotation or delays. EPIBT introduces bounded multi-action operations, revisiting, and operation inheritance to support richer action models while preserving speed.
- Use For: Evidence that continuous/kinodynamic shields likely need multi-step candidate operations, not only instantaneous moves.
- Caveat: Still MAPF-like; check exact accepted version before citing in a paper.

## S05 - MD-PIBT

- Title: Planning over MAPF Agent Dependencies via Multi-Dependency PIBT
- Authors: Zixiang Jiang, Yulun Zhang, Rishi Veerapaneni, Jiaoyang Li
- Link: https://arxiv.org/abs/2603.23405
- Key Claims: PIBT and EPIBT can be viewed through agent dependencies; MD-PIBT generalizes them by searching over dependencies. Reported experiments include up to 10,000 homogeneous agents under kinodynamic constraints such as rotation motion and differential-drive robots with speed and acceleration limits.
- Use For: Direct conceptual bridge from priority inheritance to dependency search; especially relevant for continuous candidate collision shields where one candidate can conflict with multiple agents.
- Caveat: Very recent as of 2026-04-13; read full paper before adopting parameterizations.

## S06 - SIPP

- Title: SIPP: Safe Interval Path Planning for Dynamic Environments
- Authors: Mike Phillips, Maxim Likhachev
- Venue: ICRA 2011
- Link: https://www.cs.cmu.edu/~maxim/files/sipp_icra11.pdf
- Key Claims: A safe interval is a contiguous collision-free time interval at a configuration; planning over `(configuration, safe interval)` can keep time continuous-ish without enumerating every timestep and can preserve optimality/completeness under assumptions.
- Use For: Low-level single-agent planning under dynamic constraints; candidate retiming; representing time windows compactly.
- Caveat: Assumes wait capability and particular dynamic-obstacle representation; kinodynamic constraints may require variants.

## S07 - CCBS and Continuous-Time MAPF

- Title: Multi-Agent Pathfinding with Continuous Time
- Authors: Anton Andreychuk, Konstantin Yakovlev, Dor Atzmon, Roni Stern
- Venues: IJCAI 2019; Artificial Intelligence 2022
- Links:
  - https://www.ijcai.org/proceedings/2019/0006.pdf
  - https://doi.org/10.1016/j.artint.2022.103662
- Key Claims: CCBS combines CBS with a SIPP-like low-level search to handle continuous time, non-uniform action durations, roadmaps, and agents with volume. It reasons with conflicts, constraints, and unsafe intervals rather than discrete vertex/edge conflicts.
- Use For: Constraint representation; swept-volume conflict detection; unsafe interval computation; roadmaps in continuous time.
- Caveat: Exact unsafe interval computation is geometry-dependent and can be expensive; later work questions some termination/soundness details of reference implementations.

## S08 - CCBS Soundness/Termination Critique and Delta Branching

- Title: Optimal Multi-agent Path Finding in Continuous Time
- Authors: Alvin Combrink, Sabino Francesco Roselli, Martin Fabian
- Link: https://arxiv.org/html/2508.16410v2
- Key Claims: Theoretical CCBS-style algorithms need conditions for soundness and solution completeness; reference CCBS can be suboptimal or non-terminating in counterexamples. The paper proposes a delta branching rule to restore guarantees.
- Use For: Warning: do not blindly copy CCBS constraints for proof claims. Useful checklist for continuous-time branching and pruning.
- Caveat: Recent work; verify final journal/version when available.

## S09 - Robust MAPF with Continuous Time

- Title: Robust Multi-Agent Pathfinding with Continuous Time
- Authors: Wen Jun Tan, Xueyan Tang, Wentong Cai
- Venue: ICAPS 2024
- Link: https://openreview.net/forum?id=AIwAtZzM3v
- Key Claims: Defines T-robust MAPF in continuous time, where plans remain collision-free under bounded delays. Provides exact collision detection among delayed agents and claims complete, optimal solutions.
- Use For: Robustness margins for shield execution; delay-aware unsafe intervals; safety buffers for tracking error.
- Caveat: Exact robustness may be too costly for a fast local shield; use as a gold-standard reference.

## S10 - K-CBS

- Title: Conflict-based Search for Multi-Robot Motion Planning with Kinodynamic Constraints
- Authors: Justin Kottinger, Shaull Almagor, Morteza Lahijanian
- Venue: IROS 2022
- Links:
  - https://arxiv.org/abs/2207.00576
  - https://justinkottinger.com/projects/K-CBS/
  - https://doi.org/10.1109/IROS47612.2022.9982018
- Key Claims: K-CBS adapts CBS to continuous multi-robot motion planning with kinodynamic constraints. The low-level planner can be any sampling-based tree planner such as RRT or KPIECE, and K-CBS inherits probabilistic completeness from that planner; it adds merge-and-restart for repeated conflicts.
- Use For: Escalation fallback when local priority inheritance cannot find feasible candidates; sampling-based low-level interface.
- Caveat: More expensive than a shield; use selectively for small conflict neighborhoods.

## S11 - Representation-Optimal MAMP with CBS

- Title: Representation-Optimal Multi-Robot Motion Planning using Conflict-Based Search
- Authors: Juan Irving Solis Vidana, James Motes, Read Sandstrom, Nancy M. Amato
- Link: https://arxiv.org/abs/1909.13352
- Additional links:
  - https://experts.illinois.edu/en/publications/representation-optimal-multi-robot-motion-planning-using-conflict
  - https://doi.org/10.1109/LRA.2021.3068910
- Key Claims: CBS ideas can be adapted from MAPF to heterogeneous continuous-space multi-agent motion planning without assuming a shared discrete representation. Demonstrated teams up to 32 agents and high-DOF manipulators.
- Use For: Evidence for continuous-space CBS-style conflict decomposition and heterogeneous agent handling.
- Caveat: Offline planner, not a local real-time shield.

## S12 - dRRT

- Title: Finding a needle in an exponential haystack: Discrete RRT for exploration of implicit roadmaps in multi-robot motion planning
- Authors: Kiril Solovey, Oren Salzman, Dan Halperin
- Link: https://arxiv.org/abs/1305.2889
- Key Claims: dRRT explores an implicit tensor product of individual roadmaps using an RRT-like graph-search process, avoiding explicit construction of the full composite roadmap.
- Use For: Sampling-based coupled fallback; local implicit product search for multi-agent conflict clusters.
- Caveat: Not a shield by itself; needs integration with local constraints and runtime budgets.

## S13 - RVO and ORCA

- Titles:
  - Reciprocal Velocity Obstacles for Real-Time Multi-Agent Navigation
  - Optimal Reciprocal Collision Avoidance
- Authors: Jur van den Berg, Ming Lin, Dinesh Manocha; later ORCA work with Stephen Guy and others
- Links:
  - https://gamma.cs.unc.edu/RVO/icra2008.pdf
  - http://gamma-web.iacs.umd.edu/ORCA/
- Key Claims: RVO/ORCA are decentralized velocity-space collision avoidance methods. ORCA gives sufficient pairwise conditions for collision-free motion and solves a low-dimensional linear program per agent.
- Use For: Fast candidate velocity generation, final safety filter, and baseline local avoidance.
- Caveat: Reactive collision avoidance can deadlock or fail liveness in congested/topologically constrained scenarios; do not treat ORCA as a MAPF solver.

## S14 - Safety Barrier Certificates / CBFs

- Titles:
  - Control Barrier Certificates for Safe Swarm Behavior
  - Safety Barrier Certificates for Collisions-Free Multirobot Systems
- Authors: Urs Borrmann, Li Wang, Aaron D. Ames, Magnus Egerstedt; Li Wang, Aaron D. Ames, Magnus Egerstedt
- Links:
  - https://www.sciencedirect.com/science/article/pii/S240589631502412X
  - https://authors.library.caltech.edu/records/tshzw-g4v69
  - https://doi.org/10.1109/TRO.2017.2659727
- Key Claims: Barrier certificates formulate safe control as an optimization problem that minimally modifies nominal controls while enforcing forward invariance of a safe set. Later work addresses decentralization, conservativeness, solution existence, and deadlock avoidance.
- Use For: Last-mile safety filter and control-level enforcement under dynamics.
- Caveat: Safety guarantees alone are not liveness guarantees; reactive CBFs can deadlock without symmetry-breaking or planning.

## S15 - CBF Deadlock Analysis

- Titles:
  - Why Does Symmetry Cause Deadlocks?
  - The Before, During, and After of Multi-robot Deadlock
- Authors: Jaskaran Grover, Changliu Liu, Katia Sycara and related collaborators
- Links:
  - https://www.sciencedirect.com/science/article/pii/S2405896320334042
  - https://doi.org/10.1177/02783649221074718
- Key Claims: Reactive CBF-based multi-robot collision avoidance can deadlock; symmetry in initial positions and goals can make deadlock stable.
- Use For: Negative result for liveness; motivates priority asymmetry, backtracking, horizon widening, and explicit progress tests.
- Caveat: Analyze applicability to your specific dynamics and nominal controller.

## S16 - Deadlock-Free NMPC

- Title: Nonlinear MPC for collision-free and deadlock-free navigation of multiple nonholonomic mobile robots
- Authors: Amir Salimi Lafmejani, Spring Berman
- Link: https://doi.org/10.1016/j.robot.2021.103774
- Key Claims: Online nonlinear MPC can incorporate collision constraints for nonholonomic wheeled robots and provide feasibility/stability proofs; experiments include up to six robots.
- Use For: Local coupled optimizer fallback and proof ideas around finite-horizon feasibility.
- Caveat: Optimization cost and scalability may limit direct use as a shield for many agents.

## S17 - MAPF Definitions and Benchmarks

- Title: Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks
- Authors: R. Stern et al.
- Link: https://mapf.info/index.php/Main.SKoen19k
- Key Claims: MAPF papers differ in conflict definitions, objectives, and assumptions; the position paper provides unifying terminology and benchmark pointers.
- Use For: Keep terminology precise when defining continuous-space collision shield variants.
- Caveat: Mostly classical MAPF framing; extend carefully to continuous geometry and controls.
