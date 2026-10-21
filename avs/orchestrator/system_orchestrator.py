# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT
======================

SYSTEM ORCHESTRATOR

L'orchestrateur centralise les informations provenant
des différentes couches du système :

1. PROBES
   - RAM
   - CPU
   - Stockage logique
   - Disque physique
   - Batterie
   - Processus
   - Réseau
   - Programmes au démarrage

2. DIAGNOSTICS
   - Diagnostic RAM
   - Diagnostic CPU
   - Diagnostic stockage
   - Diagnostic processus
   - Diagnostic réseau
   - Diagnostic démarrage

3. ANALYSE DES CAUSES
   - Causes probables
   - Éléments observés
   - Recommandations
   - Priorité

4. MOTEUR D'ACTIONS
   - Actions concrètes
   - Priorité des actions
   - Statut global

L'orchestrateur ne remplace pas les modules spécialisés.
Il les coordonne afin de produire un rapport système complet.

Note : le diagnostic réseau et le diagnostic des programmes au
démarrage sont calculés et inclus dans le rapport, mais n'alimentent
pas encore l'analyse des causes ni le moteur d'actions
(analyze_causes / decide_action). Cette intégration plus profonde
sera traitée dans une étape ultérieure, une fois ces deux modules
audités.
"""

from dataclasses import asdict


# =========================================================
# PROBES SYSTEME
# =========================================================

from avs.system.performance_probe import get_memory_info
from avs.system.cpu_probe import get_cpu_info
from avs.system.disk_probe import get_disk_info
from avs.system.storage_probe import get_storage_info
from avs.system.battery_probe import get_battery_info
from avs.system.process_probe import get_process_info
from avs.system.network_probe import ping, resolve_dns
from avs.system.startup_probe import get_startup_programs


# =========================================================
# DIAGNOSTICS
# =========================================================

from avs.diagnostics.performance_diagnostic import diagnose_ram
from avs.diagnostics.cpu_diagnostic import diagnose_cpu
from avs.diagnostics.disk_diagnostic import diagnose_disk
from avs.diagnostics.process_diagnostic import diagnose_processes
from avs.diagnostics.network_diagnostic import analyze_network
from avs.diagnostics.startup_diagnostic import diagnose_startup


# =========================================================
# ANALYSE DES CAUSES
# =========================================================

from avs.diagnostics.cause_analyzer import analyze_causes


# =========================================================
# MOTEUR D'ACTIONS
# =========================================================

from avs.decision.action_engine import decide_action


# =========================================================
# DIAGNOSTIC GLOBAL
# =========================================================

def run_system_diagnostic():
    """
    Exécute l'analyse complète du système.

    Retourne un rapport contenant :

    - RAM
    - CPU
    - stockage logique
    - disque physique
    - batterie
    - processus
    - réseau
    - programmes au démarrage
    - causes probables
    - recommandations
    - actions
    """

    # =====================================================
    # 1. RAM
    # =====================================================

    memory = get_memory_info()

    ram_diagnostic = diagnose_ram(
        memory.total_gb,
        memory.used_gb,
        memory.usage_percent,
    )

    # =====================================================
    # 2. CPU
    # =====================================================

    cpu = get_cpu_info()

    cpu_diagnostic = diagnose_cpu(
        cpu.usage_percent,
        cpu.logical_processors,
    )

    # =====================================================
    # 3. STOCKAGE LOGIQUE
    # =====================================================

    disk = get_disk_info()

    disk_diagnostic = diagnose_disk(
        disk.total_gb,
        disk.used_gb,
        disk.free_gb,
        disk.usage_percent,
    )

    # =====================================================
    # 4. DISQUE PHYSIQUE
    # =====================================================

    physical_disk = get_storage_info()

    # =====================================================
    # 5. BATTERIE
    # =====================================================

    battery = get_battery_info()

    # =====================================================
    # 6. PROCESSUS
    # =====================================================

    processes = get_process_info(
        limit=10
    )

    process_diagnostics = diagnose_processes(
        processes
    )

    # =====================================================
    # 6.5 RÉSEAU
    # =====================================================

    ping_result = ping("1.1.1.1")
    dns_result = resolve_dns("google.com")

    network_diagnostic = analyze_network(
        ping_result,
        dns_result,
    )

    # =====================================================
    # 6.6 PROGRAMMES AU DÉMARRAGE
    # =====================================================

    startup_programs = get_startup_programs()
    startup_diagnostic = diagnose_startup(startup_programs)

    # =====================================================
    # 7. ANALYSE DES CAUSES
    # =====================================================

    cause_analysis = analyze_causes(
        ram_diagnostic,
        cpu_diagnostic,
        disk_diagnostic,
        process_diagnostics,
    )

    # =====================================================
    # 8. MOTEUR D'ACTIONS
    # =====================================================

    action_result = decide_action(
        ram_diagnostic,
        cpu_diagnostic,
        disk_diagnostic,
        process_diagnostics,
        cause_analysis,
    )

    # =====================================================
    # 9. RAPPORT COMPLET
    # =====================================================

    return {

        # -------------------------------------------------
        # RAM
        # -------------------------------------------------

        "ram": {
            "measurement": {
                "total_gb": memory.total_gb,
                "used_gb": memory.used_gb,
                "available_gb": memory.available_gb,
                "usage_percent": memory.usage_percent,
            },

            "diagnostic": ram_diagnostic,
        },

        # -------------------------------------------------
        # CPU
        # -------------------------------------------------

        "cpu": {
            "measurement": {
                "usage_percent": cpu.usage_percent,
                "logical_processors": cpu.logical_processors,
            },

            "diagnostic": cpu_diagnostic,
        },

        # -------------------------------------------------
        # STOCKAGE LOGIQUE
        # -------------------------------------------------

        "disk": {
            "measurement": {
                "total_gb": disk.total_gb,
                "used_gb": disk.used_gb,
                "free_gb": disk.free_gb,
                "usage_percent": disk.usage_percent,
            },

            "diagnostic": disk_diagnostic,
        },

        # -------------------------------------------------
        # DISQUE PHYSIQUE
        # -------------------------------------------------

        "physical_disk": asdict(
            physical_disk
        ),

        # -------------------------------------------------
        # BATTERIE
        # -------------------------------------------------

        "battery": battery,

        # -------------------------------------------------
        # PROCESSUS
        # -------------------------------------------------

        "processes": {
            "count": len(process_diagnostics),
            "diagnostics": process_diagnostics,
        },

        # -------------------------------------------------
        # RÉSEAU
        # -------------------------------------------------

        "network": {
            "ping": {
                "host": ping_result.host,
                "success": ping_result.success,
                "packet_loss_percent": ping_result.packet_loss_percent,
                "min_latency_ms": ping_result.min_latency_ms,
                "max_latency_ms": ping_result.max_latency_ms,
                "avg_latency_ms": ping_result.avg_latency_ms,
            },
            "dns": {
                "hostname": dns_result.hostname,
                "success": dns_result.success,
                "ip_address": dns_result.ip_address,
            },
            "diagnostic": {
                "status": network_diagnostic.status,
                "title": network_diagnostic.title,
                "message": network_diagnostic.message,
                "recommendation": network_diagnostic.recommendation,
            },
        },

        # -------------------------------------------------
        # PROGRAMMES AU DÉMARRAGE
        # -------------------------------------------------

        "startup": startup_diagnostic,

        # -------------------------------------------------
        # CAUSES
        # -------------------------------------------------

        "causes": cause_analysis,

        # -------------------------------------------------
        # ACTIONS
        # -------------------------------------------------

        "actions": action_result,
    }


# =========================================================
# AFFICHAGE TERMINAL
# =========================================================

def display_system_report(report):
    """Affiche le rapport complet du système dans le terminal."""

    print("=" * 75)
    print("                 AVS COMPUTER ASSISTANT")
    print("                   DIAGNOSTIC GLOBAL")
    print("=" * 75)

    # =====================================================
    # RAM
    # =====================================================

    ram = report["ram"]

    print()
    print("MEMOIRE RAM")
    print("-" * 75)

    print(
        f"RAM totale          : "
        f"{ram['measurement']['total_gb']} Go"
    )

    print(
        f"RAM utilisee        : "
        f"{ram['measurement']['used_gb']} Go"
    )

    print(
        f"RAM disponible      : "
        f"{ram['measurement']['available_gb']} Go"
    )

    print(
        f"Utilisation         : "
        f"{ram['measurement']['usage_percent']}%"
    )

    print(
        f"Statut utilisation  : "
        f"{ram['diagnostic']['usage_status']}"
    )

    print(
        f"Statut capacite     : "
        f"{ram['diagnostic']['capacity_status']}"
    )

    # =====================================================
    # CPU
    # =====================================================

    cpu = report["cpu"]

    print()
    print("CPU")
    print("-" * 75)

    print(
        f"Utilisation         : "
        f"{cpu['measurement']['usage_percent']}%"
    )

    print(
        f"Processeurs         : "
        f"{cpu['measurement']['logical_processors']}"
    )

    print(
        f"Statut utilisation  : "
        f"{cpu['diagnostic']['usage_status']}"
    )

    print(
        f"Statut processeurs  : "
        f"{cpu['diagnostic']['processor_status']}"
    )

    # =====================================================
    # STOCKAGE LOGIQUE
    # =====================================================

    disk = report["disk"]

    print()
    print("STOCKAGE")
    print("-" * 75)

    print(
        f"Capacite totale     : "
        f"{disk['measurement']['total_gb']} Go"
    )

    print(
        f"Espace utilise      : "
        f"{disk['measurement']['used_gb']} Go"
    )

    print(
        f"Espace libre        : "
        f"{disk['measurement']['free_gb']} Go"
    )

    print(
        f"Utilisation         : "
        f"{disk['measurement']['usage_percent']}%"
    )

    print(
        f"Statut utilisation  : "
        f"{disk['diagnostic']['usage_status']}"
    )

    free_space_status = disk["diagnostic"].get(
        "free_space_status",
        disk["diagnostic"].get(
            "free_status",
            "N/A",
        ),
    )

    print(
        f"Statut espace libre : "
        f"{free_space_status}"
    )

    # =====================================================
    # DISQUE PHYSIQUE
    # =====================================================

    physical_disk = report["physical_disk"]

    print()
    print("DISQUE PHYSIQUE")
    print("-" * 75)

    print(
        f"Numero disque       : "
        f"{physical_disk.get('disk_number', 'N/A')}"
    )

    print(
        f"Fabricant           : "
        f"{physical_disk.get('manufacturer') or 'N/A'}"
    )

    print(
        f"Modele              : "
        f"{physical_disk.get('model') or 'N/A'}"
    )

    print(
        f"Type                : "
        f"{physical_disk.get('disk_type') or 'N/A'}"
    )

    print(
        f"Interface           : "
        f"{physical_disk.get('interface') or 'N/A'}"
    )

    print(
        f"Capacite physique   : "
        f"{physical_disk.get('physical_size_gb') or 'N/A'} Go"
    )

    print(
        f"Sante               : "
        f"{physical_disk.get('health_status') or 'N/A'}"
    )

    print(
        f"Etat operationnel   : "
        f"{physical_disk.get('operational_status') or 'N/A'}"
    )

    print(
        f"Partition           : "
        f"{physical_disk.get('partition_style') or 'N/A'}"
    )

    # =====================================================
    # BATTERIE
    # =====================================================

    battery = report["battery"]

    print()
    print("BATTERIE")
    print("-" * 75)

    if battery.get("present"):

        charge = battery.get(
            "charge_percent"
        )

        power_source = battery.get(
            "power_source",
            "N/A",
        )

        status = battery.get(
            "status",
            "N/A",
        )

        health = battery.get(
            "health_percent"
        )

        health_status = battery.get(
            "health_status",
            "N/A",
        )

        design_capacity = battery.get(
            "design_capacity_mwh"
        )

        full_capacity = battery.get(
            "full_charge_capacity_mwh"
        )

        print(
            f"Charge actuelle    : "
            f"{charge if charge is not None else 'N/A'}%"
        )

        print(
            f"Alimentation       : "
            f"{power_source}"
        )

        print(
            f"Etat               : "
            f"{status}"
        )

        print(
            f"Capacite conception: "
            f"{design_capacity if design_capacity is not None else 'N/A'} mWh"
        )

        print(
            f"Capacite maximale  : "
            f"{full_capacity if full_capacity is not None else 'N/A'} mWh"
        )

        print(
            f"Sante estimee      : "
            f"{health if health is not None else 'N/A'}%"
        )

        print(
            f"Etat de sante      : "
            f"{health_status}"
        )

    else:

        print(
            "Aucune batterie detectee."
        )

    # =====================================================
    # PROCESSUS
    # =====================================================

    processes = report["processes"]

    print()
    print("PROCESSUS PRINCIPAUX")
    print("-" * 75)

    print(
        f"Processus analyses  : "
        f"{processes['count']}"
    )

    for process in processes["diagnostics"]:

        print(
            f"{process['name']:<30} "
            f"RAM : {process['memory_mb']:>8.2f} MB | "
            f"CPU : {process['cpu_percent']:>6.2f}% | "
            f"Statut : {process['status']}"
        )

    # =====================================================
    # RÉSEAU
    # =====================================================

    network = report["network"]

    print()
    print("RESEAU")
    print("-" * 75)

    print(
        f"Connexion (ping)    : "
        f"{'OK' if network['ping']['success'] else 'ECHEC'}"
    )

    print(
        f"Resolution DNS      : "
        f"{'OK' if network['dns']['success'] else 'ECHEC'}"
    )

    print(
        f"Statut diagnostic   : "
        f"{network['diagnostic']['status']}"
    )

    print(
        f"{network['diagnostic']['message']}"
    )

    # =====================================================
    # PROGRAMMES AU DEMARRAGE
    # =====================================================

    startup = report["startup"]

    print()
    print("PROGRAMMES AU DEMARRAGE")
    print("-" * 75)

    print(
        f"Nombre de programmes : "
        f"{startup['count']}"
    )

    print(
        f"Statut                : "
        f"{startup['status']}"
    )

    print()