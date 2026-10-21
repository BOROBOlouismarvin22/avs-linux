"""
AVS Computer Assistant
Diagnostic de l'utilisation du CPU.
"""


def diagnose_cpu(usage_percent, logical_processors):
    """Analyse l'utilisation du processeur."""

    # Diagnostic de l'utilisation CPU
    if usage_percent < 50:
        usage_status = "FAIBLE"
        usage_message = (
            "Le processeur est faiblement sollicité. "
            "Aucune charge importante n'est détectée."
        )

    elif usage_percent < 70:
        usage_status = "NORMALE"
        usage_message = (
            "L'utilisation du processeur est normale "
            "pour une utilisation courante."
        )

    elif usage_percent < 85:
        usage_status = "ÉLEVÉE"
        usage_message = (
            "Le processeur est fortement sollicité. "
            "Certaines applications ou tâches en arrière-plan "
            "peuvent consommer beaucoup de ressources."
        )

    elif usage_percent < 95:
        usage_status = "TRÈS ÉLEVÉE"
        usage_message = (
            "Le processeur est très fortement sollicité. "
            "Une charge importante peut provoquer des ralentissements."
        )

    else:
        usage_status = "CRITIQUE"
        usage_message = (
            "Le processeur est presque totalement sollicité. "
            "Le système risque de subir des ralentissements importants."
        )

    # Diagnostic du nombre de processeurs logiques
    if logical_processors <= 2:
        processor_status = "LIMITÉ"
        processor_message = (
            "Le nombre de processeurs logiques est limité. "
            "Le multitâche peut être plus difficile."
        )

    elif logical_processors <= 4:
        processor_status = "CORRECT"
        processor_message = (
            "Le nombre de processeurs logiques est correct "
            "pour les tâches courantes."
        )

    else:
        processor_status = "BON"
        processor_message = (
            "Le nombre de processeurs logiques est adapté "
            "au multitâche et aux applications modernes."
        )

    # Recommandation
    if usage_percent >= 85:
        recommendation = (
            "Identifier les applications consommant beaucoup de CPU, "
            "fermer les programmes inutilisés et vérifier les tâches "
            "exécutées en arrière-plan."
        )

    elif usage_percent >= 70:
        recommendation = (
            "Surveiller les applications utilisant fortement le CPU "
            "et fermer celles qui ne sont pas nécessaires."
        )

    else:
        recommendation = (
            "Aucune action immédiate nécessaire. "
            "Surveiller l'utilisation du CPU si des ralentissements apparaissent."
        )

    return {
        "usage_percent": usage_percent,
        "usage_status": usage_status,
        "usage_message": usage_message,
        "logical_processors": logical_processors,
        "processor_status": processor_status,
        "processor_message": processor_message,
        "recommendation": recommendation,
    }


def format_cpu_diagnostic(result):
    """Transforme le diagnostic CPU en rapport lisible."""

    return f"""
=======================================================
             AVS COMPUTER ASSISTANT
                DIAGNOSTIC CPU
=======================================================

UTILISATION CPU
----------------
Utilisation       : {result["usage_percent"]} %
Statut             : {result["usage_status"]}

{result["usage_message"]}


PROCESSEURS LOGIQUES
---------------------
Nombre             : {result["logical_processors"]}
Statut             : {result["processor_status"]}

{result["processor_message"]}


RECOMMANDATION
---------------
{result["recommendation"]}

=======================================================
"""


if __name__ == "__main__":
    from avs.system.cpu_probe import get_cpu_info

    cpu = get_cpu_info()

    result = diagnose_cpu(
        usage_percent=cpu.usage_percent,
        logical_processors=cpu.logical_processors,
    )

    print("=" * 55)
    print("             AVS COMPUTER ASSISTANT")
    print("                DIAGNOSTIC CPU")
    print("=" * 55)

    print()
    print(f"Utilisation CPU       : {cpu.usage_percent}%")
    print(f"Processeurs logiques  : {cpu.logical_processors}")

    print()
    print("DIAGNOSTIC")
    print("-" * 55)

    print(f"Utilisation           : {result['usage_status']}")
    print(f"Processeurs           : {result['processor_status']}")

    print()
    print(result["usage_message"])
    print(result["processor_message"])

    print()
    print("RECOMMANDATION")
    print("-" * 55)
    print(result["recommendation"])

    print()
    print("=" * 55)