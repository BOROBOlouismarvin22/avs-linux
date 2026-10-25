# -*- coding: utf-8 -*-
"""Tests de la sonde réseau détaillée : analyse de texte, filtrage des interfaces, ports, résultat complet."""

import os
import socket
from collections import namedtuple

import psutil

from avs.system import network_details_probe as probe

ROUTE_LINUX = (
    "Iface\tDestination\tGateway\tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"
    "eth0\t00000000\t01A016AC\t0003\t0\t0\t0\t00000000\t0\t0\t0\n"
    "eth0\t00A016AC\t00000000\t0001\t0\t0\t0\t00F0FFFF\t0\t0\t0\n"
)

ROUTE_PRINT_EN = (
    "IPv4 Route Table\n"
    "Active Routes:\n"
    "Network Destination        Netmask          Gateway       Interface  Metric\n"
    "          0.0.0.0          0.0.0.0      192.168.1.254     192.168.1.74     50\n"
    "          0.0.0.0          0.0.0.0          On-link       172.16.0.2    5\n"
    "        127.0.0.0        255.0.0.0         On-link         127.0.0.1    331\n"
)

ROUTE_PRINT_FR = (
    "Itinéraires actifs :\n"
    "Destination réseau    Masque réseau  Adr. passerelle   Adr. interface Métrique\n"
    "          0.0.0.0          0.0.0.0    Sur courte distance    172.16.0.2     5\n"
    "          0.0.0.0          0.0.0.0      192.168.1.254     192.168.1.74     50\n"
    "          0.0.0.0          0.0.0.0      10.5.0.1       10.5.0.2      80\n"
)

Addr = namedtuple("snicaddr", "family address netmask broadcast ptp")
Stats = namedtuple("snicstats", "isup duplex speed mtu flags")
Local = namedtuple("addr", "ip port")
Conn = namedtuple("sconn", "fd family type laddr raddr status pid")


# ---------------------------------------------------------
# Analyse de texte
# ---------------------------------------------------------

def test_passerelle_linux_est_trouvee():
    assert probe.parse_proc_net_route(ROUTE_LINUX) == "172.22.160.1"


def test_passerelle_linux_sans_route_par_defaut():
    assert probe.parse_proc_net_route(ROUTE_LINUX.splitlines()[0] + "\n") is None


def test_passerelle_linux_garde_la_route_la_plus_prioritaire():
    texte = (
        ROUTE_LINUX.splitlines()[0] + "\n"
        "eth0\t00000000\t0101A8C0\t0003\t0\t0\t100\t00000000\t0\t0\t0\n"
        "wlan0\t00000000\t0100000A\t0003\t0\t0\t10\t00000000\t0\t0\t0\n"
    )
    assert probe.parse_proc_net_route(texte) == "10.0.0.1"


def test_passerelle_linux_ignore_les_lignes_illisibles():
    assert probe.parse_proc_net_route("entete\nligne trop courte\nxx\n") is None


def test_dns_resolv_conf_supprime_les_doublons():
    texte = "# commentaire\nnameserver 10.255.255.254\nnameserver 10.255.255.254\nnameserver 1.1.1.1\nsearch lan\n"
    assert probe.parse_resolv_conf(texte) == ["10.255.255.254", "1.1.1.1"]


def test_dns_resolv_conf_vide():
    assert probe.parse_resolv_conf("") == []


def test_route_print_anglais_et_francais():
    assert probe.parse_route_print(ROUTE_PRINT_EN) == "192.168.1.254"
    assert probe.parse_route_print(ROUTE_PRINT_FR) == "192.168.1.254"


def test_route_print_vide():
    assert probe.parse_route_print("") is None


# ---------------------------------------------------------
# Interfaces
# ---------------------------------------------------------

def test_interfaces_filtrage_tri_et_vitesse(monkeypatch):
    af_inet = socket.AF_INET
    monkeypatch.setattr(psutil, "net_if_addrs", lambda: {
        "lo": [Addr(af_inet, "127.0.0.1", None, None, None)],
        "eth0": [Addr(af_inet, "192.168.1.5", None, None, None), Addr(psutil.AF_LINK, "aa:bb:cc:dd:ee:ff", None, None, None)],
        "virt": [Addr(af_inet, "172.16.0.2", None, None, None)],
        "vpn": [Addr(af_inet, "10.5.0.2", None, None, None)],
        "apipa": [Addr(af_inet, "169.254.1.1", None, None, None)],
        "sansip": [Addr(psutil.AF_LINK, "11:22:33:44:55:66", None, None, None)],
    })
    monkeypatch.setattr(psutil, "net_if_stats", lambda: {
        "lo": Stats(True, 0, 0, 65536, ""),
        "eth0": Stats(True, 2, 1000, 1500, ""),
        "virt": Stats(True, 0, 4294, 1500, ""),
        "vpn": Stats(False, 0, 0, 1500, ""),
        "apipa": Stats(False, 0, 1000, 1500, ""),
        "sansip": Stats(False, 0, 0, 1500, ""),
    })

    resultat = probe.get_interfaces()
    noms = [i.name for i in resultat]

    assert noms == ["eth0", "virt", "vpn"]  # actives d'abord ; lo, apipa inactive et interface sans IP écartées
    par_nom = {i.name: i for i in resultat}
    assert par_nom["eth0"].speed_mbps == 1000
    assert par_nom["eth0"].mac == "aa:bb:cc:dd:ee:ff"
    assert par_nom["virt"].speed_mbps is None  # 4294 = vitesse inconnue
    assert par_nom["vpn"].is_up is False and par_nom["vpn"].ipv4 == "10.5.0.2"


