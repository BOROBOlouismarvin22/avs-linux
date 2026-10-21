from avs.diagnostics.process_diagnostic import (
    diagnose_process,
    diagnose_processes,
)
from avs.system.process_probe import ProcessResult


def make_process(
    pid=1000,
    name="test.exe",
    cpu=10.0,
    memory=100.0,
):
    return ProcessResult(
        pid=pid,
        name=name,
        cpu_percent=cpu,
        memory_mb=memory,
    )


def test_process_normal():
    process = make_process(
        cpu=10.0,
        memory=100.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "NORMAL"


def test_process_high_ram():
    process = make_process(
        cpu=10.0,
        memory=600.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "ÉLEVÉ"


def test_process_high_ram_at_threshold():
    process = make_process(
        cpu=10.0,
        memory=500.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "ÉLEVÉ"


def test_process_high_cpu():
    process = make_process(
        cpu=60.0,
        memory=100.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "ÉLEVÉ"


def test_process_high_cpu_at_threshold():
    process = make_process(
        cpu=50.0,
        memory=100.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "ÉLEVÉ"


def test_process_critical():
    process = make_process(
        cpu=80.0,
        memory=700.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "CRITIQUE"


def test_process_ram_only_recommendation():
    process = make_process(
        cpu=10.0,
        memory=600.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "ÉLEVÉ"
    assert "mémoire RAM" in result["message"]


def test_process_cpu_only_message():
    process = make_process(
        cpu=70.0,
        memory=100.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "ÉLEVÉ"
    assert "processeur" in result["message"]


def test_process_critical_message():
    process = make_process(
        cpu=70.0,
        memory=700.0,
    )

    result = diagnose_process(process)

    assert result["status"] == "CRITIQUE"
    assert "RAM" in result["message"]
    assert "CPU" in result["message"]


def test_multiple_processes():
    processes = [
        make_process(
            pid=1,
            name="normal.exe",
            cpu=10.0,
            memory=100.0,
        ),
        make_process(
            pid=2,
            name="ram.exe",
            cpu=10.0,
            memory=600.0,
        ),
        make_process(
            pid=3,
            name="cpu.exe",
            cpu=60.0,
            memory=100.0,
        ),
    ]

    results = diagnose_processes(processes)

    assert len(results) == 3
    assert results[0]["status"] == "NORMAL"
    assert results[1]["status"] == "ÉLEVÉ"
    assert results[2]["status"] == "ÉLEVÉ"


def test_realistic_process_case():
    process = make_process(
        pid=17140,
        name="Code.exe",
        cpu=0.0,
        memory=298.50,
    )

    result = diagnose_process(process)

    assert result["pid"] == 17140
    assert result["name"] == "Code.exe"
    assert result["memory_mb"] == 298.50
    assert result["cpu_percent"] == 0.0
    assert result["status"] == "NORMAL"