"""
AVS COMPUTER ASSISTANT
======================

RAPPORT SYSTEME COMPLET

Ce module rassemble les differentes analyses
d'AVS dans un rapport unique et lisible.
"""


def build_system_report(
    ram_diagnostic: dict,
    cpu_diagnostic: dict,
    disk_diagnostic: dict,
    process_diagnostics: list[dict],
    cause_analysis: dict,
    action_decision: dict,
) -> dict:
    """
    Construit le rapport systeme complet d'AVS.
    """

    return {
        "ram": ram_diagnostic,
        "cpu": cpu_diagnostic,
        "disk": disk_diagnostic,
        "processes": process_diagnostics,
        "causes": cause_analysis,
        "actions": action_decision,
    }


def display_system_report(report: dict) -> None:
    """
    Affiche le rapport systeme complet.
    """

    ram = report["ram"]
    cpu = report["cpu"]
    disk = report["disk"]
    processes = report["processes"]
    causes = report["causes"]
    actions = report["actions"]

    print("=" * 75)
    print("                 AVS COMPUTER ASSISTANT")
    print("                  RAPPORT SYSTEME COMPLET")
    print("=" * 75)

    # =====================================================
    # RAM
    # =====================================================

    print()
    print("MEMOIRE RAM")
    print("-" * 75)

    print(
        f"RAM totale       : "
        f"{ram.get('total_gb', 'N/A')} Go"
    )

    print(
        f"RAM utilisee     : "
        f"{ram.get('used_gb', ram.get('used', 'N/A'))} Go"
    )

    print(
        f"RAM disponible   : "
        f"{ram.get('available_gb', ram.get('available', 'N/A'))} Go"
    )

    print(
        f"Utilisation      : "
        f"{ram.get('usage_percent', 'N/A')}%"
    )

    print(
        f"Statut utilisation : "
        f"{ram.get('usage_status', 'N/A')}"
    )

    print(
        f"Statut capacite    : "
        f"{ram.get('capacity_status', 'N/A')}"
    )

    # =====================================================
    # CPU
    # =====================================================

    print()
    print("CPU")
    print("-" * 75)

    print(
        f"Utilisation      : "
        f"{cpu.get('usage_percent', 'N/A')}%"
    )

    print(
        f"Processeurs      : "
        f"{cpu.get('logical_processors', 'N/A')}"
    )

    print(
        f"Statut utilisation : "
        f"{cpu.get('usage_status', 'N/A')}"
    )

    print(
        f"Statut processeurs : "
        f"{cpu.get('processor_status', 'N/A')}"
    )

    # =====================================================
    # STOCKAGE
    # =====================================================

    print()
    print("STOCKAGE")
    print("-" * 75)

    print(
        f"Capacite totale  : "
        f"{disk.get('total_gb', 'N/A')} Go"
    )

    print(
        f"Espace utilise   : "
        f"{disk.get('used_gb', 'N/A')} Go"
    )

    print(
        f"Espace libre     : "
        f"{disk.get('free_gb', 'N/A')} Go"
    )

    print(
        f"Utilisation      : "
        f"{disk.get('usage_percent', 'N/A')}%"
    )

    print(
        f"Statut utilisation : "
        f"{disk.get('usage_status', 'N/A')}"
    )

    print(
        f"Statut espace libre : "
        f"{disk.get('free_status', 'N/A')}"
    )

    # =====================================================
    # PROCESSUS
    # =====================================================

    print()
    print("PROCESSUS PRINCIPAUX")
    print("-" * 75)

    if processes:

        print(
            f"{'PID':<8}"
            f"{'PROCESSUS':<30}"
            f"{'RAM (MB)':>12}"
            f"{'CPU (%)':>12}"
        )

        print("-" * 75)

        for process in processes[:10]:

            print(
                f"{process.get('pid', 'N/A'):<8}"
                f"{process.get('name', 'N/A'):<30}"
                f"{process.get('memory_mb', 0):>12.2f}"
                f"{process.get('cpu_percent', 0):>12.2f}"
            )

    else:
        print("Aucun processus disponible.")

    # =====================================================
    # CAUSES PROBABLES
    # =====================================================

    print()
    print("CAUSES PROBABLES")
    print("-" * 75)

    causes_list = causes.get("causes", [])

    if causes_list:

        for cause in causes_list:
            print(f"- {cause}")

    else:
        print("- Aucune cause préoccupante identifiée.")

    # =====================================================
    # PRIORITE
    # =====================================================

    print()
    print("PRIORITE")
    print("-" * 75)

    print(
        f"Statut   : "
        f"{causes.get('status', 'N/A')}"
    )

    print(
        f"Priorite : "
        f"{causes.get('priority', 'N/A')}"
    )

    # =====================================================
    # RECOMMANDATIONS
    # =====================================================

    print()
    print("RECOMMANDATIONS")
    print("-" * 75)

    recommendations = causes.get(
        "recommendations",
        [],
    )

    if recommendations:

        for index, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            print(
                f"{index}. {recommendation}"
            )

    else:
        print("Aucune recommandation disponible.")

    # =====================================================
    # ACTIONS
    # =====================================================

    print()
    print("ACTIONS A EFFECTUER")
    print("-" * 75)

    print(
        f"Statut   : "
        f"{actions.get('status', 'N/A')}"
    )

    print(
        f"Priorite : "
        f"{actions.get('priority', 'N/A')}"
    )

    action_list = actions.get(
        "actions",
        [],
    )

    if action_list:

        for index, action in enumerate(
            action_list,
            start=1,
        ):
            print(
                f"{index}. "
                f"[{action.get('priority', 'N/A')}] "
                f"{action.get('type', 'SYSTEME')}"
            )

            print(
                f"   {action.get('action', 'Aucune action disponible.')}"
            )

    else:
        print("Aucune action disponible.")

    print()
    print("=" * 75)


