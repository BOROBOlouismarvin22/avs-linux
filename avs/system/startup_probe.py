"""
startup_probe.py

Couche système du module "Programmes au démarrage".

Ce module lit les clés du registre Windows qui contiennent
les programmes lancés automatiquement à l'ouverture de session.

Il ne prend aucune décision de diagnostic, et ne modifie
jamais le registre (lecture seule).
"""

try:
    import winreg  # AVS_WINREG_STUB
except ImportError:  # Linux : remplaçant minimal pour que le module se charge
    class _WinregStub:
        def __getattr__(self, nom):
            return 0
    winreg = _WinregStub()
from dataclasses import dataclass
from typing import List


@dataclass
class StartupProgram:
    """Représente un programme configuré pour démarrer avec Windows."""

    name: str
    command: str
    source: str  # d'où vient l'entrée (ex: "Utilisateur actuel", "Toutes les sessions")


# Chaque entrée : (racine du registre, chemin, libellé source)
_STARTUP_LOCATIONS = [
    (
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "Utilisateur actuel",
    ),
    (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "Toutes les sessions",
    ),
]


def _read_registry_key(hive, path: str, source_label: str) -> List[StartupProgram]:
    """
    Lit une clé de registre donnée et retourne la liste des
    programmes qui y sont déclarés.

    Retourne une liste vide si la clé n'existe pas ou est
    inaccessible, plutôt que de faire planter le programme.
    """

    programs: List[StartupProgram] = []

    try:
        key = winreg.OpenKey(hive, path)
    except OSError:
        return programs

    try:
        index = 0
        while True:
            try:
                name, command, _ = winreg.EnumValue(key, index)
                programs.append(
                    StartupProgram(
                        name=name,
                        command=command,
                        source=source_label,
                    )
                )
                index += 1
            except OSError:
                # Plus de valeurs à lire dans cette clé.
                break
    finally:
        winreg.CloseKey(key)

    return programs


def get_startup_programs() -> List[StartupProgram]:
    """
    Retourne la liste complète des programmes configurés pour
    démarrer automatiquement avec Windows, toutes sources confondues.
    """

    all_programs: List[StartupProgram] = []

    for hive, path, source_label in _STARTUP_LOCATIONS:
        all_programs.extend(
            _read_registry_key(hive, path, source_label)
        )

    return all_programs


# ============================================================
# TEST MANUEL
# ============================================================

if __name__ == "__main__":

    print("=" * 55)
    print("       AVS COMPUTER ASSISTANT")
    print("     PROGRAMMES AU DÉMARRAGE")
    print("=" * 55)

    programs = get_startup_programs()

    print(f"\n{len(programs)} programme(s) trouvé(s) :\n")

    for program in programs:
        print(f"- {program.name} [{program.source}]")
        print(f"  {program.command}\n")

# --- AVS_LINUX_PATCH : versions Linux ---
import sys as _avs_sys
if not _avs_sys.platform.startswith('win'):
    from avs.system import linux_compat as _avs_lc
    get_startup_programs = _avs_lc.get_startup_programs  # AVS_LINUX_PATCH
