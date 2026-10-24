# -*- coding: utf-8 -*-
"""Sonde réseau détaillée : interfaces, passerelle, serveurs DNS et ports en écoute.

Fonctionne sous Linux (lecture de /proc et /etc) et prévoit une branche Windows
(PowerShell) : la branche Windows n'a pas encore été testée.
"""

import ipaddress
import platform
import socket
import struct
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional

import psutil


@dataclass
class InterfaceInfo:
    """Une interface réseau (carte Ethernet, Wi-Fi, etc.)."""

    name: str
    is_up: bool
    ipv4: Optional[str]
    mac: Optional[str]
    speed_mbps: Optional[int]


@dataclass
class ListeningPort:
    """Un port TCP sur lequel un service attend des connexions."""

    port: int
    address: str
    process: Optional[str]


@dataclass
class NetworkDetails:
    """Résultat complet de la sonde."""

    interfaces: List[InterfaceInfo]
    gateway: Optional[str]
    dns_servers: List[str]
    listening_ports: List[ListeningPort]
    process_info_limited: bool
    environment_note: Optional[str]


def _is_windows() -> bool:
    return sys.platform.startswith("win")


def _powershell(script: str, timeout: int = 8) -> str:
    """Exécute une commande PowerShell et renvoie sa sortie (vide en cas d'échec)."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


# ---------------------------------------------------------
# Analyse de texte (fonctions simples, faciles à tester)
# ---------------------------------------------------------

def parse_proc_net_route(text: str) -> Optional[str]:
    """Trouve l'adresse de la passerelle par défaut dans le contenu de /proc/net/route."""
    best_metric = None
    best_gateway = None

    for line in text.splitlines()[1:]:
        fields = line.split()
        if len(fields) < 8:
            continue
        destination, gateway_hex, flags_hex, metric = fields[1], fields[2], fields[3], fields[6]
        try:
            is_default = destination == "00000000"
            has_gateway = int(flags_hex, 16) & 0x2
            metric_value = int(metric)
            if not (is_default and has_gateway):
                continue
            gateway = socket.inet_ntoa(struct.pack("<L", int(gateway_hex, 16)))
        except (ValueError, struct.error):
            continue
        if best_metric is None or metric_value < best_metric:
            best_metric, best_gateway = metric_value, gateway

    return best_gateway


def parse_resolv_conf(text: str) -> List[str]:
    """Liste les serveurs DNS déclarés dans le contenu de /etc/resolv.conf."""
    servers = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("nameserver"):
            parts = line.split()
            if len(parts) >= 2 and parts[1] not in servers:
                servers.append(parts[1])
    return servers


def _run_command(command: List[str], timeout: int = 8) -> str:
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
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


# ---------------------------------------------------------
# Mesures
# ---------------------------------------------------------

def get_interfaces() -> List[InterfaceInfo]:
    """Liste les interfaces réseau (sans 'lo'), les interfaces actives d'abord."""
    stats = psutil.net_if_stats()
    interfaces = []

    for name, addresses in psutil.net_if_addrs().items():
        ipv4 = None
        mac = None
        for address in addresses:
            if address.family == socket.AF_INET and ipv4 is None:
                ipv4 = address.address
            elif address.family == psutil.AF_LINK and mac is None:
                mac = address.address

        if name == "lo" or (ipv4 and ipv4.startswith("127.")):
            continue

        info = stats.get(name)
        is_up = bool(info.isup) if info else False
        if not is_up and (ipv4 is None or ipv4.startswith("169.254.")):
            continue
        speed = info.speed if info and 0 < info.speed != 4294 else None
        interfaces.append(
            InterfaceInfo(
                name=name,
                is_up=bool(info.isup) if info else False,
                ipv4=ipv4,
                mac=mac,
                speed_mbps=speed,
            )
        )

    return sorted(interfaces, key=lambda item: (not item.is_up, item.name))


def get_gateway() -> Optional[str]:
    """Adresse de la passerelle par défaut (le routeur), ou None si elle est introuvable."""
    if _is_windows():
        gateway = parse_route_print(_run_command(["route", "print", "-4"], timeout=15))
        if gateway:
            return gateway
        output = _powershell(
            "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | "
            "Sort-Object RouteMetric | Select-Object -First 1).NextHop",
            timeout=25,
        )
        return output.splitlines()[0].strip() if output else None
    return parse_proc_net_route(_read_text("/proc/net/route"))


def get_dns_servers() -> List[str]:
    """Serveurs DNS utilisés par la machine."""
    if _is_windows():
        output = _powershell(
            "Get-DnsClientServerAddress -AddressFamily IPv4 | "
            "ForEach-Object { $_.ServerAddresses }"
        )
        servers = []
        for line in output.splitlines():
            line = line.strip()
            if line and line not in servers:
                servers.append(line)
        return servers
    return parse_resolv_conf(_read_text("/etc/resolv.conf"))


def get_listening_ports():
    """Ports TCP en écoute. Renvoie (liste de ports, informations_limitées)."""
    try:
        connections = psutil.net_connections(kind="tcp")
    except (psutil.AccessDenied, PermissionError, OSError):
        return [], True

    ports = {}
    limited = False

    for connection in connections:
        if connection.status != psutil.CONN_LISTEN or not connection.laddr:
            continue

        process_name = None
        if connection.pid:
            try:
                process_name = psutil.Process(connection.pid).name()
            except (psutil.Error, OSError):
                limited = True
        else:
            limited = True

        key = (connection.laddr.port, connection.laddr.ip)
        if key not in ports or (ports[key].process is None and process_name):
            ports[key] = ListeningPort(
                port=connection.laddr.port,
                address=connection.laddr.ip,
                process=process_name,
            )

    return sorted(ports.values(), key=lambda item: (item.port, item.address)), limited


def get_network_details() -> NetworkDetails:
    """Rassemble toutes les informations réseau détaillées."""
    ports, limited = get_listening_ports()

    note = None
    if "microsoft" in platform.release().lower():
        note = (
            "Linux tourne ici dans une machine virtuelle (WSL 2) : ces informations "
            "décrivent le réseau d'Ubuntu, pas celui de Windows."
        )

    return NetworkDetails(
        interfaces=get_interfaces(),
        gateway=get_gateway(),
        dns_servers=get_dns_servers(),
        listening_ports=ports,
        process_info_limited=limited,
        environment_note=note,
    )
