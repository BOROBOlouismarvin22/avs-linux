# -*- coding: utf-8 -*-
"""Adapte une COPIE du projet AVS Computer Assistant pour Linux (Ubuntu / WSL).

Usage (depuis le dossier de la copie) :   python patch_linux.py

- Ne touche qu'aux fichiers de avs/system/ de la copie (sauvegarde .orig créée).
- Sans effet sous Windows : les versions Windows restent utilisées.
- Peut être relancé sans risque (déjà patché = ignoré).
"""
import os
import re
import shutil
import sys

RACINE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
SYS_DIR = os.path.join(RACINE, "avs", "system")
MARQUEUR = "AVS_LINUX_PATCH"

LINUX_COMPAT = r'''# -*- coding: utf-8 -*-
"""Sondes AVS pour Linux (Ubuntu / WSL). Renvoie les mêmes résultats que les sondes Windows."""
import glob
import os
import platform
import subprocess

import psutil

GO = 1024 ** 3


def _lire(chemin):
    try:
        with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip() or None
    except OSError:
        return None


def _en_wsl():
    return "microsoft" in platform.release().lower()


def get_cpu_info():
    from avs.system.cpu_probe import CPUResult
    return CPUResult(usage_percent=float(psutil.cpu_percent(interval=0.3)),
                     logical_processors=int(psutil.cpu_count() or 1))


def get_disk_info(drive="/"):
    from avs.system.disk_probe import DiskResult
    u = psutil.disk_usage("/")
    return DiskResult(total_gb=round(u.total / GO, 1), used_gb=round(u.used / GO, 1),
                      free_gb=round(u.free / GO, 1), usage_percent=float(u.percent))


def get_memory_info():
    from avs.system.performance_probe import MemoryResult
    m = psutil.virtual_memory()
    return MemoryResult(total_gb=round(m.total / GO, 1), available_gb=round(m.available / GO, 1),
                        used_gb=round((m.total - m.available) / GO, 1), usage_percent=float(m.percent))


def get_processor_info():
    from avs.system.hardware_info_probe import ProcessorInfo
    nom = None
    texte = _lire("/proc/cpuinfo") or ""
    for ligne in texte.splitlines():
        if ligne.lower().startswith("model name"):
            nom = ligne.split(":", 1)[1].strip()
            break
    return ProcessorInfo(name=nom or platform.processor() or None)


def get_graphics_info():
    from avs.system.hardware_info_probe import GraphicsInfo
    try:
        sortie = subprocess.run(["lspci"], capture_output=True, text=True, timeout=3).stdout
        for ligne in sortie.splitlines():
            if "VGA" in ligne or "3D controller" in ligne or "Display" in ligne:
                return GraphicsInfo(name=ligne.split(":", 2)[-1].strip())
    except (OSError, subprocess.SubprocessError):
        pass
    if os.path.exists("/dev/dxg"):
        return GraphicsInfo(name="Carte graphique virtuelle (WSL)")
    return GraphicsInfo(name=None)


def get_machine_info():
    from avs.system.hardware_info_probe import MachineInfo
    fab = _lire("/sys/class/dmi/id/sys_vendor")
    modele = _lire("/sys/class/dmi/id/product_name")
    if not fab and not modele and _en_wsl():
        fab, modele = "Microsoft", "WSL 2 (machine virtuelle)"
    return MachineInfo(manufacturer=fab, model=modele)


def get_startup_programs():
    from avs.system.startup_probe import StartupProgram
    resultats = []
    sources = [(os.path.expanduser("~/.config/autostart"), "Utilisateur actuel"),
               ("/etc/xdg/autostart", "Toutes les sessions")]
    for dossier, libelle in sources:
        for chemin in sorted(glob.glob(os.path.join(dossier, "*.desktop"))):
            nom, cmd = os.path.basename(chemin), ""
            for ligne in (_lire(chemin) or "").splitlines():
                if ligne.startswith("Name=") and nom == os.path.basename(chemin):
                    nom = ligne[5:].strip()
                elif ligne.startswith("Exec="):
                    cmd = ligne[5:].strip()
            resultats.append(StartupProgram(name=nom, command=cmd, source=libelle))
    return resultats


def get_storage_info(*args, **kwargs):
    from avs.system.storage_probe import StorageResult
    u = psutil.disk_usage("/")
    return StorageResult(drive="/", total_gb=round(u.total / GO, 1), used_gb=round(u.used / GO, 1),
                         free_gb=round(u.free / GO, 1), usage_percent=float(u.percent),
                         disk_type="Virtuel (WSL)" if _en_wsl() else None)
'''

