from avs.system.network_probe import PingResult, DnsResult
from avs.diagnostics.network_diagnostic import analyze_network


def test_connexion_correcte():
    ping = PingResult(
        host="1.1.1.1",
        success=True,
        packet_loss_percent=0,
        min_latency_ms=30,
        max_latency_ms=50,
        avg_latency_ms=40,
        raw_output=""
    )

    dns = DnsResult(
        hostname="google.com",
        success=True,
        ip_address="142.251.47.14",
        error_message=None
    )

    diagnostic = analyze_network(ping, dns)

    assert diagnostic.status == "OK"


def test_probleme_dns():
    ping = PingResult(
        host="1.1.1.1",
        success=True,
        packet_loss_percent=0,
        min_latency_ms=30,
        max_latency_ms=50,
        avg_latency_ms=40,
        raw_output=""
    )

    dns = DnsResult(
        hostname="google.com",
        success=False,
        ip_address=None,
        error_message="DNS failure"
    )

    diagnostic = analyze_network(ping, dns)

    assert diagnostic.status == "DNS_ERROR"


def test_connexion_instable():
    ping = PingResult(
        host="1.1.1.1",
        success=True,
        packet_loss_percent=0,
        min_latency_ms=63,
        max_latency_ms=2080,
        avg_latency_ms=571,
        raw_output=""
    )

    dns = DnsResult(
        hostname="google.com",
        success=True,
        ip_address="142.251.47.14",
        error_message=None
    )

    diagnostic = analyze_network(ping, dns)

    assert diagnostic.status == "HIGH_LATENCY"


def test_donnees_incompletes():
    ping = PingResult(
        host="1.1.1.1",
        success=True,
        packet_loss_percent=0,
        min_latency_ms=None,
        max_latency_ms=None,
        avg_latency_ms=None,
        raw_output=""
    )

    dns = DnsResult(
        hostname="google.com",
        success=True,
        ip_address="142.251.47.14",
        error_message=None
    )

    diagnostic = analyze_network(ping, dns)

    assert diagnostic.status == "INCOMPLETE_DATA"