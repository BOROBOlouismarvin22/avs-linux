"""Test minimal : les appels PowerShell fonctionnent-ils dans un .exe ?"""

import subprocess
import sys
import traceback

print("Programme empaquete :", getattr(sys, "frozen", False))
print("Python              :", sys.version)
print()

print("--- Test 1 : appel PowerShell direct ---")

try:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "(Get-CimInstance Win32_Processor).Name",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        stdin=subprocess.DEVNULL,
    )

    print("code retour :", result.returncode)
    print("stdout      :", repr(result.stdout))
    print("stderr      :", repr(result.stderr))

except Exception:
    print("EXCEPTION :")
    traceback.print_exc()

print()
print("--- Test 2 : via le module AVS ---")

try:
    from avs.system import hardware_info_probe as probe

    print("Processeur      :", probe.get_processor_info())
    print("Carte graphique :", probe.get_graphics_info())
    print("Machine         :", probe.get_machine_info())

except Exception:
    print("EXCEPTION :")
    traceback.print_exc()

print()
input("Appuie sur Entree pour fermer...")