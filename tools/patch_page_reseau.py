# -*- coding: utf-8 -*-
"""Ajoute la page « Réseau détaillé » à la console AVS (avs/ui/app.py).

Usage (depuis la racine du projet) :   python tools/patch_page_reseau.py
Sauvegarde : avs/ui/app.py.avant_reseau. Relançable sans risque.
"""
import os
import shutil
import sys

RACINE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
FICHIER = os.path.join(RACINE, "avs", "ui", "app.py")
MARQUEUR = "show_network_details"

IMPORT_ANCRE = (
    "from avs.system.hardware_info_probe import (\n"
    "    get_processor_info,\n"
    "    get_graphics_info,\n"
    "    get_machine_info,\n"
    ")\n"
)
IMPORT_NOUVEAU = "from avs.system.network_details_probe import get_network_details\n"

MENU_ANCRE = '            ("◎", "Réseau", self.show_network),\n'
MENU_NOUVEAU = '            ("●", "Réseau détaillé", self.show_network_details),\n'

METHODE_ANCRE = "    def show_hardware_info(self):\n"
METHODE = '''    def show_network_details(self):
        """Affiche les détails du réseau : interfaces, passerelle, DNS et ports en écoute."""

        self.page_title.config(
            text="● Réseau détaillé"
        )

        self._clear_content()

        self.status_label.config(
            text="Lecture des informations réseau..."
        )

        self.update_idletasks()

        details = get_network_details()

        self.status_label.config(
            text="Interfaces, passerelle, DNS et ports en écoute."
        )

        self._create_info_card(
            0,
            0,
            "PASSERELLE",
            details.gateway or "Non disponible",
            "OK" if details.gateway else "CRITIQUE",
            "Adresse du routeur par lequel sort le trafic.",
        )

        self._create_info_card(
            0,
            1,
            "SERVEURS DNS",
            ", ".join(details.dns_servers) or "Non disponible",
            "OK" if details.dns_servers else "CRITIQUE",
            "Serveurs qui traduisent les noms de sites en adresses.",
        )

        def format_speed(speed):
            if not speed:
                return "vitesse inconnue"
            if speed >= 1000:
                return str(round(speed / 1000, 1)).rstrip("0").rstrip(".") + " Gb/s"
            return str(speed) + " Mb/s"

        lines = []
        for interface in details.interfaces[:8]:
            state = "active" if interface.is_up else "inactive"
            address = interface.ipv4 or "sans adresse IPv4"
            mac = interface.mac or "inconnue"
            lines.append(
                interface.name + "   |   " + state + "   |   " + address
                + "   |   MAC " + mac + "   |   " + format_speed(interface.speed_mbps)
            )
        if len(details.interfaces) > 8:
            lines.append("... et " + str(len(details.interfaces) - 8) + " autre(s) interface(s)")

        self._create_information_box(
            1,
            "INTERFACES RÉSEAU",
            "\\n".join(lines) or "Aucune interface détectée.",
        )

        port_lines = []
        for port in details.listening_ports[:15]:
            port_lines.append(
                "Port " + str(port.port) + "   |   " + port.address
                + "   |   " + (port.process or "processus non visible")
            )
        if len(details.listening_ports) > 15:
            port_lines.append("... et " + str(len(details.listening_ports) - 15) + " autre(s) port(s)")

        message = "\\n".join(port_lines) or "Aucun port TCP en écoute détecté."
        if details.process_info_limited:
            message += "\\n\\nCertains noms de processus ne sont pas visibles sans droits administrateur."

        self._create_information_box(
            2,
            "PORTS TCP EN ÉCOUTE",
            message,
        )

        if details.environment_note:
            self._create_information_box(
                3,
                "À SAVOIR",
                details.environment_note,
            )

'''


def compter(code, texte):
    return code.count(texte)


def main():
    if not os.path.exists(FICHIER):
        print("ERREUR : avs/ui/app.py introuvable. Lancez ce script depuis la racine du projet.")
        sys.exit(1)
    with open(FICHIER, "r", encoding="utf-8") as f:
        code = f.read()
    if MARQUEUR in code:
        print("  déjà fait  app.py")
        return
    for nom, ancre in (("import", IMPORT_ANCRE), ("menu", MENU_ANCRE), ("méthode", METHODE_ANCRE)):
        if compter(code, ancre) != 1:
            print("ERREUR : repère « " + nom + " » introuvable ou en double dans app.py. Rien n'a été modifié.")
            sys.exit(1)
    if not os.path.exists(FICHIER + ".avant_reseau"):
        shutil.copy2(FICHIER, FICHIER + ".avant_reseau")
    code = code.replace(IMPORT_ANCRE, IMPORT_ANCRE + IMPORT_NOUVEAU)
    code = code.replace(MENU_ANCRE, MENU_ANCRE + MENU_NOUVEAU)
    code = code.replace(METHODE_ANCRE, METHODE + METHODE_ANCRE)
    with open(FICHIER, "w", encoding="utf-8") as f:
        f.write(code)
    print("  patché     app.py (import, menu, page)")


if __name__ == "__main__":
    main()
