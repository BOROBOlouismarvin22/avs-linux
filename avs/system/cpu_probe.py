"""
cpu_probe.py

Couche système du module CPU.

Ce module récupère les informations réelles
concernant l'utilisation du processeur sous Windows.

Il ne prend aucune décision de diagnostic.
"""

import ctypes
import os
import time
from ctypes import wintypes
from dataclasses import dataclass


@dataclass
class CPUResult:
    """Informations brutes concernant le processeur."""

    usage_percent: float
    logical_processors: int


def _filetime_to_int(filetime):
    """Convertit une structure FILETIME en entier."""

    return (
        (filetime.dwHighDateTime << 32)
        | filetime.dwLowDateTime
    )


def get_cpu_info() -> CPUResult:
    """
    Récupère l'utilisation réelle du CPU sous Windows.

    La mesure est effectuée sur un court intervalle
    afin de calculer l'utilisation du processeur.
    """

    kernel32 = ctypes.windll.kernel32

    idle_before = wintypes.FILETIME()
    kernel_before = wintypes.FILETIME()
    user_before = wintypes.FILETIME()

    idle_after = wintypes.FILETIME()
    kernel_after = wintypes.FILETIME()
    user_after = wintypes.FILETIME()

    success = kernel32.GetSystemTimes(
        ctypes.byref(idle_before),
        ctypes.byref(kernel_before),
        ctypes.byref(user_before),
    )

    if not success:
        raise OSError("Impossible de récupérer les informations CPU.")

    time.sleep(0.5)

    success = kernel32.GetSystemTimes(
        ctypes.byref(idle_after),
        ctypes.byref(kernel_after),
        ctypes.byref(user_after),
    )

    if not success:
        raise OSError("Impossible de récupérer les informations CPU.")

    idle_delta = (
        _filetime_to_int(idle_after)
        - _filetime_to_int(idle_before)
    )

    kernel_delta = (
        _filetime_to_int(kernel_after)
        - _filetime_to_int(kernel_before)
    )

    user_delta = (
        _filetime_to_int(user_after)
        - _filetime_to_int(user_before)
    )

    total_delta = kernel_delta + user_delta

    if total_delta <= 0:
        usage_percent = 0.0
    else:
        usage_percent = (
            (total_delta - idle_delta)
            / total_delta
        ) * 100

    usage_percent = max(0.0, min(100.0, usage_percent))

    logical_processors = os.cpu_count() or 1

    return CPUResult(
        usage_percent=round(usage_percent, 2),
        logical_processors=logical_processors,
    )


if __name__ == "__main__":

    result = get_cpu_info()

    print("=" * 55)
    print("             AVS COMPUTER ASSISTANT")
    print("                ANALYSE DU CPU")
    print("=" * 55)

    print(f"\nUtilisation CPU       : {result.usage_percent}%")
    print(f"Processeurs logiques  : {result.logical_processors}")

# --- AVS_LINUX_PATCH : versions Linux ---
import sys as _avs_sys
if not _avs_sys.platform.startswith('win'):
    from avs.system import linux_compat as _avs_lc
    get_cpu_info = _avs_lc.get_cpu_info  # AVS_LINUX_PATCH
