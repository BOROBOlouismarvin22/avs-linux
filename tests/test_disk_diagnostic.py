from avs.diagnostics.disk_diagnostic import diagnose_disk


def test_disk_usage_ok():
    result = diagnose_disk(500, 200, 300, 40)
    assert result["usage_status"] == "OK"


def test_disk_usage_attention():
    result = diagnose_disk(500, 375, 125, 75)
    assert result["usage_status"] == "ATTENTION"


def test_disk_usage_eleve():
    result = diagnose_disk(500, 450, 50, 90)
    assert result["usage_status"] == "ÉLEVÉ"


def test_disk_usage_critique():
    result = diagnose_disk(500, 480, 20, 96)
    assert result["usage_status"] == "CRITIQUE"


def test_disk_free_space_very_low():
    result = diagnose_disk(500, 495, 5, 99)
    assert result["free_status"] == "TRÈS FAIBLE"


def test_disk_free_space_low():
    result = diagnose_disk(500, 480, 20, 96)
    assert result["free_status"] == "FAIBLE"


def test_disk_free_space_correct():
    result = diagnose_disk(500, 200, 300, 40)
    assert result["free_status"] == "CORRECT"


def test_disk_recommendation_critical():
    result = diagnose_disk(500, 480, 20, 96)

    assert "Libérer rapidement de l'espace disque" in result["recommendation"]


def test_disk_recommendation_low_space():
    result = diagnose_disk(500, 495, 5, 99)

    assert "Libérer rapidement de l'espace disque" in result["recommendation"]


def test_disk_recommendation_normal():
    result = diagnose_disk(500, 200, 300, 40)

    assert "Aucune action immédiate nécessaire" in result["recommendation"]


def test_disk_realistic_user_case():
    result = diagnose_disk(
        237.37,
        123.09,
        114.28,
        51.86,
    )

    assert result["usage_status"] == "OK"
    assert result["free_status"] == "CORRECT"