"""
AVS Computer Assistant
======================

PROCESS PROBE

Ce module récupère les informations réelles
sur les processus actuellement exécutés.

Responsabilité :
    - récupérer les processus
    - mesurer leur consommation CPU
    - mesurer leur consommation RAM
    - trier les processus

Ce module NE fait aucun diagnostic.
"""

from dataclasses import dataclass

import psutil


@dataclass
class ProcessResult:
    """Informations mesurées pour un processus."""

    pid: int
    name: str
    cpu_percent: float
    memory_mb: float


def get_process_info(limit: int = 10) -> list[ProcessResult]:
    """
    Récupère les processus consommant le plus de RAM.

    Parameters
    ----------
    limit : int
        Nombre maximum de processus à retourner.

    Returns
    -------
    list[ProcessResult]
        Liste des processus triés par consommation RAM.
    """

    if limit <= 0:
        return []

    processes: list[ProcessResult] = []

    for process in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_info"]
    ):
        try:
            info = process.info

            pid = info.get("pid")
            name = info.get("name") or "Inconnu"
            cpu_percent = info.get("cpu_percent") or 0.0
            memory_info = info.get("memory_info")

            if memory_info is None:
                continue

            memory_mb = memory_info.rss / (1024 * 1024)

            processes.append(
                ProcessResult(
                    pid=pid,
                    name=name,
                    cpu_percent=round(cpu_percent, 2),
                    memory_mb=round(memory_mb, 2),
                )
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(
        key=lambda process: process.memory_mb,
        reverse=True,
    )

    return processes[:limit]


def display_processes(processes: list[ProcessResult]) -> None:
    """Affiche les processus mesurés."""

    print("=" * 75)
    print("                 AVS COMPUTER ASSISTANT")
    print("                    ANALYSE PROCESSUS")
    print("=" * 75)

    print()
    print("PROCESSUS CONSOMMANT LE PLUS DE RAM")
    print("-" * 75)

    if not processes:
        print("Aucun processus accessible.")
        return

    print(
        f"{'PID':<8}"
        f"{'PROCESSUS':<30}"
        f"{'RAM (MB)':>12}"
        f"{'CPU (%)':>12}"
    )

    print("-" * 75)

    for process in processes:
        print(
            f"{process.pid:<8}"
            f"{process.name[:28]:<30}"
            f"{process.memory_mb:>12.2f}"
            f"{process.cpu_percent:>12.2f}"
        )

    print()
    print("=" * 75)


if __name__ == "__main__":
    results = get_process_info(limit=10)
    display_processes(results)