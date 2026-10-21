# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT

Informations matérielles - couche système.

Version portable :
- CPU via registre Windows
- carte graphique via registre Windows
- fabricant et modèle via registre Windows

Cette version n'utilise plus PowerShell/WMI pour ce module.
Le but est de rendre la collecte robuste dans l'EXE PyInstaller
et lorsqu'AVS est lancé depuis une clé USB.

Aucune décision de diagnostic n'est prise ici.
"""

import datetime
import os
import platform
import tempfile
try:
    import winreg  # AVS_WINREG_STUB
except ImportError:  # Linux : remplaçant minimal pour que le module se charge
    class _WinregStub:
        def __getattr__(self, nom):
            return 0
    winreg = _WinregStub()
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProcessorInfo:
    """Informations statiques concernant le processeur."""

    name: Optional[str]


@dataclass
class GraphicsInfo:
    """Informations statiques concernant la carte graphique."""

    name: Optional[str]


@dataclass
class MachineInfo:
    """Informations statiques concernant la machine."""

    manufacturer: Optional[str]
    model: Optional[str]


def _log_debug(message: str) -> None:
    """Écrit une ligne dans le journal temporaire AVS."""

    try:
        path = os.path.join(
            tempfile.gettempdir(),
            "avs_debug.log",
        )

        with open(
            path,
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                f"{datetime.datetime.now().isoformat()}  {message}\n"
            )

    except Exception:
        pass


def _clean_value(value) -> Optional[str]:
    """Nettoie une valeur texte provenant du registre."""

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def _open_registry_key(path: str):
    """
    Ouvre une clé HKLM en lecture seule.

    KEY_WOW64_64KEY permet au programme portable de lire la vue
    64 bits du registre lorsque Windows est 64 bits.
    """

    access = winreg.KEY_READ

    wow64_64key = getattr(
        winreg,
        "KEY_WOW64_64KEY",
        0,
    )

    access |= wow64_64key

    return winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        path,
        0,
        access,
    )


def _read_registry_value(
    path: str,
    value_name: str,
) -> Optional[str]:
    """Lit une valeur texte dans HKLM."""

    try:
        with _open_registry_key(path) as key:
            value, _ = winreg.QueryValueEx(
                key,
                value_name,
            )

        cleaned = _clean_value(value)

        _log_debug(
            f"REG path={path!r} value={value_name!r} result={cleaned!r}"
        )

        return cleaned

    except (
        FileNotFoundError,
        PermissionError,
        OSError,
    ) as error:
        _log_debug(
            f"REG ERROR path={path!r} value={value_name!r} "
            f"{type(error).__name__}: {error}"
        )
        return None


def get_processor_info() -> ProcessorInfo:
    """
    Récupère le nom du processeur via le registre Windows.

    Aucun processus externe n'est lancé.
    """

    name = _read_registry_value(
        r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        "ProcessorNameString",
    )

    if not name:
        name = _clean_value(platform.processor())

        _log_debug(
            f"CPU fallback platform.processor -> {name!r}"
        )

    return ProcessorInfo(name=name)


def _get_graphics_from_registry() -> Optional[str]:
    """
    Cherche une carte graphique dans les profils vidéo Windows.

    DriverDesc est utilisé comme nom lisible du GPU.
    """

    base_path = (
        r"SYSTEM\CurrentControlSet\Control\Video"
    )

    try:
        with _open_registry_key(base_path) as video_key:
            subkey_count = winreg.QueryInfoKey(video_key)[0]
            fallback_name = None

            for index in range(subkey_count):
                try:
                    adapter_guid = winreg.EnumKey(
                        video_key,
                        index,
                    )
                except OSError:
                    continue

                adapter_path = (
                    f"{base_path}\\{adapter_guid}\\0000"
                )

                name = _read_registry_value(
                    adapter_path,
                    "DriverDesc",
                )

                if not name:
                    continue

                normalized = name.strip().lower()

                if fallback_name is None:
                    fallback_name = name

                if normalized != "microsoft basic display adapter":
                    return name

            return fallback_name

    except (
        FileNotFoundError,
        PermissionError,
        OSError,
    ) as error:
        _log_debug(
            "GPU registry error: "
            f"{type(error).__name__}: {error}"
        )
        return None


def get_graphics_info() -> GraphicsInfo:
    """Récupère le nom d'une carte graphique via le registre Windows."""

    return GraphicsInfo(
        name=_get_graphics_from_registry(),
    )


def get_machine_info() -> MachineInfo:
    """
    Récupère le fabricant et le modèle de la machine
    via le registre Windows.
    """

    system_path = (
        r"SYSTEM\CurrentControlSet\Control\SystemInformation"
    )

    manufacturer = _read_registry_value(
        system_path,
        "SystemManufacturer",
    )

    model = _read_registry_value(
        system_path,
        "SystemProductName",
    )

    return MachineInfo(
        manufacturer=manufacturer,
        model=model,
    )


if __name__ == "__main__":
    processor = get_processor_info()
    graphics = get_graphics_info()
    machine = get_machine_info()

    print("=" * 65)
    print("             AVS COMPUTER ASSISTANT")
    print("           INFORMATIONS MATÉRIELLES")
    print("=" * 65)

    print(
        f"\nProcesseur      : "
        f"{processor.name or 'Non disponible'}"
    )

    print(
        f"Carte graphique : "
        f"{graphics.name or 'Non disponible'}"
    )

    print(
        f"Fabricant       : "
        f"{machine.manufacturer or 'Non disponible'}"
    )

    print(
        f"Modèle          : "
        f"{machine.model or 'Non disponible'}"
    )

# --- AVS_LINUX_PATCH : versions Linux ---
import sys as _avs_sys
if not _avs_sys.platform.startswith('win'):
    from avs.system import linux_compat as _avs_lc
    get_processor_info = _avs_lc.get_processor_info
    get_graphics_info = _avs_lc.get_graphics_info
    get_machine_info = _avs_lc.get_machine_info  # AVS_LINUX_PATCH
