"""
storage_diagnostic.py

Couche diagnostic du module de stockage.

Ce module reçoit les données du stockage
et les transforme en diagnostic compréhensible.
"""

from dataclasses import dataclass

from avs.system.storage_probe import StorageResult


@dataclass
class StorageDiagnostic:
    """Résultat de l'analyse du stockage."""

    status: str
    message: str
    recommendation: str


def analyze_storage(result: StorageResult) -> StorageDiagnostic:
    """
    Analyse l'utilisation du stockage et produit un diagnostic.
    """

    usage = result.usage_percent

    if usage >= 90:
        return StorageDiagnostic(
            status="CRITICAL",
            message=(
                f"Le disque {result.drive} est presque plein. "
                f"{usage}% de l'espace est actuellement utilisé."
            ),
            recommendation=(
                "Libérez de l'espace rapidement en supprimant "
                "les fichiers inutiles ou en déplaçant certaines données."
            ),
        )

    if usage >= 80:
        return StorageDiagnostic(
            status="WARNING",
            message=(
                f"Le disque {result.drive} commence à être fortement utilisé. "
                f"{usage}% de l'espace est actuellement occupé."
            ),
            recommendation=(
                "Il est recommandé de surveiller l'espace disponible "
                "et de supprimer régulièrement les fichiers inutiles."
            ),
        )

    return StorageDiagnostic(
        status="OK",
        message=(
            f"L'espace disponible sur {result.drive} est suffisant. "
            f"{usage}% du stockage est actuellement utilisé."
        ),
        recommendation=(
            "Aucune action urgente n'est nécessaire. "
            "Continuez simplement à surveiller l'espace disponible."
        ),
    )


if __name__ == "__main__":

    from avs.system.storage_probe import get_storage_info

    storage = get_storage_info()
    diagnostic = analyze_storage(storage)

    print("=" * 55)
    print("             AVS COMPUTER ASSISTANT")
    print("                DIAGNOSTIC STOCKAGE")
    print("=" * 55)

    print(f"\nLecteur : {storage.drive}")
    print(f"Espace total      : {storage.total_gb} Go")
    print(f"Espace utilisé    : {storage.used_gb} Go")
    print(f"Espace disponible : {storage.free_gb} Go")
    print(f"Utilisation       : {storage.usage_percent}%")

    print("\nAnalyse...")
    
    print("\n" + "-" * 55)
    print("                    DIAGNOSTIC")
    print("-" * 55)

    print(f"\nSTATUT : {diagnostic.status}")

    print(f"\n{diagnostic.message}")

    print("\nRECOMMANDATION")
    print(diagnostic.recommendation)

    print("\n" + "-" * 55)