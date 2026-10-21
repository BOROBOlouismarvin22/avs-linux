# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT
======================

Storage Probe
-------------

Recupere les informations du stockage Windows :

- lecteur
- espace total
- espace utilise
- espace libre
- pourcentage d'utilisation
- numero du disque physique
- modele
- fabricant
- type de disque
- interface
- sante
- etat operationnel
- type de partition
- capacite physique
"""

import json
import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class StorageResult:
    """Informations brutes concernant le stockage."""

    drive: str
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float

    disk_number: Optional[int] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    disk_type: Optional[str] = None
    interface: Optional[str] = None
    health_status: Optional[str] = None
    operational_status: Optional[str] = None
    partition_style: Optional[str] = None
    physical_size_gb: Optional[float] = None


def _run_powershell(script: str) -> dict:
    """Execute PowerShell et retourne un dictionnaire JSON."""

    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            creationflags=getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0,
            ),
        )

        if result.returncode != 0:
            return {}

        output = result.stdout.strip()

        if not output:
            return {}

        lines = [
            line.strip()
            for line in output.splitlines()
            if line.strip()
        ]

        for line in reversed(lines):
            try:
                data = json.loads(line)

                if isinstance(data, dict):
                    return data

            except json.JSONDecodeError:
                continue

        return {}

    except (
        subprocess.SubprocessError,
        json.JSONDecodeError,
        ValueError,
        OSError,
    ):
        return {}


def _clean_value(value) -> Optional[str]:
    """Nettoie une valeur Windows."""

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def _normalize_disk_type(
    media_type: Optional[str],
    bus_type: Optional[str],
) -> str:
    """Convertit les valeurs Windows en libelles AVS."""

    media = (media_type or "").strip().upper()
    bus = (bus_type or "").strip().upper()

    if bus == "NVME":
        return "SSD NVMe"

    if media == "SSD":
        return "SSD"

    if media == "HDD":
        return "HDD"

    if bus == "USB":
        return "Disque USB"

    if bus == "SATA":
        return "Disque SATA"

    if media:
        return media

    if bus:
        return f"Disque {bus}"

    return "INCONNU"


def _get_physical_disk_info(drive: str) -> dict:
    """
    Relie le lecteur Windows au disque physique.

    Exemple :
        C: -> Disque 0
    """

    drive_letter = drive[:1].upper()

    script = rf'''
$ErrorActionPreference = "SilentlyContinue"

$partition = Get-Partition -DriveLetter "{drive_letter}" |
    Select-Object -First 1

if ($null -eq $partition) {{
    exit 0
}}

$diskNumber = [int]$partition.DiskNumber

$disk = Get-Disk -Number $diskNumber

if ($null -eq $disk) {{
    exit 0
}}

$wmiDisk = Get-CimInstance Win32_DiskDrive |
    Where-Object {{
        $_.Index -eq $diskNumber
    }} |
    Select-Object -First 1

$physicalDisk = Get-PhysicalDisk |
    Where-Object {{
        $_.FriendlyName -eq $disk.FriendlyName
    }} |
    Select-Object -First 1

$model = [string]$disk.FriendlyName

if ($null -ne $wmiDisk -and $wmiDisk.Model) {{
    $model = [string]$wmiDisk.Model
}}

$manufacturer = $null

if ($null -ne $wmiDisk -and $wmiDisk.Manufacturer) {{
    $manufacturer = [string]$wmiDisk.Manufacturer
}}

$mediaType = $null
$physicalHealthStatus = $null
$physicalOperationalStatus = $null

if ($null -ne $physicalDisk) {{

    if ($physicalDisk.MediaType) {{
        $mediaType = [string]$physicalDisk.MediaType
    }}

    if ($physicalDisk.HealthStatus) {{
        $physicalHealthStatus = [string]$physicalDisk.HealthStatus
    }}

    if ($physicalDisk.OperationalStatus) {{
        $physicalOperationalStatus = (
            $physicalDisk.OperationalStatus -join ", "
        )
    }}
}}

$operationalStatus = $null

if ($disk.OperationalStatus) {{
    $operationalStatus = (
        $disk.OperationalStatus -join ", "
    )
}}

[PSCustomObject]@{{
    DiskNumber = $diskNumber
    Model = $model
    Manufacturer = $manufacturer
    MediaType = $mediaType
    BusType = [string]$disk.BusType
    HealthStatus = [string]$disk.HealthStatus
    OperationalStatus = $operationalStatus
    PhysicalHealthStatus = $physicalHealthStatus
    PhysicalOperationalStatus = $physicalOperationalStatus
    PartitionStyle = [string]$disk.PartitionStyle
    Size = [int64]$disk.Size
}} | ConvertTo-Json -Compress
'''

    return _run_powershell(script)


def get_storage_info(
    drive: str = "C:\\",
) -> StorageResult:
    """Recupere les informations du lecteur et du disque physique."""

    total, used, free = shutil.disk_usage(drive)

    total_gb = total / (1024 ** 3)
    used_gb = used / (1024 ** 3)
    free_gb = free / (1024 ** 3)

    if total > 0:
        usage_percent = (used / total) * 100
    else:
        usage_percent = 0.0

    physical = _get_physical_disk_info(drive)

    # -------------------------------------------------
    # NUMERO DU DISQUE
    # -------------------------------------------------

    disk_number = physical.get("DiskNumber")

    if disk_number is not None:
        try:
            disk_number = int(disk_number)
        except (TypeError, ValueError):
            disk_number = None

    # -------------------------------------------------
    # MODELE
    # -------------------------------------------------

    model = _clean_value(
        physical.get("Model")
    )

    # -------------------------------------------------
    # FABRICANT
    # -------------------------------------------------

    manufacturer = _clean_value(
        physical.get("Manufacturer")
    )

    # -------------------------------------------------
    # TYPE
    # -------------------------------------------------

    media_type = _clean_value(
        physical.get("MediaType")
    )

    bus_type = _clean_value(
        physical.get("BusType")
    )

    disk_type = _normalize_disk_type(
        media_type,
        bus_type,
    )

    # -------------------------------------------------
    # INTERFACE
    # -------------------------------------------------

    interface = bus_type

    # -------------------------------------------------
    # SANTE
    # -------------------------------------------------

    health_status = _clean_value(
        physical.get("HealthStatus")
    )

    if not health_status:
        health_status = _clean_value(
            physical.get("PhysicalHealthStatus")
        )

    # -------------------------------------------------
    # ETAT OPERATIONNEL
    # -------------------------------------------------

    operational_status = _clean_value(
        physical.get("OperationalStatus")
    )

    if not operational_status:
        operational_status = _clean_value(
            physical.get("PhysicalOperationalStatus")
        )

    # -------------------------------------------------
    # PARTITION
    # -------------------------------------------------

    partition_style = _clean_value(
        physical.get("PartitionStyle")
    )

    # -------------------------------------------------
    # CAPACITE PHYSIQUE
    # -------------------------------------------------

    physical_size_gb = physical.get("Size")

    if physical_size_gb is not None:
        try:
            physical_size_gb = round(
                int(physical_size_gb)
                / (1024 ** 3),
                2,
            )
        except (TypeError, ValueError):
            physical_size_gb = None

    # -------------------------------------------------
    # RESULTAT
    # -------------------------------------------------

    return StorageResult(
        drive=drive,
        total_gb=round(
            total_gb,
            2,
        ),
        used_gb=round(
            used_gb,
            2,
        ),
        free_gb=round(
            free_gb,
            2,
        ),
        usage_percent=round(
            usage_percent,
            2,
        ),
        disk_number=disk_number,
        model=model,
        manufacturer=manufacturer,
        disk_type=disk_type,
        interface=interface,
        health_status=health_status,
        operational_status=operational_status,
        partition_style=partition_style,
        physical_size_gb=physical_size_gb,
    )


def main():
    """Test console du module."""

    result = get_storage_info()

    print("=" * 65)
    print("             AVS COMPUTER ASSISTANT")
    print("               ANALYSE DU STOCKAGE")
    print("=" * 65)

    print()

    print(
        f"Lecteur             : {result.drive}"
    )

    print(
        f"Espace total        : {result.total_gb} Go"
    )

    print(
        f"Espace utilise      : {result.used_gb} Go"
    )

    print(
        f"Espace disponible   : {result.free_gb} Go"
    )

    print(
        f"Utilisation         : {result.usage_percent} %"
    )

    print()

    print("----- DISQUE PHYSIQUE -----")

    disk_number_text = (
        str(result.disk_number)
        if result.disk_number is not None
        else "N/A"
    )

    model_text = (
        result.model
        if result.model
        else "N/A"
    )

    manufacturer_text = (
        result.manufacturer
        if result.manufacturer
        else "N/A"
    )

    disk_type_text = (
        result.disk_type
        if result.disk_type
        else "N/A"
    )

    interface_text = (
        result.interface
        if result.interface
        else "N/A"
    )

    physical_size_text = (
        f"{result.physical_size_gb} Go"
        if result.physical_size_gb is not None
        else "N/A"
    )

    health_text = (
        result.health_status
        if result.health_status
        else "N/A"
    )

    operational_text = (
        result.operational_status
        if result.operational_status
        else "N/A"
    )

    partition_text = (
        result.partition_style
        if result.partition_style
        else "N/A"
    )

    print(
        f"Numero disque       : {disk_number_text}"
    )

    print(
        f"Fabricant           : {manufacturer_text}"
    )

    print(
        f"Modele              : {model_text}"
    )

    print(
        f"Type                : {disk_type_text}"
    )

    print(
        f"Interface           : {interface_text}"
    )

    print(
        f"Capacite physique   : {physical_size_text}"
    )

    print(
        f"Sante               : {health_text}"
    )

    print(
        f"Etat operationnel   : {operational_text}"
    )

    print(
        f"Partition           : {partition_text}"
    )


if __name__ == "__main__":
    main()

# --- AVS_LINUX_PATCH : versions Linux ---
import sys as _avs_sys
if not _avs_sys.platform.startswith('win'):
    from avs.system import linux_compat as _avs_lc
    get_storage_info = _avs_lc.get_storage_info  # AVS_LINUX_PATCH
