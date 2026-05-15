from csd_pibt import AgentState, Candidate, Roadmap, ShieldConfig, conflict_between, shield_step


def line_map():
    return Roadmap(
        vertices={"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (2.0, 0.0)},
        edges={"a": ("b",), "b": ("a", "c"), "c": ("b",)},
    )


def square_map():
    return Roadmap(
        vertices={
            "a": (0.0, 0.0),
            "b": (1.0, 0.0),
            "c": (1.0, 1.0),
            "d": (0.0, 1.0),
            "x": (0.5, 0.5),
        },
        edges={
            "a": ("b", "d", "x"),
            "b": ("a", "c", "x"),
            "c": ("b", "d", "x"),
            "d": ("a", "c", "x"),
            "x": ("a", "b", "c", "d"),
        },
    )


def test_candidate_ordering_is_finite_and_deterministic():
    roadmap = square_map()
    states = {"a0": AgentState("a"), "a1": AgentState("c")}
    goals = {"a0": "c", "a1": "a"}
    first, diag_first = shield_step(states, goals, roadmap)
    second, diag_second = shield_step(states, goals, roadmap)
    assert [first[k].id for k in sorted(first)] == [second[k].id for k in sorted(second)]
    assert diag_first.candidate_count == diag_second.candidate_count
    assert all(count < 20 for count in diag_first.candidate_count.values())


def test_swept_conflict_same_edge_and_delayed_traversal():
    roadmap = line_map()
    states = {"a0": AgentState("a", radius=0.2), "a1": AgentState("b", radius=0.2)}
    c0 = Candidate("a0:go", "a0", "a", "b", 0.0, 1.0, 0.0, "traverse")
    c1 = Candidate("a1:go", "a1", "b", "a", 0.0, 1.0, 0.0, "traverse")
    delayed = Candidate("a1:delay", "a1", "b", "a", 1.1, 2.1, 0.0, "delayed")
    assert conflict_between(c0, c1, states, roadmap)[0]
    assert not conflict_between(c0, delayed, states, roadmap)[0]


def test_swept_conflict_crossing_edge():
    roadmap = Roadmap(
        vertices={"n": (0, 1), "s": (0, -1), "e": (1, 0), "w": (-1, 0)},
        edges={"n": ("s",), "s": ("n",), "e": ("w",), "w": ("e",)},
    )
    states = {"a0": AgentState("n", radius=0.1), "a1": AgentState("w", radius=0.1)}
    c0 = Candidate("a0:go", "a0", "n", "s", 0.0, 1.0, 0.0, "traverse")
    c1 = Candidate("a1:go", "a1", "w", "e", 0.0, 1.0, 0.0, "traverse")
    assert conflict_between(c0, c1, states, roadmap, ShieldConfig(collision_samples=20))[0]


def test_recursion_terminates_with_visited_guard():
    roadmap = square_map()
    states = {
        "a0": AgentState("a", priority_age=3),
        "a1": AgentState("b", priority_age=2),
        "a2": AgentState("c", priority_age=1),
        "a3": AgentState("d", priority_age=0),
    }
    goals = {"a0": "c", "a1": "d", "a2": "a", "a3": "b"}
    reservations, diagnostics = shield_step(states, goals, roadmap, config=ShieldConfig(max_visits=200))
    assert set(reservations) == set(states)
    assert diagnostics.step_time_ms < 500


def test_committed_reservations_are_pairwise_collision_free():
    roadmap = square_map()
    states = {"a0": AgentState("a", priority_age=1), "a1": AgentState("c", priority_age=0)}
    goals = {"a0": "c", "a1": "a"}
    reservations, diagnostics = shield_step(states, goals, roadmap)
    assert set(reservations) == set(states)
    assert diagnostics.collisions == 0


def test_two_agent_swap_on_cycle_succeeds():
    roadmap = square_map()
    states = {"a0": AgentState("a", priority_age=1), "a1": AgentState("b", priority_age=0)}
    goals = {"a0": "b", "a1": "a"}
    reservations, diagnostics = shield_step(states, goals, roadmap)
    assert reservations["a0"].end == "b"
    assert reservations["a1"].end in {"c", "x", "d"}
    assert diagnostics.collisions == 0
    assert not diagnostics.no_progress_certificate


def test_head_on_corridor_without_side_cycle_safely_stalls():
    roadmap = Roadmap(
        vertices={"a": (0.0, 0.0), "b": (1.0, 0.0)},
        edges={"a": ("b",), "b": ("a",)},
    )
    states = {"a0": AgentState("a", priority_age=1), "a1": AgentState("b", priority_age=0)}
    goals = {"a0": "b", "a1": "a"}
    reservations, diagnostics = shield_step(states, goals, roadmap)
    assert diagnostics.collisions == 0
    assert diagnostics.no_progress_certificate
    assert reservations["a0"].end == "a" or reservations["a1"].end == "b"


def test_three_agent_ring_rotation_progresses_with_priority_aging():
    roadmap = Roadmap(
        vertices={"a": (0, 0), "b": (2, 0), "c": (2, 2), "d": (0, 2)},
        edges={"a": ("b", "d"), "b": ("a", "c"), "c": ("b", "d"), "d": ("a", "c")},
    )
    states = {
        "a0": AgentState("a", priority_age=2),
        "a1": AgentState("b", priority_age=1),
        "a2": AgentState("c", priority_age=0),
    }
    goals = {"a0": "b", "a1": "c", "a2": "d"}
    reservations, diagnostics = shield_step(states, goals, roadmap)
    assert diagnostics.collisions == 0
    assert any(reservations[aid].end == goals[aid] for aid in states)


def test_four_way_crossing_resolves_without_collision():
    roadmap = square_map()
    states = {
        "north": AgentState("c", priority_age=3),
        "south": AgentState("a", priority_age=2),
        "west": AgentState("d", priority_age=1),
        "east": AgentState("b", priority_age=0),
    }
    goals = {"north": "a", "south": "c", "west": "b", "east": "d"}
    _, diagnostics = shield_step(states, goals, roadmap, config=ShieldConfig(collision_samples=24))
    assert diagnostics.collisions == 0


def test_cul_de_sac_goal_blocker_fails_gracefully_records_progress_debt():
    roadmap = line_map()
    states = {
        "mover": AgentState("a", priority_age=1, progress_debt=2),
        "blocker": AgentState("b", priority_age=0, progress_debt=0),
    }
    goals = {"mover": "c", "blocker": "b"}
    reservations, diagnostics = shield_step(states, goals, roadmap)
    assert set(reservations).issubset(states)
    assert diagnostics.collisions == 0
    assert diagnostics.time_to_progress["mover"] >= 3
    assert diagnostics.no_progress_certificate


def test_ablation_flags_are_reported():
    roadmap = square_map()
    states = {"a0": AgentState("a", priority_age=1), "a1": AgentState("b", priority_age=0)}
    goals = {"a0": "b", "a1": "a"}
    _, diagnostics = shield_step(
        states,
        goals,
        roadmap,
        config=ShieldConfig(enable_inheritance=False, enable_retiming=False, enable_priority_aging=False),
    )
    assert "inheritance_disabled" in diagnostics.candidate_rejection_reasons or diagnostics.fallback_trigger_count
