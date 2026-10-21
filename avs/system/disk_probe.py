"""
disk_probe.py

Couche système du module stockage.

Ce module récupère les informations réelles
concernant l'espace disque sous Windows.

Il ne prend aucune décision de diagnostic.
"""

import ctypes
from dataclasses import dataclass


@dataclass
class DiskResult:
    """Informations brutes concernant le stockage."""

    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float


def get_disk_info(drive="C:\\") -> DiskResult:
    """
    Récupère les informations réelles du disque.

    Par défaut, le disque système C: est analysé.
    """

    free_bytes = ctypes.c_ulonglong()
    total_bytes = ctypes.c_ulonglong()
    available_bytes = ctypes.c_ulonglong()

    result = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
        ctypes.c_wchar_p(drive),
        ctypes.byref(available_bytes),
        ctypes.byref(total_bytes),
        ctypes.byref(free_bytes),
    )

    if not result:
        raise OSError(
            f"Impossible de récupérer les informations du disque {drive}"
        )

    total_gb = total_bytes.value / (1024 ** 3)
    free_gb = free_bytes.value / (1024 ** 3)
    used_gb = total_gb - free_gb

    if total_gb > 0:
        usage_percent = (used_gb / total_gb) * 100
    else:
        usage_percent = 0.0

    return DiskResult(
        total_gb=round(total_gb, 2),
        used_gb=round(used_gb, 2),
        free_gb=round(free_gb, 2),
        usage_percent=round(usage_percent, 2),
    )


if __name__ == "__main__":

    result = get_disk_info()

    print("=" * 55)
    print("             AVS COMPUTER ASSISTANT")
    print("              ANALYSE DU STOCKAGE")
    print("=" * 55)

    print(f"\nDisque analysé    : C:")
    print(f"Capacité totale   : {result.total_gb} Go")
    print(f"Espace utilisé    : {result.used_gb} Go")
    print(f"Espace libre      : {result.free_gb} Go")
    print(f"Utilisation       : {result.usage_percent}%")

# --- AVS_LINUX_PATCH : versions Linux ---
import sys as _avs_sys
if not _avs_sys.platform.startswith('win'):
    from avs.system import linux_compat as _avs_lc
    get_disk_info = _avs_lc.get_disk_info  # AVS_LINUX_PATCH
