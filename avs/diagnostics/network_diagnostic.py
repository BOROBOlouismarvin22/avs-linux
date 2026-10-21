"""
network_diagnostic.py

Cerveau du diagnostic réseau de AVS Computer Assistant.

Ce module analyse les résultats produits par network_probe.py
et transforme les données techniques en un verdict compréhensible.
"""

from dataclasses import dataclass

from avs.system.network_probe import PingResult, DnsResult


@dataclass
class DiagnosticResult:
    """Résultat interprété du diagnostic réseau."""

    status: str
    title: str
    message: str
    recommendation: str


def analyze_network(
    ping_result: PingResult,
    dns_result: DnsResult
) -> DiagnosticResult:

    # ========================================================
    # CAS 1 : aucune connexion IP
    # ========================================================

    if not ping_result.success:

        return DiagnosticResult(
            status="CRITICAL",
            title="Connexion Internet inaccessible",
            message=(
                "Votre ordinateur ne parvient pas à joindre "
                "la destination réseau testée."
            ),
            recommendation=(
                "Vérifiez votre Wi-Fi ou votre câble réseau, "
                "puis redémarrez votre équipement réseau si nécessaire."
            )
        )

    # ========================================================
    # CAS 2 : DNS en panne
    # ========================================================

    if not dns_result.success:

        return DiagnosticResult(
            status="DNS_ERROR",
            title="Problème DNS probable",
            message=(
                "Votre ordinateur communique avec Internet, "
                "mais la résolution des noms de domaine échoue."
            ),
            recommendation=(
                "Vérifiez la configuration DNS de votre connexion "
                "et essayez un autre serveur DNS."
            )
        )

    # ========================================================
    # CAS 3 : perte importante de paquets
    # ========================================================

    if (
        ping_result.packet_loss_percent is not None
        and ping_result.packet_loss_percent >= 20
    ):

        return DiagnosticResult(
            status="PACKET_LOSS",
            title="Perte de paquets détectée",
            message=(
                f"{ping_result.packet_loss_percent}% des paquets "
                "n'ont pas reçu de réponse."
            ),
            recommendation=(
                "Vérifiez la qualité du Wi-Fi, le câble réseau "
                "et la stabilité de votre connexion."
            )
        )

    # ========================================================
    # CAS 4 : latence très élevée
    # ========================================================

    if (
        ping_result.avg_latency_ms is not None
        and ping_result.avg_latency_ms >= 300
    ):

        return DiagnosticResult(
            status="HIGH_LATENCY",
            title="Latence élevée détectée",
            message=(
                f"La latence moyenne est de "
                f"{ping_result.avg_latency_ms} ms."
            ),
            recommendation=(
                "Votre connexion répond lentement. "
                "Effectuez un nouveau test et vérifiez "
                "la qualité de votre réseau."
            )
        )

    # ========================================================
    # CAS 5 : forte variation de latence
    # ========================================================

    if (
        ping_result.min_latency_ms is not None
        and ping_result.max_latency_ms is not None
        and (
            ping_result.max_latency_ms
            - ping_result.min_latency_ms
        ) >= 500
    ):

        return DiagnosticResult(
            status="UNSTABLE",
            title="Connexion instable",
            message=(
                "Le temps de réponse varie fortement "
                "entre les différentes requêtes."
            ),
            recommendation=(
                "Vérifiez votre connexion Wi-Fi, "
                "la distance avec votre routeur et "
                "la charge de votre réseau."
            )
        )

    # ========================================================
    # CAS 5.5 : données de latence manquantes malgré un ping réussi
    # ========================================================

    if ping_result.avg_latency_ms is None:

        return DiagnosticResult(
            status="INCOMPLETE_DATA",
            title="Résultat partiel",
            message=(
                "La connexion semble fonctionner, mais certaines "
                "mesures n'ont pas pu être obtenues correctement."
            ),
            recommendation=(
                "Relancez le diagnostic. Si le problème persiste, "
                "cela peut indiquer un format de résultat inattendu."
            )
        )

    # ========================================================
    # CAS 6 : tout semble normal
    # ========================================================

    return DiagnosticResult(
        status="OK",
        title="Connexion correcte",
        message=(
            "La connexion réseau répond correctement "
            "et la résolution DNS fonctionne."
        ),
        recommendation=(
            "Aucune anomalie importante n'a été détectée "
            "par ces tests."
        )
    )