if __name__ == "__main__":

    from avs.system.performance_probe import get_memory_info
    from avs.system.cpu_probe import get_cpu_info
    from avs.system.disk_probe import get_disk_info
    from avs.system.process_probe import get_process_info

    from avs.diagnostics.performance_diagnostic import diagnose_ram
    from avs.diagnostics.cpu_diagnostic import diagnose_cpu
    from avs.diagnostics.disk_diagnostic import diagnose_disk
    from avs.diagnostics.process_diagnostic import diagnose_processes
    from avs.diagnostics.cause_analyzer import analyze_causes

    from avs.decision.action_engine import decide_action

    # =====================================================
    # MESURE RAM
    # =====================================================

    memory = get_memory_info()

    ram_diagnostic = diagnose_ram(
        memory.total_gb,
        memory.used_gb,
        memory.usage_percent,
    )

    # =====================================================
    # MESURE CPU
    # =====================================================

    cpu = get_cpu_info()

    cpu_diagnostic = diagnose_cpu(
        cpu.usage_percent,
        cpu.logical_processors,
    )

    # =====================================================
    # MESURE STOCKAGE
    # =====================================================

    disk = get_disk_info()

    disk_diagnostic = diagnose_disk(
        disk.total_gb,
        disk.used_gb,
        disk.free_gb,
        disk.usage_percent,
    )

    # =====================================================
    # MESURE PROCESSUS
    # =====================================================

    processes = get_process_info(
        limit=10
    )

    process_diagnostics = diagnose_processes(
        processes
    )

    # =====================================================
    # ANALYSE DES CAUSES
    # =====================================================

    cause_analysis = analyze_causes(
        ram_diagnostic,
        cpu_diagnostic,
        disk_diagnostic,
        process_diagnostics,
    )

    # =====================================================
    # MOTEUR D'ACTION
    # =====================================================

    action_decision = decide_action(
        ram_diagnostic,
        cpu_diagnostic,
        disk_diagnostic,
        process_diagnostics,
        cause_analysis,
    )

    # =====================================================
    # RAPPORT FINAL
    # =====================================================

    report = build_system_report(
        ram_diagnostic,
        cpu_diagnostic,
        disk_diagnostic,
        process_diagnostics,
        cause_analysis,
        action_decision,
    )

    display_system_report(report)