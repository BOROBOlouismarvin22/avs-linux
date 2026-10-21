from avs.diagnostics.global_diagnostic import diagnose_system


def make_report(ram_status, cpu_status, disk_status):
    return {
        "ram": {
            "diagnostic": {
                "usage_status": ram_status
            }
        },
        "cpu": {
            "diagnostic": {
                "usage_status": cpu_status
            }
        },
        "disk": {
            "diagnostic": {
                "usage_status": disk_status
            }
        }
    }


def test_system_normal():
    report = make_report(
        "OK",
        "NORMALE",
        "OK"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "NORMAL"
    assert result["priority"] == "AUCUNE"


def test_ram_problem():
    report = make_report(
        "ÉLEVÉ",
        "NORMALE",
        "OK"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "ATTENTION"
    assert result["priority"] == "MOYENNE"
    assert "RAM" in result["problems"]


def test_cpu_problem():
    report = make_report(
        "OK",
        "ÉLEVÉE",
        "OK"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "ATTENTION"
    assert result["priority"] == "MOYENNE"
    assert "CPU" in result["problems"]


def test_disk_problem():
    report = make_report(
        "OK",
        "NORMALE",
        "ÉLEVÉ"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "ATTENTION"
    assert result["priority"] == "MOYENNE"
    assert "STOCKAGE" in result["problems"]


def test_ram_and_cpu_problem():
    report = make_report(
        "ÉLEVÉ",
        "ÉLEVÉE",
        "OK"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "ÉLEVÉ"
    assert result["priority"] == "HAUTE"

    assert "RAM" in result["problems"]
    assert "CPU" in result["problems"]


def test_ram_cpu_disk_problem():
    report = make_report(
        "CRITIQUE",
        "CRITIQUE",
        "CRITIQUE"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "ÉLEVÉ"
    assert result["priority"] == "HAUTE"

    assert "RAM" in result["problems"]
    assert "CPU" in result["problems"]
    assert "STOCKAGE" in result["problems"]


def test_ram_and_cpu_with_disk_ok():
    report = make_report(
        "CRITIQUE",
        "TRÈS ÉLEVÉE",
        "OK"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "ÉLEVÉ"
    assert result["priority"] == "HAUTE"

    assert "RAM" in result["problems"]
    assert "CPU" in result["problems"]


def test_only_disk_problem():
    report = make_report(
        "OK",
        "NORMALE",
        "CRITIQUE"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "ATTENTION"
    assert result["priority"] == "MOYENNE"


def test_no_problem():
    report = make_report(
        "OK",
        "FAIBLE",
        "OK"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "NORMAL"
    assert result["priority"] == "AUCUNE"


def test_global_recommendation_high_priority():
    report = make_report(
        "ÉLEVÉ",
        "ÉLEVÉE",
        "OK"
    )

    result = diagnose_system(report)

    assert result["priority"] == "HAUTE"
    assert "applications et processus" in result["recommendation"]


def test_realistic_user_case():
    report = make_report(
        "ÉLEVÉ",
        "ÉLEVÉE",
        "OK"
    )

    result = diagnose_system(report)

    assert result["global_status"] == "ÉLEVÉ"
    assert result["priority"] == "HAUTE"
    assert result["problems"] == ["RAM", "CPU"]