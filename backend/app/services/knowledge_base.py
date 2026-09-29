"""Static defensive knowledge base, scoped strictly to Problem 4's techniques."""

ATTACK_TECHNIQUES = [
    {
        "name": "Impersonation",
        "mitre_ref": "T1656",
        "description": (
            "An attacker may impersonate a trusted person (e.g. an executive) to "
            "persuade staff to disclose sensitive authentication or recovery information."
        ),
        "detection_indicators": [
            "Unusual recovery-code use.",
            "Unexpected authentication reset.",
            "Suspicious identity-verification request.",
            "Unusual privileged-account activity.",
        ],
        "defensive_controls": [
            "Identity verification.",
            "Out-of-band verification.",
            "Phishing-resistant MFA.",
            "Security awareness.",
            "Recovery-code protection.",
        ],
        "affected_assets": ["Identity systems", "Help desk / support workflows"],
    },
    {
        "name": "Account Discovery",
        "mitre_ref": "T1087",
        "description": (
            "Attackers may identify available accounts, roles, or service accounts "
            "to understand which permissions would be useful to obtain or abuse."
        ),
        "detection_indicators": [
            "Unusual account enumeration.",
            "Unexpected identity queries.",
            "Abnormal service-account discovery.",
        ],
        "defensive_controls": [
            "Least privilege.",
            "Restrict directory access.",
            "Monitor account enumeration.",
            "Minimize exposed identity information.",
        ],
        "affected_assets": ["Identity systems", "Directory services"],
    },
    {
        "name": "Web Protocols",
        "mitre_ref": "T1071.001",
        "description": (
            "Web protocols can be used as a communication layer, so proxy, DNS, "
            "endpoint, and application telemetry can be important for detection."
        ),
        "detection_indicators": [
            "Unusual destinations.",
            "Abnormal request patterns.",
            "Unexpected outbound web traffic.",
        ],
        "defensive_controls": [
            "Proxy monitoring.",
            "DNS monitoring.",
            "Application logging.",
            "Endpoint telemetry.",
        ],
        "affected_assets": ["Public application endpoint", "Clinical scheduling system"],
    },
    {
        "name": "Exfiltration Over C2 Channel",
        "mitre_ref": "T1041",
        "description": (
            "The scenario contains a controlled transfer attempt through an "
            "attacker-controlled communication path."
        ),
        "detection_indicators": [
            "Unusual outbound volume.",
            "Unknown destinations.",
            "Abnormal transfer timing.",
            "Data transfer inconsistent with normal behavior.",
        ],
        "defensive_controls": [
            "Egress monitoring.",
            "Destination allowlisting where appropriate.",
            "Data-transfer anomaly detection.",
            "Network segmentation.",
        ],
        "affected_assets": ["Patient records system", "Clinical scheduling system"],
    },
]

DEFENSE_RECOMMENDATIONS = [
    ("Asset & Exposure Management", "Inventory internet-facing services."),
    ("Asset & Exposure Management", "Assign asset owners."),
    ("Asset & Exposure Management", "Review exposure regularly."),
    ("Identity & Access Management", "Enforce least privilege."),
    ("Identity & Access Management", "Require unique credentials per user."),
    ("Identity & Access Management", "Use phishing-resistant MFA."),
    ("Identity & Access Management", "Perform immediate offboarding on role change/departure."),
    ("Identity & Access Management", "Require independent identity verification for recovery actions."),
    ("Secure Configuration", "Restrict traffic to approved network paths."),
    ("Secure Configuration", "Enable centralized logging."),
    ("Secure Configuration", "Use encryption in transit and at rest."),
    ("Secure Configuration", "Restrict administration to approved protocols."),
    ("Secure Configuration", "Apply deny-by-default network access."),
    ("Vulnerability & Vendor Management", "Prioritize remediation based on exposure and business impact."),
    ("Vulnerability & Vendor Management", "Require supplier security notifications."),
    ("Vulnerability & Vendor Management", "Require appropriate security attestations from vendors."),
    ("Detection & Response", "Centralize logs across identity, network, and endpoint sources."),
    ("Detection & Response", "Monitor for anomalous access patterns."),
    ("Detection & Response", "Monitor for unusual data-transfer behavior."),
    ("Detection & Response", "Regularly test incident-response playbooks."),
    ("Resilience & Recovery", "Maintain isolated, tested backups."),
    ("Resilience & Recovery", "Test restoration procedures."),
    ("Resilience & Recovery", "Verify recovery does not reintroduce the original weakness."),
]

BUSINESS_IMPACT_ASSETS = [
    {"name": "Patient records", "note": "Confidentiality and integrity of clinical history."},
    {"name": "Clinical scheduling", "note": "Availability of appointment and care-coordination systems."},
    {"name": "Administrative systems", "note": "Billing, HR, and operational continuity."},
    {"name": "Identity systems", "note": "Trust anchor for every other access decision."},
]
