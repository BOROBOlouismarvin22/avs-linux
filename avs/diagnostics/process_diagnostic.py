"""
AVS Computer Assistant
======================

PROCESS DIAGNOSTIC

Ce module interprète les mesures fournies
par process_probe.py.

Il ne mesure rien lui-même.
Il analyse les processus et détermine
les niveaux de consommation RAM et CPU.
"""


from avs.system.process_probe import ProcessResult


def diagnose_process(
    process: ProcessResult,
    ram_threshold: float = 500.0,
    cpu_threshold: float = 50.0,
) -> dict:
    """
    Analyse la consommation d'un processus.

    Parameters
    ----------
    process : ProcessResult
        Informations mesurées sur le processus.

    ram_threshold : float
        Seuil RAM en MB considéré comme élevé.

    cpu_threshold : float
        Seuil CPU en % considéré comme élevé.

    Returns
    -------
    dict
        Diagnostic du processus.
    """

    ram_high = process.memory_mb >= ram_threshold
    cpu_high = process.cpu_percent >= cpu_threshold

    if ram_high and cpu_high:
        status = "CRITIQUE"

        message = (
            "Le processus consomme fortement la RAM "
            "et le CPU."
        )

        recommendation = (
            "Vérifier si ce processus est nécessaire. "
            "S'il n'est pas indispensable, fermer l'application "
            "et effectuer une nouvelle analyse."
        )

    elif ram_high:
        status = "ÉLEVÉ"

        message = (
            "Le processus consomme une quantité importante "
            "de mémoire RAM."
        )

        recommendation = (
            "Vérifier l'utilisation de ce processus et fermer "
            "l'application si elle n'est pas nécessaire."
        )

    elif cpu_high:
        status = "ÉLEVÉ"

        message = (
            "Le processus utilise fortement le processeur."
        )

        recommendation = (
            "Vérifier l'activité du processus et fermer "
            "l'application si elle n'est pas nécessaire."
        )

    else:
        status = "NORMAL"

        message = (
            "La consommation du processus reste dans "
            "une plage normale."
        )

        recommendation = (
            "Aucune action immédiate nécessaire."
        )

    return {
        "pid": process.pid,
        "name": process.name,
        "memory_mb": process.memory_mb,
        "cpu_percent": process.cpu_percent,
        "status": status,
        "message": message,
        "recommendation": recommendation,
    }


def diagnose_processes(
    processes: list[ProcessResult],
    ram_threshold: float = 500.0,
    cpu_threshold: float = 50.0,
) -> list[dict]:
    """
    Analyse une liste de processus.
    """

    return [
        diagnose_process(
            process,
            ram_threshold=ram_threshold,
            cpu_threshold=cpu_threshold,
        )
        for process in processes
    ]


def display_process_diagnostics(
    diagnostics: list[dict],
) -> None:
    """Affiche les diagnostics des processus."""

    print("=" * 80)
    print("                 AVS COMPUTER ASSISTANT")
    print("                DIAGNOSTIC PROCESSUS")
    print("=" * 80)

    print()

    if not diagnostics:
        print("Aucun processus à analyser.")
        print("=" * 80)
        return

    for diagnostic in diagnostics:

        print(
            f"PID : {diagnostic['pid']}"
        )

        print(
            f"Processus : {diagnostic['name']}"
        )

        print(
            f"RAM : {diagnostic['memory_mb']:.2f} MB"
        )

        print(
            f"CPU : {diagnostic['cpu_percent']:.2f}%"
        )

        print(
            f"Statut : {diagnostic['status']}"
        )

        print(
            f"Diagnostic : {diagnostic['message']}"
        )

        print(
            f"Recommandation : {diagnostic['recommendation']}"
        )

        print("-" * 80)

    print("=" * 80)


if __name__ == "__main__":

    from avs.system.process_probe import get_process_info

    processes = get_process_info(limit=10)

    diagnostics = diagnose_processes(processes)

    display_process_diagnostics(diagnostics)