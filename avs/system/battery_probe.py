# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT
======================

Battery Probe
--------------

Collecte les informations disponibles sur la batterie
d'un ordinateur Windows.

Informations récupérées :
- présence d'une batterie
- pourcentage de charge
- source d'alimentation
- état de charge
- capacité de conception
- capacité maximale actuelle
- estimation de la santé de la batterie
"""

import json
import subprocess
from dataclasses import asdict, dataclass
from typing import Optional

import psutil


@dataclass
class BatteryResult:
    """Résultat de l'analyse de la batterie."""

    present: bool
    charge_percent: Optional[int]
    power_source: str
    status: str
    design_capacity_mwh: Optional[int]
    full_charge_capacity_mwh: Optional[int]
    health_percent: Optional[int]
    health_status: str


def _get_basic_battery_info():
    """
    Récupère le niveau de charge et l'état d'alimentation
    grâce à psutil.
    """

    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "present": False,
            "charge_percent": None,
            "power_source": "Aucune batterie détectée",
            "status": "NON DISPONIBLE",
        }

    charge_percent = int(round(battery.percent))

    if battery.power_plugged:
        power_source = "Secteur"

        if charge_percent >= 100:
            status = "Charge complète"
        else:
            status = "En charge"
    else:
        power_source = "Batterie"
        status = "Sur batterie"

    return {
        "present": True,
        "charge_percent": charge_percent,
        "power_source": power_source,
        "status": status,
    }


def _get_capacity_info():
    """
    Récupère les capacités de conception et de charge maximale
    depuis WMI Windows.

    Certaines machines ne fournissent pas ces informations.
    Dans ce cas, les valeurs restent à None.
    """

    powershell_script = r"""
$static = Get-CimInstance `
    -Namespace root\WMI `
    -ClassName BatteryStaticData `
    -ErrorAction SilentlyContinue |
    Select-Object -First 1 DesignedCapacity, FullChargedCapacity

if ($null -eq $static) {
    exit 0
}

[PSCustomObject]@{
    DesignedCapacity = $static.DesignedCapacity
    FullChargedCapacity = $static.FullChargedCapacity
} | ConvertTo-Json -Compress
"""

    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_script,
            ],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        if completed.returncode != 0:
            return None, None

        output = completed.stdout.strip()

        if not output:
            return None, None

        data = json.loads(output)

        design_capacity = data.get("DesignedCapacity")
        full_charge_capacity = data.get("FullChargedCapacity")

        design_capacity = (
            int(design_capacity)
            if design_capacity is not None
            else None
        )

        full_charge_capacity = (
            int(full_charge_capacity)
            if full_charge_capacity is not None
            else None
        )

        return design_capacity, full_charge_capacity

    except (
        subprocess.SubprocessError,
        json.JSONDecodeError,
        ValueError,
        OSError,
    ):
        return None, None


def _calculate_health(design_capacity, full_charge_capacity):
    """
    Calcule une estimation de la santé de la batterie.

    La santé est calculée comme :
        capacité actuelle / capacité de conception * 100
    """

    if not design_capacity or not full_charge_capacity:
        return None, "NON DISPONIBLE"

    if design_capacity <= 0 or full_charge_capacity <= 0:
        return None, "NON DISPONIBLE"

    health = round(
        (full_charge_capacity / design_capacity) * 100
    )

    health = max(0, min(100, health))

    if health >= 80:
        health_status = "BONNE"
    elif health >= 60:
        health_status = "USURE MODEREE"
    else:
        health_status = "USURE IMPORTANTE"

    return health, health_status


def get_battery_info():
    """
    Fonction principale du module.

    Retourne un dictionnaire facilement intégrable
    dans le rapport AVS.
    """

    basic_info = _get_basic_battery_info()

    if not basic_info["present"]:
        result = BatteryResult(
            present=False,
            charge_percent=None,
            power_source=basic_info["power_source"],
            status=basic_info["status"],
            design_capacity_mwh=None,
            full_charge_capacity_mwh=None,
            health_percent=None,
            health_status="NON DISPONIBLE",
        )

        return asdict(result)

    design_capacity, full_charge_capacity = _get_capacity_info()

    health_percent, health_status = _calculate_health(
        design_capacity,
        full_charge_capacity,
    )

    result = BatteryResult(
        present=True,
        charge_percent=basic_info["charge_percent"],
        power_source=basic_info["power_source"],
        status=basic_info["status"],
        design_capacity_mwh=design_capacity,
        full_charge_capacity_mwh=full_charge_capacity,
        health_percent=health_percent,
        health_status=health_status,
    )

    return asdict(result)


def main():
    """Affichage console pour test du module."""

    print("=" * 55)
    print("             AVS COMPUTER ASSISTANT")
    print("                ANALYSE BATTERIE")
    print("=" * 55)

    battery = get_battery_info()

    print()

    if not battery["present"]:
        print("Batterie : Aucune batterie détectée")
        print(f"Etat     : {battery['health_status']}")
        return

    print(f"Charge actuelle       : {battery['charge_percent']} %")
    print(f"Alimentation          : {battery['power_source']}")
    print(f"Etat                   : {battery['status']}")

    if battery["design_capacity_mwh"] is not None:
        print(
            "Capacite de conception : "
            f"{battery['design_capacity_mwh']} mWh"
        )
    else:
        print("Capacite de conception : N/A")

    if battery["full_charge_capacity_mwh"] is not None:
        print(
            "Capacite maximale      : "
            f"{battery['full_charge_capacity_mwh']} mWh"
        )
    else:
        print("Capacite maximale      : N/A")

    if battery["health_percent"] is not None:
        print(
            f"Sante estimee          : "
            f"{battery['health_percent']} %"
        )
        print(
            f"Etat de sante          : "
            f"{battery['health_status']}"
        )
    else:
        print("Sante estimee          : N/A")
        print(
            "Etat de sante          : "
            f"{battery['health_status']}"
        )


if __name__ == "__main__":
    main()