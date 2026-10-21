"""
AVS COMPUTER ASSISTANT

MOTEUR D'ACTION

Ce module transforme les diagnostics du systeme
en actions concretes a effectuer.
"""

import unicodedata


def normalize_status(value):
    """
    Normalise un statut pour faciliter les comparaisons.

    Exemple :
    ÉLEVÉ  -> ELEVE
    ÉLEVÉE -> ELEVEE
    CRITIQUE -> CRITIQUE
    """

    value = str(value).upper()

    value = unicodedata.normalize(
        "NFD",
        value,
    )

    return "".join(
        character
        for character in value
        if unicodedata.category(character) != "Mn"
    )


def decide_action(
    ram: dict,
    cpu: dict,
    disk: dict,
    processes: list[dict],
    causes: dict,
) -> dict:
    """
    Determine les actions a effectuer a partir
    des diagnostics du systeme.
    """

    actions = []

    cause_priority = normalize_status(
        causes.get("priority", "NORMALE")
    )

    # =====================================================
    # RAM
    # =====================================================

    ram_status = normalize_status(
        ram.get("usage_status", "OK")
    )

    if ram_status in ["ELEVE", "CRITIQUE"]:
        actions.append(
            {
                "type": "RAM",
                "priority": (
                    "HAUTE"
                    if cause_priority in ["HAUTE", "CRITIQUE"]
                    else "NORMALE"
                ),
                "action": (
                    "Fermer les applications inutilisees "
                    "et identifier les processus consommant "
                    "le plus de RAM."
                ),
            }
        )

    # =====================================================
    # CPU
    # =====================================================

    cpu_status = normalize_status(
        cpu.get("usage_status", "NORMALE")
    )

    if cpu_status in ["ELEVEE", "CRITIQUE"]:
        actions.append(
            {
                "type": "CPU",
                "priority": "HAUTE",
                "action": (
                    "Identifier les applications consommant "
                    "le plus de CPU."
                ),
            }
        )

    # =====================================================
    # DISQUE
    # =====================================================

    disk_status = normalize_status(
        disk.get("usage_status", "OK")
    )

    if disk_status in [
        "ATTENTION",
        "ELEVE",
        "CRITIQUE",
    ]:
        actions.append(
            {
                "type": "DISQUE",
                "priority": (
                    "HAUTE"
                    if cause_priority in ["HAUTE", "CRITIQUE"]
                    else "NORMALE"
                ),
                "action": (
                    "Liberer de l'espace disque et supprimer "
                    "les fichiers inutiles."
                ),
            }
        )

    # =====================================================
    # PROCESSUS
    # =====================================================

    problematic_processes = []

    for process in processes:
        status = normalize_status(
            process.get("status", "NORMAL")
        )

        if status in ["ELEVE", "CRITIQUE"]:
            problematic_processes.append(process)

    if problematic_processes:
        actions.append(
            {
                "type": "PROCESSUS",
                "priority": (
                    "HAUTE"
                    if cause_priority in ["HAUTE", "CRITIQUE"]
                    else "NORMALE"
                ),
                "action": (
                    "Examiner les processus fortement "
                    "consommateurs de ressources."
                ),
            }
        )

    # =====================================================
    # AUCUN PROBLEME
    # =====================================================

    if not actions:
        return {
            "status": "SURVEILLANCE",
            "priority": "NORMALE",
            "actions": [
                {
                    "type": "SYSTEME",
                    "priority": "NORMALE",
                    "action": (
                        "Aucune action immediate necessaire. "
                        "Continuer la surveillance du systeme."
                    ),
                }
            ],
        }

    # =====================================================
    # PRIORITE GLOBALE
    # =====================================================

    priority_order = {
        "HAUTE": 3,
        "NORMALE": 2,
        "FAIBLE": 1,
    }

    global_priority = max(
        actions,
        key=lambda action: priority_order.get(
            action["priority"],
            0,
        ),
    )["priority"]

    # =====================================================
    # TRI DES ACTIONS
    # =====================================================

    actions.sort(
        key=lambda action: priority_order.get(
            action["priority"],
            0,
        ),
        reverse=True,
    )

    return {
        "status": "ACTION REQUISE",
        "priority": global_priority,
        "actions": actions,
    }


# =========================================================
# TEST MANUEL
# =========================================================

if __name__ == "__main__":

    ram = {
        "usage_status": "ÉLEVÉ",
    }

    cpu = {
        "usage_status": "CRITIQUE",
    }

    disk = {
        "usage_status": "OK",
    }

    processes = [
        {
            "name": "Code.exe",
            "status": "NORMAL",
        }
    ]

    causes = {
        "priority": "HAUTE",
    }

    result = decide_action(
        ram,
        cpu,
        disk,
        processes,
        causes,
    )

    print("=" * 70)
    print("              AVS COMPUTER ASSISTANT")
    print("                  MOTEUR D'ACTION")
    print("=" * 70)

    print()
    print("STATUT")
    print("-" * 70)
    print("Statut   :", result["status"])
    print("Priorite :", result["priority"])

    print()
    print("ACTIONS")
    print("-" * 70)

    for index, action in enumerate(
        result["actions"],
        start=1,
    ):
        print(
            f"{index}. "
            f"[{action['priority']}] "
            f"{action['type']} : "
            f"{action['action']}"
        )

    print()
    print("=" * 70)