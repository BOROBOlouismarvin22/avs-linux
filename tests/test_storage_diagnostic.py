from avs.system.storage_probe import StorageResult
from avs.diagnostics.storage_diagnostic import analyze_storage


def test_stockage_normal():
    result = StorageResult(
        drive="C:\\",
        total_gb=500,
        used_gb=200,
        free_gb=300,
        usage_percent=40,
    )

    diagnostic = analyze_storage(result)

    assert diagnostic.status == "OK"


def test_stockage_attention():
    result = StorageResult(
        drive="C:\\",
        total_gb=500,
        used_gb=425,
        free_gb=75,
        usage_percent=85,
    )

    diagnostic = analyze_storage(result)

    assert diagnostic.status == "WARNING"


def test_stockage_critique():
    result = StorageResult(
        drive="C:\\",
        total_gb=500,
        used_gb=475,
        free_gb=25,
        usage_percent=95,
    )

    diagnostic = analyze_storage(result)

    assert diagnostic.status == "CRITICAL"