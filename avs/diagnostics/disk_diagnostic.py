"""
AVS Computer Assistant
Diagnostic du stockage.
"""


def diagnose_disk(total_gb, used_gb, free_gb, usage_percent):
    """Analyse l'utilisation de l'espace disque."""

    if usage_percent < 70:
        usage_status = "OK"
        usage_message = (
            "L'espace disque disponible est suffisant "
            "pour une utilisation normale."
        )

    elif usage_percent <= 85:
        usage_status = "ATTENTION"
        usage_message = (
            "L'espace disque commence à être fortement utilisé. "
            "Il est conseillé de surveiller l'espace disponible."
        )

    elif usage_percent <= 95:
        usage_status = "ÉLEVÉ"
        usage_message = (
            "L'espace disque est fortement utilisé. "
            "Le stockage disponible commence à devenir limité."
        )

    else:
        usage_status = "CRITIQUE"
        usage_message = (
            "Le disque est presque saturé. "
            "Le manque d'espace peut provoquer des problèmes "
            "de fonctionnement du système."
        )

    # Diagnostic de l'espace libre
    if free_gb < 10:
        free_status = "TRÈS FAIBLE"
        free_message = (
            "L'espace libre est très faible. "
            "Une libération d'espace est fortement recommandée."
        )

    elif free_gb < 25:
        free_status = "FAIBLE"
        free_message = (
            "L'espace libre est limité. "
            "Il est conseillé de supprimer les fichiers inutiles."
        )

    else:
        free_status = "CORRECT"
        free_message = (
            "L'espace libre disponible est suffisant "
            "pour une utilisation courante."
        )

    # Recommandation
    if usage_percent > 95 or free_gb < 10:
        recommendation = (
            "Libérer rapidement de l'espace disque en supprimant "
            "les fichiers inutiles, les téléchargements volumineux "
            "et les applications qui ne sont plus utilisées."
        )

    elif usage_percent > 85 or free_gb < 25:
        recommendation = (
            "Surveiller l'espace disponible et effectuer régulièrement "
            "un nettoyage des fichiers inutiles."
        )

    else:
        recommendation = (
            "Aucune action immédiate nécessaire. "
            "Continuer à surveiller l'espace disque."
        )

    return {
        "total_gb": total_gb,
        "used_gb": used_gb,
        "free_gb": free_gb,
        "usage_percent": usage_percent,
        "usage_status": usage_status,
        "usage_message": usage_message,
        "free_status": free_status,
        "free_message": free_message,
        "recommendation": recommendation,
    }


def format_disk_diagnostic(result):
    """Transforme le diagnostic stockage en rapport lisible."""

    return f"""
=======================================================
             AVS COMPUTER ASSISTANT
              DIAGNOSTIC STOCKAGE
=======================================================

ESPACE DISQUE
--------------
Capacité totale   : {result["total_gb"]:.2f} Go
Espace utilisé    : {result["used_gb"]:.2f} Go
Espace libre      : {result["free_gb"]:.2f} Go
Utilisation       : {result["usage_percent"]} %

Statut utilisation : {result["usage_status"]}
Statut espace libre : {result["free_status"]}

{result["usage_message"]}

{result["free_message"]}


RECOMMANDATION
---------------
{result["recommendation"]}

=======================================================
"""


if __name__ == "__main__":
    from avs.system.disk_probe import get_disk_info

    disk = get_disk_info()

    result = diagnose_disk(
        total_gb=disk.total_gb,
        used_gb=disk.used_gb,
        free_gb=disk.free_gb,
        usage_percent=disk.usage_percent,
    )

    print("=" * 55)
    print("             AVS COMPUTER ASSISTANT")
    print("              DIAGNOSTIC STOCKAGE")
    print("=" * 55)

    print()
    print(f"Capacité totale   : {disk.total_gb} Go")
    print(f"Espace utilisé    : {disk.used_gb} Go")
    print(f"Espace libre      : {disk.free_gb} Go")
    print(f"Utilisation       : {disk.usage_percent}%")

    print()
    print("DIAGNOSTIC")
    print("-" * 55)

    print(f"Utilisation       : {result['usage_status']}")
    print(f"Espace libre      : {result['free_status']}")

    print()
    print(result["usage_message"])
    print(result["free_message"])

    print()
    print("RECOMMANDATION")
    print("-" * 55)
    print(result["recommendation"])

    print()
    print("=" * 55)