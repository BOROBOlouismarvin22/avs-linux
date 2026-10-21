"""
network_probe.py

Couche système de AVS Computer Assistant.

Ce module effectue des mesures réseau brutes :
- test de connectivité avec ping
- mesure de perte de paquets
- mesure de latence
- résolution DNS

Il ne prend pas encore de décision de diagnostic.
"""

import re
import socket
import subprocess
from dataclasses import dataclass
from typing import Optional


# ============================================================
# RÉSULTAT DU PING
# ============================================================

@dataclass
class PingResult:
    """Contient les données brutes et mesurées d'un test de ping."""

    host: str
    success: bool

    packet_loss_percent: Optional[float]

    min_latency_ms: Optional[float]
    max_latency_ms: Optional[float]
    avg_latency_ms: Optional[float]

    raw_output: str


# ============================================================
# RÉSULTAT DNS
# ============================================================

@dataclass
class DnsResult:
    """Contient le résultat d'une résolution DNS."""

    hostname: str
    success: bool

    ip_address: Optional[str]

    error_message: Optional[str]


# ============================================================
# TEST DE PING
# ============================================================

def ping(host: str, count: int = 4, timeout_seconds: int = 5) -> PingResult:
    """
    Effectue un ping vers une adresse IP ou un nom de domaine.

    Exemple :
        ping("1.1.1.1")

    Si l'hôte ne répond pas dans le délai imparti (timeout_seconds
    par requête, count requêtes au total), retourne un PingResult
    avec success=False plutôt que de bloquer le programme.

    Retourne un objet PingResult contenant :
    - réussite ou échec
    - perte de paquets
    - latence minimale
    - latence maximale
    - latence moyenne
    - sortie brute de Windows
    """

    try:
        result = subprocess.run(
            ["ping", "-n", str(count), host],
            capture_output=True,
            text=True,
            encoding="cp850",
            errors="replace",
            timeout=timeout_seconds * count
        )
    except subprocess.TimeoutExpired:
        return PingResult(
            host=host,
            success=False,
            packet_loss_percent=None,
            min_latency_ms=None,
            max_latency_ms=None,
            avg_latency_ms=None,
            raw_output="Timeout : aucune réponse dans le délai imparti."
        )

    output = result.stdout

    # --------------------------------------------------------
    # Extraction de la perte de paquets
    # --------------------------------------------------------

    loss_match = re.search(
        r"perte\s+(\d+)%|loss\s+(\d+)%",
        output,
        re.IGNORECASE
    )

    packet_loss = None

    if loss_match:
        value = loss_match.group(1) or loss_match.group(2)
        packet_loss = float(value)

    # --------------------------------------------------------
    # Extraction des latences
    # --------------------------------------------------------

    latency_match = re.search(
        r"Minimum\s*=\s*(\d+)ms,\s*Maximum\s*=\s*(\d+)ms,\s*Moyenne\s*=\s*(\d+)ms",
        output,
        re.IGNORECASE
    )

    min_latency = None
    max_latency = None
    avg_latency = None

    if latency_match:
        min_latency = float(latency_match.group(1))
        max_latency = float(latency_match.group(2))
        avg_latency = float(latency_match.group(3))

    # --------------------------------------------------------
    # Détermination de la réussite du ping
    # --------------------------------------------------------

    success = (
        result.returncode == 0
        and packet_loss is not None
        and packet_loss < 100
    )

    return PingResult(
        host=host,
        success=success,
        packet_loss_percent=packet_loss,
        min_latency_ms=min_latency,
        max_latency_ms=max_latency,
        avg_latency_ms=avg_latency,
        raw_output=output
    )


# ============================================================
# RÉSOLUTION DNS
# ============================================================

def resolve_dns(hostname: str, timeout_seconds: float = 3) -> DnsResult:
    """
    Tente de convertir un nom de domaine en adresse IP.

    Applique un délai maximal pour éviter un blocage si le DNS
    ne répond jamais.

    Exemple :
        resolve_dns("google.com")
    """

    ancien_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout_seconds)

    try:

        ip_address = socket.gethostbyname(hostname)

        return DnsResult(
            hostname=hostname,
            success=True,
            ip_address=ip_address,
            error_message=None
        )

    except socket.gaierror as error:

        return DnsResult(
            hostname=hostname,
            success=False,
            ip_address=None,
            error_message=str(error)
        )

    except socket.timeout:

        return DnsResult(
            hostname=hostname,
            success=False,
            ip_address=None,
            error_message="Timeout : le serveur DNS n'a pas répondu à temps."
        )

    finally:
        socket.setdefaulttimeout(ancien_timeout)


# ============================================================
# TEST MANUEL
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("       AVS COMPUTER ASSISTANT")
    print("          DIAGNOSTIC RÉSEAU")
    print("=" * 50)

    # --------------------------------------------------------
    # TEST 1 : CONNECTIVITÉ IP
    # --------------------------------------------------------

    print("\n=== TEST 1 : CONNECTIVITÉ IP ===")

    result = ping("1.1.1.1")

    print(f"Hôte : {result.host}")
    print(f"Connexion réussie : {result.success}")

    print(f"Perte de paquets : {result.packet_loss_percent}%")

    print(f"Latence minimale : {result.min_latency_ms} ms")
    print(f"Latence maximale : {result.max_latency_ms} ms")
    print(f"Latence moyenne : {result.avg_latency_ms} ms")

    # --------------------------------------------------------
    # TEST 2 : RÉSOLUTION DNS
    # --------------------------------------------------------

    print("\n=== TEST 2 : RÉSOLUTION DNS ===")

    dns_result = resolve_dns("google.com")

    print(f"Domaine : {dns_result.hostname}")
    print(f"Résolution réussie : {dns_result.success}")
    print(f"Adresse IP : {dns_result.ip_address}")
    print(f"Erreur : {dns_result.error_message}")

    # --------------------------------------------------------
    # RÉSULTAT BRUT DU PING
    # --------------------------------------------------------

    print("\n=== TEST 2 : RÉSULTAT BRUT DU PING ===")

    print(result.raw_output)


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
    perte = _re.search(r"([\d.]+)%\s+packet loss", output)
    packet_loss = float(perte.group(1)) if perte else None
    lat = _re.search(r"=\s*([\d.]+)/([\d.]+)/([\d.]+)", output)
    mini = float(lat.group(1)) if lat else None
    moy = float(lat.group(2)) if lat else None
    maxi = float(lat.group(3)) if lat else None
    success = result.returncode == 0 and packet_loss is not None and packet_loss < 100
    return PingResult(host=host, success=success, packet_loss_percent=packet_loss,
                      min_latency_ms=mini, max_latency_ms=maxi, avg_latency_ms=moy,
                      raw_output=output)


if not _sys.platform.startswith("win"):
    ping = _ping_linux  # AVS_LINUX_PATCH_PING
