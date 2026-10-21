# -*- coding: utf-8 -*-
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
