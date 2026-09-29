import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from pydantic import ValidationError

from app.schemas import ScanCreateRequest
from app.services.risk_engine import build_finding_for_service
from app.services.detection_engine import run_detections


class FakeEvent:
    def __init__(self, id, event_type, timestamp, user=None, asset=None, source="test", event_code=None):
        self.id = id
        self.event_type = event_type
        self.timestamp = timestamp
        self.user = user
        self.asset = asset
        self.source = source
        self.event_code = event_code or id


def test_valid_hostname_target():
    req = ScanCreateRequest(target="healthcare.example.org")
    assert req.target == "healthcare.example.org"


def test_valid_ip_target():
    req = ScanCreateRequest(target="192.168.1.10")
    assert req.target == "192.168.1.10"


def test_strips_scheme_for_validation_but_keeps_original():
    req = ScanCreateRequest(target="https://healthcare.example.org")
    assert req.target == "https://healthcare.example.org"


def test_invalid_target_rejected():
    with pytest.raises(ValidationError):
        ScanCreateRequest(target="not a valid target !!")


def test_empty_target_rejected():
    with pytest.raises(ValidationError):
        ScanCreateRequest(target="   ")


def test_risk_engine_known_service():
    finding = build_finding_for_service("SSH")
    assert finding["risk"] == "HIGH"
    assert "controls" in finding["recommended_controls"][0].lower() or len(finding["recommended_controls"]) > 0


def test_risk_engine_unknown_service_defaults_to_info():
    finding = build_finding_for_service("FTP")
    assert finding["risk"] == "INFO"


def test_detection_rule1_fires_on_recovery_code_event():
    events = [FakeEvent("1", "recovery-code usage", datetime(2026, 1, 1, 8, 24), user="admin01")]
    detections = run_detections(events)
    assert any(d.rule_id == "RULE-1" for d in detections)


def test_detection_rule4_fires_on_full_chain():
    events = [
        FakeEvent("1", "recovery-code usage", datetime(2026, 1, 1, 8, 24), user="admin01"),
        FakeEvent("2", "sensitive resource access", datetime(2026, 1, 1, 9, 5), user="admin01"),
        FakeEvent("3", "suspicious outbound transfer", datetime(2026, 1, 1, 13, 15), user="admin01"),
    ]
    detections = run_detections(events)
    assert any(d.rule_id == "RULE-4" for d in detections)


def test_detection_no_false_positive_on_benign_events():
    events = [FakeEvent("1", "configuration change", datetime(2026, 1, 1, 15, 0))]
    detections = run_detections(events)
    assert all(d.rule_id != "RULE-4" for d in detections)
