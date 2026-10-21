from avs.diagnostics.cause_analyzer import analyze_causes


def make_ram(status="OK", capacity="BONNE"):
    return {
        "usage_status": status,
        "capacity_status": capacity,
    }


def make_cpu(status="NORMALE"):
    return {
        "usage_status": status,
    }


def make_disk(usage="OK", free="CORRECT"):
    return {
        "usage_status": usage,
        "free_space_status": free,
    }


def make_process(
    name="test.exe",
    memory=100.0,
    cpu=10.0,
    status="NORMAL",
):
    return {
        "pid": 1000,
        "name": name,
        "memory_mb": memory,
        "cpu_percent": cpu,
        "status": status,
    }


def test_system_normal():
    result = analyze_causes(
        make_ram(),
        make_cpu(),
        make_disk(),
        [],
    )

    assert result["status"] == "NORMAL"
    assert result["priority"] == "FAIBLE"
    assert result["causes"] == []


def test_ram_problem():
    result = analyze_causes(
        make_ram("ÉLEVÉ", "BONNE"),
        make_cpu(),
        make_disk(),
        [],
    )

    assert result["status"] == "PROBLÈME DÉTECTÉ"
    assert "Forte sollicitation de la mémoire RAM." in result["causes"]


def test_ram_capacity_problem():
    result = analyze_causes(
        make_ram("OK", "TRÈS LIMITÉE"),
        make_cpu(),
        make_disk(),
        [],
    )

    assert result["status"] == "PROBLÈME DÉTECTÉ"
    assert "Capacité RAM limitée." in result["causes"]


def test_cpu_problem():
    result = analyze_causes(
        make_ram(),
        make_cpu("ÉLEVÉE"),
        make_disk(),
        [],
    )

    assert result["status"] == "PROBLÈME DÉTECTÉ"
    assert "Forte sollicitation du processeur." in result["causes"]


def test_disk_problem():
    result = analyze_causes(
        make_ram(),
        make_cpu(),
        make_disk("CRITIQUE", "CORRECT"),
        [],
    )

    assert result["status"] == "PROBLÈME DÉTECTÉ"
    assert (
        "Espace de stockage insuffisant ou fortement utilisé."
        in result["causes"]
    )


def test_ram_and_cpu_problem():
    result = analyze_causes(
        make_ram("ÉLEVÉ", "BONNE"),
        make_cpu("ÉLEVÉE"),
        make_disk(),
        [],
    )

    assert result["priority"] == "HAUTE"
    assert (
        "La RAM et le CPU sont fortement sollicités simultanément."
        in result["causes"]
    )


def test_high_ram_process():
    process = make_process(
        name="Code.exe",
        memory=700.0,
        cpu=10.0,
        status="ÉLEVÉ",
    )

    result = analyze_causes(
        make_ram(),
        make_cpu(),
        make_disk(),
        [process],
    )

    assert (
        "Un ou plusieurs processus consomment beaucoup de mémoire RAM."
        in result["causes"]
    )


def test_high_cpu_process():
    process = make_process(
        name="test.exe",
        memory=100.0,
        cpu=70.0,
        status="ÉLEVÉ",
    )

    result = analyze_causes(
        make_ram(),
        make_cpu(),
        make_disk(),
        [process],
    )

    assert (
        "Un ou plusieurs processus sollicitent fortement le CPU."
        in result["causes"]
    )


def test_process_evidence():
    process = make_process(
        name="Code.exe",
        memory=800.0,
        cpu=60.0,
        status="CRITIQUE",
    )

    result = analyze_causes(
        make_ram(),
        make_cpu(),
        make_disk(),
        [process],
    )

    assert any(
        "Code.exe" in item
        for item in result["evidence"]
    )


def test_recommendations_are_present():
    result = analyze_causes(
        make_ram("ÉLEVÉ", "TRÈS LIMITÉE"),
        make_cpu("ÉLEVÉE"),
        make_disk(),
        [],
    )

    assert len(result["recommendations"]) > 0


def test_realistic_user_case():
    processes = [
        make_process(
            name="Code.exe",
            memory=298.50,
            cpu=0.0,
            status="NORMAL",
        ),
        make_process(
            name="firefox.exe",
            memory=130.04,
            cpu=0.0,
            status="NORMAL",
        ),
    ]

    result = analyze_causes(
        make_ram("ÉLEVÉ", "TRÈS LIMITÉE"),
        make_cpu("ÉLEVÉE"),
        make_disk("OK", "CORRECT"),
        processes,
    )

    assert result["status"] == "PROBLÈME DÉTECTÉ"
    assert result["priority"] == "HAUTE"
    assert len(result["causes"]) >= 3
    assert len(result["recommendations"]) >= 3