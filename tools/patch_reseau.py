# -*- coding: utf-8 -*-
"""Corrige la sonde réseau AVS pour Linux (ping -n -> ping -c, lecture du résultat Linux).

Usage (depuis la COPIE du projet) :   python patch_reseau.py
Sauvegarde : avs/system/network_probe.py.orig. Relançable sans risque.
"""
import importlib
import os
import shutil
import sys

RACINE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
FICHIER = os.path.join(RACINE, "avs", "system", "network_probe.py")
MARQUEUR = "AVS_LINUX_PATCH_PING"

BLOC = '''

# --- AVS_LINUX_PATCH_PING : ping version Linux ---
import os as _os
import re as _re
import subprocess as _sp
import sys as _sys


def _ping_linux(host: str, count: int = 4, timeout_seconds: int = 5):
    env = dict(_os.environ, LC_ALL="C")
    vide = dict(host=host, success=False, packet_loss_percent=None,
                min_latency_ms=None, max_latency_ms=None, avg_latency_ms=None)
    try:
        result = _sp.run(
            ["ping", "-c", str(count), "-W", str(timeout_seconds), host],
            capture_output=True, text=True, errors="replace",
            timeout=timeout_seconds * count + 2, env=env)
    except _sp.TimeoutExpired:
        return PingResult(raw_output="Timeout : aucune réponse dans le délai imparti.", **vide)
    except FileNotFoundError:
        return PingResult(raw_output="Commande ping introuvable (sudo apt install iputils-ping).", **vide)

    output = result.stdout or ""
    perte = _re.search(r"([\\d.]+)%\\s+packet loss", output)
    packet_loss = float(perte.group(1)) if perte else None
    lat = _re.search(r"=\\s*([\\d.]+)/([\\d.]+)/([\\d.]+)", output)
    mini = float(lat.group(1)) if lat else None
    moy = float(lat.group(2)) if lat else None
    maxi = float(lat.group(3)) if lat else None
    success = result.returncode == 0 and packet_loss is not None and packet_loss < 100
    return PingResult(host=host, success=success, packet_loss_percent=packet_loss,
                      min_latency_ms=mini, max_latency_ms=maxi, avg_latency_ms=moy,
                      raw_output=output)


if not _sys.platform.startswith("win"):
    ping = _ping_linux  # AVS_LINUX_PATCH_PING
'''


def main():
    if not os.path.exists(FICHIER):
        print("ERREUR : avs/system/network_probe.py introuvable. Lancez ce script depuis la copie du projet.")
        sys.exit(1)
    with open(FICHIER, "r", encoding="utf-8") as f:
        code = f.read()
    if MARQUEUR in code:
        print("  déjà fait  network_probe.py")
    else:
        if not os.path.exists(FICHIER + ".orig"):
            shutil.copy2(FICHIER, FICHIER + ".orig")
        with open(FICHIER, "w", encoding="utf-8") as f:
            f.write(code.rstrip("\n") + "\n" + BLOC)
        print("  patché     network_probe.py")

    print("\nTest : ping 1.1.1.1 (2 requêtes)")
    sys.path.insert(0, RACINE)
    try:
        module = importlib.import_module("avs.system.network_probe")
        r = module.ping("1.1.1.1", 2)
        print(f"  réussite={r.success}  perte={r.packet_loss_percent}%  "
              f"min/moy/max={r.min_latency_ms}/{r.avg_latency_ms}/{r.max_latency_ms} ms")
    except Exception as e:
        print(f"  ERREUR {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
