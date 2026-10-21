"""
AVS Computer Assistant

Moteur de diagnostic global.

Ce module ne mesure aucune ressource.
Il analyse les résultats déjà produits
par les différents modules de diagnostic.
"""


def diagnose_system(report):
    """
    Analyse globalement les résultats RAM, CPU et stockage.

    Parameters
    ----------
    report : dict
        Rapport produit par system_orchestrator.py

    Returns
    -------
    dict
        Diagnostic global du système.
    """

    ram = report["ram"]["diagnostic"]
    cpu = report["cpu"]["diagnostic"]
    disk = report["disk"]["diagnostic"]

    # =====================================================
    # Récupération des statuts
    # =====================================================

    ram_status = ram["usage_status"]
    cpu_status = cpu["usage_status"]
    disk_status = disk["usage_status"]

    # =====================================================
    # Détection des ressources problématiques
    # =====================================================

    problems = []

    if ram_status in ("ÉLEVÉ", "CRITIQUE"):
        problems.append("RAM")

    if cpu_status in ("ÉLEVÉE", "TRÈS ÉLEVÉE", "CRITIQUE"):
        problems.append("CPU")

    if disk_status in ("ÉLEVÉ", "CRITIQUE"):
        problems.append("STOCKAGE")

    # =====================================================
    # Diagnostic global
    # =====================================================

    if len(problems) == 0:
        global_status = "NORMAL"

        global_message = (
            "Aucune anomalie importante n'a été détectée "
            "sur les ressources principales analysées."
        )

        priority = "AUCUNE"

    elif len(problems) == 1:
        global_status = "ATTENTION"

        global_message = (
            f"Une ressource présente une charge importante : "
            f"{problems[0]}. Une investigation ciblée est recommandée."
        )

        priority = "MOYENNE"

    else:
        global_status = "ÉLEVÉ"

        resources = " et ".join(problems)

        global_message = (
            f"Plusieurs ressources sont fortement sollicitées : "
            f"{resources}. Le système peut subir des ralentissements."
        )

        priority = "HAUTE"

    # =====================================================
    # Analyse spécifique RAM + CPU
    # =====================================================

    if (
        ram_status in ("ÉLEVÉ", "CRITIQUE")
        and cpu_status in ("ÉLEVÉE", "TRÈS ÉLEVÉE", "CRITIQUE")
        and disk_status == "OK"
    ):
        global_status = "ÉLEVÉ"

        global_message = (
            "La RAM et le CPU sont fortement sollicités simultanément, "
            "tandis que le stockage ne présente pas de problème apparent. "
            "Les applications et processus actifs doivent être examinés."
        )

        priority = "HAUTE"

    # =====================================================
    # Recommandation globale
    # =====================================================

    if priority == "HAUTE":
        recommendation = (
            "Identifier les applications et processus consommant "
            "le plus de RAM et de CPU. Fermer les programmes inutilisés "
            "et effectuer une nouvelle analyse après nettoyage."
        )

    elif priority == "MOYENNE":
        recommendation = (
            "Identifier la ressource présentant la charge importante "
            "et rechercher les applications responsables."
        )

    else:
        recommendation = (
            "Aucune intervention immédiate nécessaire. "
            "Continuer à surveiller les performances du système."
        )

    return {
        "global_status": global_status,
        "global_message": global_message,
        "priority": priority,
        "problems": problems,
        "recommendation": recommendation,
    }


def display_global_diagnostic(result):
    """Affiche le diagnostic global."""

    print()
    print("=" * 65)
    print("                 AVS COMPUTER ASSISTANT")
    print("              DIAGNOSTIC SYSTÈME GLOBAL")
    print("=" * 65)

    print()
    print("ÉTAT GLOBAL")
    print("-" * 65)

    print(f"Statut       : {result['global_status']}")
    print(f"Priorité     : {result['priority']}")

    print()
    print(result["global_message"])

    print()

    if result["problems"]:
        print("RESSOURCES À SURVEILLER")
        print("-" * 65)

        for problem in result["problems"]:
            print(f"- {problem}")

    else:
        print("RESSOURCES À SURVEILLER")
        print("-" * 65)
        print("Aucune")

    print()
    print("ACTION PRIORITAIRE")
    print("-" * 65)
    print(result["recommendation"])

    print()
    print("=" * 65)


if __name__ == "__main__":
    from avs.orchestrator.system_orchestrator import run_system_diagnostic

    report = run_system_diagnostic()

    result = diagnose_system(report)

    display_global_diagnostic(result)