# ---------------------------------------------------------
# Ports en écoute
# ---------------------------------------------------------

def test_ports_en_ecoute_dedoublonnes_et_limites(monkeypatch):
    mon_pid = os.getpid()
    monkeypatch.setattr(psutil, "net_connections", lambda kind="tcp": [
        Conn(-1, socket.AF_INET, socket.SOCK_STREAM, Local("0.0.0.0", 8080), (), psutil.CONN_LISTEN, mon_pid),
        Conn(-1, socket.AF_INET, socket.SOCK_STREAM, Local("0.0.0.0", 8080), (), psutil.CONN_LISTEN, None),
        Conn(-1, socket.AF_INET, socket.SOCK_STREAM, Local("127.0.0.53", 53), (), psutil.CONN_LISTEN, None),
        Conn(-1, socket.AF_INET, socket.SOCK_STREAM, Local("10.0.0.2", 40000), ("1.2.3.4", 443), psutil.CONN_ESTABLISHED, mon_pid),
    ])

    ports, limite = probe.get_listening_ports()

    assert [(p.port, p.address) for p in ports] == [(53, "127.0.0.53"), (8080, "0.0.0.0")]
    assert ports[1].process is not None  # le doublon sans nom ne remplace pas la version identifiée
    assert ports[0].process is None
    assert limite is True


def test_ports_en_ecoute_acces_refuse(monkeypatch):
    def refuse(kind="tcp"):
        raise psutil.AccessDenied()

    monkeypatch.setattr(psutil, "net_connections", refuse)
    assert probe.get_listening_ports() == ([], True)


# ---------------------------------------------------------
# Windows (logique simulée) et résultat complet
# ---------------------------------------------------------

def test_passerelle_windows_via_route_print(monkeypatch):
    monkeypatch.setattr(probe, "_is_windows", lambda: True)
    monkeypatch.setattr(probe, "_run_command", lambda command, timeout=8: ROUTE_PRINT_FR)
    assert probe.get_gateway() == "192.168.1.254"


def test_passerelle_windows_repli_powershell(monkeypatch):
    monkeypatch.setattr(probe, "_is_windows", lambda: True)
    monkeypatch.setattr(probe, "_run_command", lambda command, timeout=8: "")
    monkeypatch.setattr(probe, "_powershell", lambda script, timeout=8: "192.168.1.254\r\n")
    assert probe.get_gateway() == "192.168.1.254"


def test_passerelle_windows_introuvable(monkeypatch):
    monkeypatch.setattr(probe, "_is_windows", lambda: True)
    monkeypatch.setattr(probe, "_run_command", lambda command, timeout=8: "")
    monkeypatch.setattr(probe, "_powershell", lambda script, timeout=8: "")
    assert probe.get_gateway() is None


def test_dns_windows_sans_doublons(monkeypatch):
    monkeypatch.setattr(probe, "_is_windows", lambda: True)
    monkeypatch.setattr(probe, "_powershell", lambda script, timeout=8: "127.0.2.2\r\n127.0.2.3\r\n127.0.2.2\r\n")
    assert probe.get_dns_servers() == ["127.0.2.2", "127.0.2.3"]


def test_resultat_complet_avec_note_wsl(monkeypatch):
    monkeypatch.setattr(probe, "get_interfaces", lambda: [])
    monkeypatch.setattr(probe, "get_gateway", lambda: "172.22.160.1")
    monkeypatch.setattr(probe, "get_dns_servers", lambda: ["10.255.255.254"])
    monkeypatch.setattr(probe, "get_listening_ports", lambda: ([], False))
    monkeypatch.setattr(probe.platform, "release", lambda: "6.18.54.1-microsoft-standard-WSL2")

    details = probe.get_network_details()

    assert details.gateway == "172.22.160.1"
    assert details.dns_servers == ["10.255.255.254"]
    assert details.process_info_limited is False
    assert "WSL 2" in details.environment_note


def test_resultat_complet_sans_note_hors_wsl(monkeypatch):
    monkeypatch.setattr(probe, "get_interfaces", lambda: [])
    monkeypatch.setattr(probe, "get_gateway", lambda: None)
    monkeypatch.setattr(probe, "get_dns_servers", lambda: [])
    monkeypatch.setattr(probe, "get_listening_ports", lambda: ([], True))
    monkeypatch.setattr(probe.platform, "release", lambda: "6.8.0-generic")

    details = probe.get_network_details()

    assert details.gateway is None and details.dns_servers == []
    assert details.environment_note is None
