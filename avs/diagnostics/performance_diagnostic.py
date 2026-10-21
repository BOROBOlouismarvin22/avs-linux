# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT
DIAGNOSTIC DE LA MEMOIRE RAM
"""


def diagnose_ram(
    total_gb: float,
    used_gb: float,
    usage_percent: float,
) -> dict:

    # DIAGNOSTIC UTILISATION RAM

    if usage_percent < 70:
        usage_status = "OK"
        usage_message = (
            "La mémoire RAM est correctement utilisée."
        )

    elif usage_percent <= 85:
        usage_status = "ATTENTION"
        usage_message = (
            "La mémoire RAM commence à être fortement sollicitée."
        )

    elif usage_percent <= 95:
        usage_status = "ÉLEVÉ"
        usage_message = (
            "La mémoire RAM est fortement utilisée."
        )

    else:
        usage_status = "CRITIQUE"
        usage_message = (
            "La mémoire RAM est presque totalement utilisée."
        )

    # DIAGNOSTIC CAPACITE RAM

    if total_gb < 4:
        capacity_status = "TRÈS LIMITÉE"
        capacity_message = (
            "La capacité totale de RAM est très limitée "
            "pour un usage informatique moderne."
        )

    elif total_gb < 8:
        capacity_status = "LIMITÉE"
        capacity_message = (
            "La capacité totale de RAM peut limiter "
            "certaines tâches exigeantes."
        )

    else:
        capacity_status = "BONNE"
        capacity_message = (
            "La capacité totale de RAM est adaptée "
            "à une utilisation courante."
        )

    # RECOMMANDATION
    # Basée directement sur usage_status, pour rester cohérente
    # avec le diagnostic affiché (pas de seuil recalculé séparément).

    if usage_status == "CRITIQUE":
        recommendation = (
            "Fermer immédiatement les applications inutilisées et "
            "identifier les programmes consommant le plus de mémoire. "
            "Un redémarrage peut également libérer de la RAM."
        )

    elif usage_status == "ÉLEVÉ":
        recommendation = (
            "Fermer les applications inutilisées et "
            "identifier les programmes consommant "
            "beaucoup de mémoire."
        )

    elif usage_status == "ATTENTION":
        recommendation = (
            "Surveiller l'utilisation de la RAM et envisager de "
            "fermer les applications les moins nécessaires."
        )

    elif total_gb < 4:
        recommendation = (
            "Envisager une augmentation de la mémoire RAM "
            "si le matériel le permet."
        )

    else:
        recommendation = (
            "Aucune action immédiate nécessaire. "
            "Continuer à surveiller l'utilisation de la RAM."
        )

    # RESULTAT

    return {
        "total_gb": round(total_gb, 2),
        "used_gb": round(used_gb, 2),
        "available_gb": round(total_gb - used_gb, 2),
        "usage_percent": round(usage_percent, 2),
        "usage_status": usage_status,
        "usage_message": usage_message,
        "capacity_status": capacity_status,
        "capacity_message": capacity_message,
        "recommendation": recommendation,
    }


if __name__ == "__main__":

    from avs.system.performance_probe import get_memory_info

    memory = get_memory_info()

    diagnostic = diagnose_ram(
        memory.total_gb,
        memory.used_gb,
        memory.usage_percent,
    )

    print("=" * 55)
    print("             AVS COMPUTER ASSISTANT")
    print("             DIAGNOSTIC MEMOIRE RAM")
    print("=" * 55)

    print()
    print(f"RAM totale       : {diagnostic['total_gb']} Go")
    print(f"RAM utilisée     : {diagnostic['used_gb']} Go")
    print(f"RAM disponible   : {diagnostic['available_gb']} Go")
    print(f"Utilisation RAM  : {diagnostic['usage_percent']}%")

    print()
    print("DIAGNOSTIC")
    print("-" * 55)

    print(f"Utilisation      : {diagnostic['usage_status']}")
    print(f"Capacité         : {diagnostic['capacity_status']}")

    print()
    print(diagnostic["usage_message"])
    print(diagnostic["capacity_message"])

    print()
    print("RECOMMANDATION")
    print("-" * 55)
    print(diagnostic["recommendation"])

    print()
    print("=" * 55)