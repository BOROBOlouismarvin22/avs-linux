# -*- coding: utf-8 -*-
"""Corrige la sonde réseau détaillée (passerelle sous Windows, vitesse inconnue, interfaces inactives).

Usage (depuis la racine du projet) :   python tools/patch_sonde_windows.py
Sauvegarde : avs/system/network_details_probe.py.avant_correctif. Relançable sans risque.
"""
import os
import shutil
import sys

RACINE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
FICHIER = os.path.join(RACINE, "avs", "system", "network_details_probe.py")
MARQUEUR = "def parse_route_print"

REMPLACEMENTS = [
    (
        "imports",
        "import platform\nimport socket\n",
        "import ipaddress\nimport platform\nimport socket\n",
    ),
    (
        "fonctions",
        "def _read_text(path: str) -> str:\n",
        '''def _run_command(command: List[str], timeout: int = 8) -> str:
    """Exécute une commande et renvoie sa sortie (vide en cas d'échec)."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def parse_route_print(text: str) -> Optional[str]:
    """Trouve la passerelle par défaut dans la sortie de « route print -4 » (Windows)."""
    best_metric = None
    best_gateway = None

    for line in text.splitlines():
        fields = line.split()
        if len(fields) < 5 or fields[0] != "0.0.0.0" or fields[1] != "0.0.0.0":
            continue
        try:
            ipaddress.IPv4Address(fields[2])
            metric_value = int(fields[4])
        except ValueError:
            continue
        if best_metric is None or metric_value < best_metric:
            best_metric, best_gateway = metric_value, fields[2]

    return best_gateway


def _read_text(path: str) -> str:
''',
    ),
    (
        "passerelle",
        '''    if _is_windows():
        output = _powershell(
            "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | "
            "Sort-Object RouteMetric | Select-Object -First 1).NextHop"
        )
        return output.splitlines()[0].strip() if output else None
''',
        '''    if _is_windows():
        gateway = parse_route_print(_run_command(["route", "print", "-4"], timeout=15))
        if gateway:
            return gateway
        output = _powershell(
            "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | "
            "Sort-Object RouteMetric | Select-Object -First 1).NextHop",
            timeout=25,
        )
        return output.splitlines()[0].strip() if output else None
''',
    ),
    (
        "interfaces",
        '''        info = stats.get(name)
        speed = info.speed if info and info.speed > 0 else None
''',
        '''        info = stats.get(name)
        is_up = bool(info.isup) if info else False
        if not is_up and (ipv4 is None or ipv4.startswith("169.254.")):
            continue
        speed = info.speed if info and 0 < info.speed != 4294 else None
''',
    ),
]


def main():
    if not os.path.exists(FICHIER):
        print("ERREUR : avs/system/network_details_probe.py introuvable. Lancez ce script depuis la racine du projet.")
        sys.exit(1)
    with open(FICHIER, "r", encoding="utf-8") as f:
        code = f.read()
    if MARQUEUR in code:
        print("  déjà fait  network_details_probe.py")
        return
    for nom, ancien, _ in REMPLACEMENTS:
        if code.count(ancien) != 1:
            print("ERREUR : repère « " + nom + " » introuvable ou en double. Rien n'a été modifié.")
            sys.exit(1)
    if not os.path.exists(FICHIER + ".avant_correctif"):
        shutil.copy2(FICHIER, FICHIER + ".avant_correctif")
    for _, ancien, nouveau in REMPLACEMENTS:
        code = code.replace(ancien, nouveau)
    with open(FICHIER, "w", encoding="utf-8") as f:
        f.write(code)
    print("  corrigé    network_details_probe.py (passerelle Windows, vitesse, interfaces)")


if __name__ == "__main__":
    main()

