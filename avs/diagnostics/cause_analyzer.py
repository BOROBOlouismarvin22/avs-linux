# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT
ANALYSEUR DE CAUSES

Ce module cherche des causes probables à partir
des diagnostics RAM, CPU, stockage et processus.

AVS ne prétend pas connaître la cause exacte.
Il formule des hypothèses à partir des observations.
"""


def analyze_causes(
    ram_diagnostic: dict,
    cpu_diagnostic: dict,
    disk_diagnostic: dict,
    process_diagnostics: list[dict],
) -> dict:
    """
    Analyse les diagnostics afin d'identifier
    les causes probables des problèmes système.
    """

    causes = []
    evidence = []
    recommendations = []

    # =====================================================
    # RAM
    # =====================================================

    ram_usage = ram_diagnostic.get(
        "usage_status",
        "",
    )

    ram_capacity = ram_diagnostic.get(
        "capacity_status",
        "",
    )

    ram_problem = ram_usage in {
        "ÉLEVÉ",
        "CRITIQUE",
    }

    ram_capacity_problem = ram_capacity in {
        "LIMITÉE",
        "TRÈS LIMITÉE",
    }

    if ram_problem:

        causes.append(
            "Forte sollicitation de la mémoire RAM."
        )

        evidence.append(
            "Le niveau d'utilisation de la RAM est élevé."
        )

        recommendations.append(
            "Fermer les applications inutilisées et "
            "identifier les processus consommant le plus de RAM."
        )

    if ram_capacity_problem:

        causes.append(
            "Capacité RAM limitée."
        )

        evidence.append(
            "La capacité totale de RAM est limitée."
        )

        recommendations.append(
            "Envisager une augmentation de la mémoire RAM "
            "si le matériel le permet."
        )

    # =====================================================
    # CPU
    # =====================================================

    cpu_usage = cpu_diagnostic.get(
        "usage_status",
        "",
    )

    cpu_problem = cpu_usage in {
        "ÉLEVÉE",
        "TRÈS ÉLEVÉE",
        "CRITIQUE",
    }

    if cpu_problem:

        causes.append(
            "Forte sollicitation du processeur."
        )

        evidence.append(
            "Le niveau d'utilisation du CPU est élevé."
        )

        recommendations.append(
            "Identifier les applications consommant beaucoup "
            "de CPU et fermer les programmes inutilisés."
        )

    # =====================================================
    # STOCKAGE
    # =====================================================

    disk_usage = disk_diagnostic.get(
        "usage_status",
        "",
    )

    disk_free = disk_diagnostic.get(
        "free_space_status",
        disk_diagnostic.get(
            "free_status",
            "",
        ),
    )

    disk_problem = disk_usage in {
        "ATTENTION",
        "ÉLEVÉ",
        "CRITIQUE",
    }

    # Les vraies valeurs produites par disk_diagnostic.py sont
    # "FAIBLE" / "TRÈS FAIBLE", pas "LIMITÉ" / "TRÈS LIMITÉ".
    # (Bug corrigé : avec les anciennes valeurs, cette condition
    # n'était jamais vraie, quel que soit l'espace libre réel.)
    disk_space_problem = disk_free in {
        "FAIBLE",
        "TRÈS FAIBLE",
    }

    if disk_problem or disk_space_problem:

        causes.append(
            "Espace de stockage insuffisant ou fortement utilisé."
        )

        evidence.append(
            "Le stockage présente un niveau d'utilisation "
            "ou un espace libre préoccupant."
        )

        recommendations.append(
            "Supprimer les fichiers inutiles et libérer "
            "de l'espace disque."
        )

    # =====================================================
    # PROCESSUS
    # =====================================================

    high_ram_processes = [
        process
        for process in process_diagnostics
        if process.get("status") in {
            "ÉLEVÉ",
            "CRITIQUE",
        }
        and process.get("memory_mb", 0) >= 500
    ]

    high_cpu_processes = [
        process
        for process in process_diagnostics
        if process.get("status") in {
            "ÉLEVÉ",
            "CRITIQUE",
        }
        and process.get("cpu_percent", 0) >= 50
    ]

    if high_ram_processes:

        causes.append(
            "Un ou plusieurs processus consomment "
            "beaucoup de mémoire RAM."
        )

        for process in high_ram_processes[:3]:

            evidence.append(
                f"{process['name']} utilise "
                f"{process['memory_mb']:.2f} MB de RAM."
            )

    if high_cpu_processes:

        causes.append(
            "Un ou plusieurs processus sollicitent "
            "fortement le CPU."
        )

        for process in high_cpu_processes[:3]:

            evidence.append(
                f"{process['name']} utilise "
                f"{process['cpu_percent']:.2f}% du CPU."
            )

    # =====================================================
    # CORRELATION RAM + CPU
    # =====================================================

    if ram_problem and cpu_problem:

        causes.append(
            "La RAM et le CPU sont fortement sollicités "
            "simultanément."
        )

        evidence.append(
            "Les deux ressources principales présentent "
            "une forte utilisation au même moment."
        )

        recommendations.append(
            "Examiner en priorité les applications et "
            "processus actifs afin d'identifier ceux "
            "qui contribuent à la charge système."
        )

    # =====================================================
    # AUCUN PROBLEME
    # =====================================================

    if not causes:

        status = "NORMAL"
        priority = "FAIBLE"

        summary = (
            "Aucune cause préoccupante n'a été identifiée "
            "à partir des mesures disponibles."
        )

        recommendations.append(
            "Aucune action immédiate nécessaire. "
            "Continuer à surveiller le système."
        )

    # =====================================================
    # PROBLEME DETECTE
    # =====================================================

    else:

        status = "PROBLÈME DÉTECTÉ"

        if ram_problem and cpu_problem:

            priority = "HAUTE"

        elif ram_problem or cpu_problem:

            priority = "MOYENNE"

        elif disk_problem or disk_space_problem:

            priority = "MOYENNE"

        else:

            priority = "FAIBLE"

        summary = (
            "AVS a identifié une ou plusieurs causes "
            "probables nécessitant une vérification."
        )

    # =====================================================
    # SUPPRESSION DES DOUBLONS
    # =====================================================

    recommendations = list(
        dict.fromkeys(recommendations)
    )

    return {
        "status": status,
        "priority": priority,
        "summary": summary,
        "causes": causes,
        "evidence": evidence,
        "recommendations": recommendations,
    }


# =========================================================
# AFFICHAGE
# =========================================================

def display_cause_analysis(result: dict) -> None:
    """Affiche l'analyse des causes dans le terminal."""

    print("=" * 70)
    print("                 AVS COMPUTER ASSISTANT")
    print("                    ANALYSE DES CAUSES")
    print("=" * 70)

    print()
    print("ÉTAT")
    print("-" * 70)

    print(f"Statut     : {result['status']}")
    print(f"Priorité   : {result['priority']}")

    print()
    print(result["summary"])

    print()
    print("CAUSES PROBABLES")
    print("-" * 70)

    if result["causes"]:

        for cause in result["causes"]:
            print(f"- {cause}")

    else:

        print(
            "- Aucune cause préoccupante identifiée."
        )

    print()
    print("ÉLÉMENTS OBSERVÉS")
    print("-" * 70)

    if result["evidence"]:

        for item in result["evidence"]:
            print(f"- {item}")

    else:

        print(
            "- Aucun élément préoccupant."
        )

    print()
    print("RECOMMANDATIONS")
    print("-" * 70)

    for recommendation in result["recommendations"]:
        print(f"- {recommendation}")

    print()
    print("=" * 70)