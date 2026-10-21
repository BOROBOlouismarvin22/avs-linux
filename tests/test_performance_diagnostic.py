from avs.diagnostics.performance_diagnostic import diagnose_ram


def test_ram_usage_ok():
    result = diagnose_ram(8.0, 4.0, 69)
    assert result["usage_status"] == "OK"


def test_ram_usage_attention():
    result = diagnose_ram(8.0, 5.6, 70)
    assert result["usage_status"] == "ATTENTION"


def test_ram_usage_attention_at_85():
    result = diagnose_ram(8.0, 6.8, 85)
    assert result["usage_status"] == "ATTENTION"


def test_ram_usage_eleve():
    result = diagnose_ram(8.0, 6.88, 86)
    assert result["usage_status"] == "ÉLEVÉ"


def test_ram_usage_eleve_at_95():
    result = diagnose_ram(8.0, 7.6, 95)
    assert result["usage_status"] == "ÉLEVÉ"


def test_ram_usage_critique():
    result = diagnose_ram(8.0, 7.68, 96)
    assert result["usage_status"] == "CRITIQUE"


def test_ram_capacity_very_limited():
    result = diagnose_ram(3.81, 3.52, 92)
    assert result["capacity_status"] == "TRÈS LIMITÉE"


def test_ram_capacity_limited():
    result = diagnose_ram(4.5, 3.5, 78)
    assert result["capacity_status"] == "LIMITÉE"


def test_ram_capacity_good():
    result = diagnose_ram(8.0, 4.0, 50)
    assert result["capacity_status"] == "BONNE"


def test_ram_recommendation_when_usage_is_high():
    result = diagnose_ram(8.0, 7.2, 90)
    assert "Fermer les applications inutilisées" in result["recommendation"]


def test_realistic_user_case():
    result = diagnose_ram(3.81, 3.52, 92)

    assert result["usage_status"] == "ÉLEVÉ"
    assert result["capacity_status"] == "TRÈS LIMITÉE"