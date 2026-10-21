from avs.diagnostics.cpu_diagnostic import diagnose_cpu


def test_cpu_usage_faible():
    result = diagnose_cpu(30, 4)
    assert result["usage_status"] == "FAIBLE"


def test_cpu_usage_normale():
    result = diagnose_cpu(60, 4)
    assert result["usage_status"] == "NORMALE"


def test_cpu_usage_elevee():
    result = diagnose_cpu(75, 4)
    assert result["usage_status"] == "ÉLEVÉE"


def test_cpu_usage_tres_elevee():
    result = diagnose_cpu(90, 4)
    assert result["usage_status"] == "TRÈS ÉLEVÉE"


def test_cpu_usage_critique():
    result = diagnose_cpu(100, 4)
    assert result["usage_status"] == "CRITIQUE"


def test_cpu_processors_limites():
    result = diagnose_cpu(50, 2)
    assert result["processor_status"] == "LIMITÉ"


def test_cpu_processors_corrects():
    result = diagnose_cpu(50, 4)
    assert result["processor_status"] == "CORRECT"


def test_cpu_processors_bons():
    result = diagnose_cpu(50, 8)
    assert result["processor_status"] == "BON"


def test_cpu_recommendation_high_usage():
    result = diagnose_cpu(90, 4)

    assert "Identifier les applications" in result["recommendation"]


def test_cpu_recommendation_critical_usage():
    result = diagnose_cpu(100, 4)

    assert "Identifier les applications" in result["recommendation"]


def test_cpu_realistic_case():
    result = diagnose_cpu(100, 4)

    assert result["usage_status"] == "CRITIQUE"
    assert result["processor_status"] == "CORRECT"