STUB_WINREG = '''try:
    import winreg  # AVS_WINREG_STUB
except ImportError:  # Linux : remplaçant minimal pour que le module se charge
    class _WinregStub:
        def __getattr__(self, nom):
            return 0
    winreg = _WinregStub()
'''

# fichier -> fonctions à remplacer par la version Linux
CIBLES = {
    "cpu_probe.py": ["get_cpu_info"],
    "disk_probe.py": ["get_disk_info"],
    "performance_probe.py": ["get_memory_info"],
    "hardware_info_probe.py": ["get_processor_info", "get_graphics_info", "get_machine_info"],
    "startup_probe.py": ["get_startup_programs"],
    "storage_probe.py": ["get_storage_info"],
}


def patcher(nom, fonctions):
    chemin = os.path.join(SYS_DIR, nom)
    if not os.path.exists(chemin):
        print(f"  ABSENT  {nom}")
        return
    with open(chemin, "r", encoding="utf-8") as f:
        code = f.read()
    if MARQUEUR in code:
        print(f"  déjà fait  {nom}")
        return
    if not os.path.exists(chemin + ".orig"):
        shutil.copy2(chemin, chemin + ".orig")
    code = re.sub(r"^import winreg[ \t]*$", STUB_WINREG.rstrip("\n"), code, flags=re.M)
    bloc = [f"\n\n# --- {MARQUEUR} : versions Linux ---",
            "import sys as _avs_sys",
            "if not _avs_sys.platform.startswith('win'):",
            "    from avs.system import linux_compat as _avs_lc"]
    bloc += [f"    {fn} = _avs_lc.{fn}" for fn in fonctions]
    if MARQUEUR not in code:
        code += "\n".join(bloc) + f"  # {MARQUEUR}\n"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"  patché     {nom}")


def main():
    if not os.path.isdir(SYS_DIR):
        print("ERREUR : dossier avs/system introuvable. Lancez ce script depuis la copie du projet.")
        sys.exit(1)
    print("Projet :", RACINE)
    with open(os.path.join(SYS_DIR, "linux_compat.py"), "w", encoding="utf-8") as f:
        f.write(LINUX_COMPAT)
    print("  créé       linux_compat.py")
    for nom, fonctions in CIBLES.items():
        patcher(nom, fonctions)

    print("\nTest des sondes (sous Linux) :")
    sys.path.insert(0, RACINE)
    tests = [("avs.system.cpu_probe", "get_cpu_info"), ("avs.system.disk_probe", "get_disk_info"),
             ("avs.system.performance_probe", "get_memory_info"),
             ("avs.system.hardware_info_probe", "get_processor_info"),
             ("avs.system.hardware_info_probe", "get_graphics_info"),
             ("avs.system.hardware_info_probe", "get_machine_info"),
             ("avs.system.startup_probe", "get_startup_programs"),
             ("avs.system.storage_probe", "get_storage_info")]
    import importlib
    for module, fonction in tests:
        try:
            r = getattr(importlib.import_module(module), fonction)()
            print(f"  OK   {fonction:22} {r}")
        except Exception as e:
            print(f"  ERREUR {fonction:20} {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
