"""
main.py

Interface en ligne de commande de AVS Computer Assistant.

La CLI :
- lance les tests réseau ;
- transmet les résultats au moteur de diagnostic ;
- affiche un résultat compréhensible par l'utilisateur.

Elle ne contient pas la logique de diagnostic.
"""

from avs.system.network_probe import ping, resolve_dns
from avs.diagnostics.network_diagnostic import analyze_network


def afficher_entete():
    """Affiche l'en-tête du programme."""

    print("=" * 55)
    print("             AVS COMPUTER ASSISTANT")
    print("                DIAGNOSTIC RÉSEAU")
    print("=" * 55)
    print()


def afficher_diagnostic(diagnostic):
    """Affiche le diagnostic final."""

    print()
    print("-" * 55)
    print("                    DIAGNOSTIC")
    print("-" * 55)
    print()

    print(f"STATUT : {diagnostic.status}")
    print(f"\n{diagnostic.title}")
    print()
    print(diagnostic.message)
    print()

    print("RECOMMANDATION")
    print(diagnostic.recommendation)

    print()
    print("-" * 55)


def main():
    """Point d'entrée principal du programme."""

    afficher_entete()

    try:
        # ======================================================
        # TEST 1 : CONNECTIVITÉ IP
        # ======================================================

        print("[1/2] Vérification de la connexion Internet...")
        print()

        ping_result = ping("1.1.1.1")
        

        if ping_result.success:
            print("✓ Connexion réseau détectée")
        else:
            print("✗ Connexion réseau inaccessible")

        # ======================================================
        # TEST 2 : DNS
        # ======================================================

        print()
        print("[2/2] Vérification du DNS...")
        print()

        dns_result = resolve_dns("google.com")

        if dns_result.success:
            print("✓ Résolution DNS fonctionnelle")
        else:
            print("✗ Problème de résolution DNS")

        # ======================================================
        # ANALYSE
        # ======================================================

        print()
        print("Analyse des résultats...")
        print()

        diagnostic = analyze_network(
            ping_result,
            dns_result
        )

        afficher_diagnostic(diagnostic)

    except Exception as erreur:
        print()
        print("-" * 55)
        print("Une erreur inattendue est survenue.")
        print(f"Détail technique : {erreur}")
        print("Veuillez réessayer. Si le problème persiste, ")
        print("contactez le support technique.")
        print("-" * 55)


if __name__ == "__main__":
    main()