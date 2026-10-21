from avs.decision.action_engine import decide_action


def test_system_normal():
    ram = {
        "usage_status": "OK",
    }

    cpu = {
        "usage_status": "NORMALE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = []

    causes = {
        "priority": "NORMALE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert result["status"] == "SURVEILLANCE"
    assert result["priority"] == "NORMALE"


def test_ram_problem():
    ram = {
        "usage_status": "ÉLEVÉ",
    }

    cpu = {
        "usage_status": "NORMALE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = []

    causes = {
        "priority": "HAUTE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert result["status"] == "ACTION REQUISE"
    assert result["priority"] == "HAUTE"


def test_cpu_problem():
    ram = {
        "usage_status": "OK",
    }

    cpu = {
        "usage_status": "ÉLEVÉE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = []

    causes = {
        "priority": "HAUTE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert result["status"] == "ACTION REQUISE"


def test_cpu_critical():
    ram = {
        "usage_status": "OK",
    }

    cpu = {
        "usage_status": "CRITIQUE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = []

    causes = {
        "priority": "CRITIQUE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert result["priority"] == "HAUTE"


def test_disk_problem():
    ram = {
        "usage_status": "OK",
    }

    cpu = {
        "usage_status": "NORMALE",
    }

    disk = {
        "usage_status": "ÉLEVÉ",
    }

    processes = []

    causes = {
        "priority": "MOYENNE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert len(result["actions"]) >= 1


def test_ram_and_cpu_problem():
    ram = {
        "usage_status": "ÉLEVÉ",
    }

    cpu = {
        "usage_status": "ÉLEVÉE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = []

    causes = {
        "priority": "HAUTE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert len(result["actions"]) == 2
    assert result["priority"] == "HAUTE"


def test_process_problem():
    ram = {
        "usage_status": "OK",
    }

    cpu = {
        "usage_status": "NORMALE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = [
        {
            "name": "Code.exe",
            "status": "CRITIQUE",
        }
    ]

    causes = {
        "priority": "HAUTE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert result["priority"] == "HAUTE"


def test_no_action_uses_default():
    ram = {
        "usage_status": "OK",
    }

    cpu = {
        "usage_status": "NORMALE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = []

    causes = {
        "priority": "NORMALE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert len(result["actions"]) == 1
    assert result["actions"][0]["type"] == "SYSTEME"


def test_high_priority_action_is_first():
    ram = {
        "usage_status": "ÉLEVÉ",
    }

    cpu = {
        "usage_status": "NORMALE",
    }

    disk = {
        "usage_status": "ÉLEVÉ",
    }

    processes = []

    causes = {
        "priority": "HAUTE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert result["actions"][0]["priority"] == "HAUTE"


def test_realistic_avs_case():
    ram = {
        "usage_status": "ÉLEVÉ",
    }

    cpu = {
        "usage_status": "CRITIQUE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = [
        {
            "name": "Code.exe",
            "status": "NORMAL",
        }
    ]

    causes = {
        "priority": "HAUTE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    assert result["status"] == "ACTION REQUISE"
    assert result["priority"] == "HAUTE"
    assert len(result["actions"]) >= 2