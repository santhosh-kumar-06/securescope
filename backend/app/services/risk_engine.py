"""
Risk engine — static, auditable mapping from service -> risk profile.

Deliberately NOT a vulnerability scanner: it never claims a "confirmed
vulnerability" from a bare open-port observation. It reports:
  - OPEN_SERVICE        -> the port responded to a connect attempt
  - SECURITY_EXPOSURE    -> the general risk category this kind of service
                            represents for the business, given exposure
A CONFIRMED_VULNERABILITY finding_type is reserved for cases with concrete
version/config evidence, which this training tool does not fabricate.
"""

from typing import Dict, List

RISK_PROFILES: Dict[str, dict] = {
    "SSH": {
        "risk": "HIGH",
        "reason": "Administrative access service requires strict network and identity controls.",
        "business_impact": "If misused, provides a path to administrative control over hosts supporting clinical systems.",
        "detection_considerations": "Monitor authentication attempts, source IP reputation, and off-hours administrative logins.",
        "recommended_controls": [
            "Restrict access to approved networks.",
            "Use strong authentication.",
            "Use phishing-resistant MFA where appropriate.",
            "Centralize authentication logging.",
            "Disable unnecessary access.",
        ],
    },
    "RDP": {
        "risk": "HIGH",
        "reason": "Remote desktop exposure can provide a valuable administrative access path if authentication or network controls are weak.",
        "business_impact": "A compromised RDP session can lead toward systems supporting patient records and clinical scheduling.",
        "detection_considerations": "Monitor for anomalous logon sources, brute-force patterns, and session hijacking indicators.",
        "recommended_controls": [
            "Restrict RDP to approved management paths.",
            "MFA.",
            "Network Level Authentication.",
            "Patch management.",
            "Authentication monitoring.",
        ],
    },
    "DNS": {
        "risk": "MEDIUM",
        "reason": "An internal resolver reachable from a broad network segment increases exposure.",
        "business_impact": "Can be leveraged as a discovery or covert-channel vector if not monitored.",
        "detection_considerations": "Monitor for unusual query volume, anomalous domains, and DNS tunneling indicators.",
        "recommended_controls": [
            "Restrict resolver access.",
            "Use approved network paths.",
            "Monitor DNS activity.",
            "Apply secure configuration.",
        ],
    },
    "HTTPS": {
        "risk": "MEDIUM",
        "reason": "Public application endpoint requires secure TLS configuration, application monitoring, and secure configuration.",
        "business_impact": "The primary path patients and staff use to reach clinical scheduling and portal systems.",
        "detection_considerations": "Monitor for unusual request patterns, authentication anomalies, and abnormal outbound web traffic.",
        "recommended_controls": [
            "Secure TLS configuration.",
            "Application logging.",
            "Vulnerability management.",
            "Monitor unusual web activity.",
        ],
    },
}


def build_finding_for_service(service_name: str) -> dict:
    profile = RISK_PROFILES.get(service_name)
    if not profile:
        profile = {
            "risk": "INFO",
            "reason": "Service observed; no predefined risk profile in this training scope.",
            "business_impact": "Unknown.",
            "detection_considerations": "General network and endpoint monitoring recommended.",
            "recommended_controls": ["Inventory the service and assign an owner."],
        }
    return {
        "title": f"{service_name} exposure",
        "risk": profile["risk"],
        "reason": profile["reason"],
        "business_impact": profile["business_impact"],
        "detection_considerations": profile["detection_considerations"],
        "recommended_controls": profile["recommended_controls"],
        "finding_type": "SECURITY_EXPOSURE",
    }
