# -*- coding: utf-8 -*-

"""
AVS COMPUTER ASSISTANT
DIAGNOSTIC DES PROGRAMMES AU DEMARRAGE

Ce module interprète la liste des programmes au démarrage
et produit un verdict basé uniquement sur des faits vérifiables
(le nombre de programmes), sans inventer de mesure d'impact
individuel que nous ne pouvons pas calculer fiablement.
"""

from typing import List

from avs.system.startup_probe import StartupProgram


def diagnose_startup(programs: List[StartupProgram]) -> dict:

    count = len(programs)

    # DIAGNOSTIC BASE SUR LE NOMBRE DE PROGRAMMES

    if count < 5:
        status = "OK"
        message = (
            "Le nombre de programmes au démarrage est raisonnable."
        )

    elif count <= 10:
        status = "ATTENTION"
        message = (
            "Un nombre modéré de programmes démarre automatiquement "
            "avec Windows. Cela peut légèrement ralentir le démarrage."
        )

    else:
        status = "ÉLEVÉ"
        message = (
            "Un grand nombre de programmes démarre automatiquement "
            "avec Windows. Cela ralentit probablement le démarrage."
        )

    # RECOMMANDATION

    if status == "ÉLEVÉ":
        recommendation = (
            "Passez en revue la liste des programmes au démarrage "
            "et désactivez ceux dont vous n'avez pas besoin dès "
            "l'ouverture de session (via les Paramètres Windows > "
            "Applications > Démarrage)."
        )

    elif status == "ATTENTION":
        recommendation = (
            "Vérifiez la liste des programmes au démarrage et "
            "désactivez ceux que vous utilisez rarement."
        )

    else:
        recommendation = (
            "Aucune action nécessaire pour le moment."
        )

    # LISTE DETAILLEE (nom + source, sans jugement individuel)

    program_list = [
        {
            "name": program.name,
            "source": program.source,
        }
        for program in programs
    ]

    return {
        "count": count,
        "status": status,
        "message": message,
        "recommendation": recommendation,
        "programs": program_list,
    }


# ============================================================
# TEST MANUEL
# ============================================================

if __name__ == "__main__":

    from avs.system.startup_probe import get_startup_programs

    programs = get_startup_programs()
    diagnostic = diagnose_startup(programs)

    print("=" * 55)
    print("       AVS COMPUTER ASSISTANT")
    print("   DIAGNOSTIC PROGRAMMES AU DÉMARRAGE")
    print("=" * 55)

    print(f"\nNombre de programmes : {diagnostic['count']}")
    print(f"Statut                : {diagnostic['status']}")
    print(f"\n{diagnostic['message']}")
    print(f"\nRecommandation :\n{diagnostic['recommendation']}")

    print(f"\nListe des programmes :")
    for program in diagnostic["programs"]:
        print(f"- {program['name']} [{program['source']}]")