"""
Safe / non-destructive network exposure scanner.

Design constraints (see project security requirements):
- NEVER executes shell commands or subprocesses built from user input.
- Only ever attempts a plain TCP connect() with a short timeout against a
  small, fixed whitelist of ports relevant to the training scenario.
- No banner grabbing, no payload sending, no brute forcing, no exploitation.
- All resolution/connection failures are caught and reported as
  human-readable statuses, never raw stack traces.
"""

import socket
import time
from dataclasses import dataclass
from typing import List

# Fixed whitelist — representative of Problem 4's exposure profile.
# Extending this list intentionally requires a code change, not user input,
# to keep the scan surface bounded and auditable.
WHITELISTED_PORTS = [
    (22, "SSH", "Administrative service"),
    (53, "DNS", "Internal resolver"),
    (443, "HTTPS", "Public application endpoint"),
    (3389, "RDP", "Management service"),
]

CONNECT_TIMEOUT_SECONDS = 1.5


@dataclass
class ServiceResult:
    port: int
    service_name: str
    exposure: str
    reachable: str  # "open" | "closed" | "filtered"


class ScanError(Exception):
    pass


def resolve_host(raw_target: str) -> str:
    cleaned = raw_target.strip()
    cleaned = cleaned.replace("https://", "").replace("http://", "")
    cleaned = cleaned.split("/")[0].split(":")[0]
    try:
        return socket.gethostbyname(cleaned)
    except socket.gaierror as exc:
        raise ScanError(f"DNS resolution failed for '{cleaned}'") from exc


def check_port(host: str, port: int) -> str:
    """Attempt a bare TCP connect. Never sends any payload."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(CONNECT_TIMEOUT_SECONDS)
    try:
        result = sock.connect_ex((host, port))
        return "open" if result == 0 else "closed"
    except (socket.timeout, OSError):
        return "filtered"
    finally:
        sock.close()


def run_safe_scan(raw_target: str, demo_mode: bool = False) -> "tuple[str, List[ServiceResult]]":
    """
    Returns (resolved_host, list of ServiceResult).
    In demo_mode, skips live network I/O and returns the fixed Problem 4
    exposure profile so the dashboard works without a reachable target.
    """
    if demo_mode:
        resolved = "203.0.113.10"  # TEST-NET-3, RFC 5737 documentation range
        results = [
            ServiceResult(22, "SSH", "Administrative service", "open"),
            ServiceResult(53, "DNS", "Internal resolver", "open"),
            ServiceResult(443, "HTTPS", "Public application endpoint", "open"),
            ServiceResult(3389, "RDP", "Management service", "open"),
        ]
        return resolved, results

    resolved = resolve_host(raw_target)
    results: List[ServiceResult] = []
    for port, name, exposure in WHITELISTED_PORTS:
        reachable = check_port(resolved, port)
        results.append(ServiceResult(port, name, exposure, reachable))
    return resolved, results
