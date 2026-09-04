"""
Automated Pytest Test Suite for Fda Faers Signal Disproportionality.
Domain: Pharmacovigilance & Drug Safety Signal Detection
Standard: WHO-UMC & FDA FAERS Signal Detection
"""
import os
import sys
from pathlib import Path

# Set audit key before any agent imports
if not os.getenv("AUDIT_SECRET_KEY"):
    os.environ["AUDIT_SECRET_KEY"] = "test-suite-audit-key-2026-long-enough"

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567 or test@example.com")
    assert "555-123-4567" not in redacted
    assert "test@example.com" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_input_validation_string_length():
    """Test that string fields enforce maximum length constraints."""
    # Valid input should work
    p = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=10.0)
    assert p.task_id == "T1"

    # Exceeding max_length for task_id should raise validation error
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="X" * 200, target_identifier="KEY-01", primary_metric=10.0)

    # Exceeding max_length for status_descriptor should raise validation error
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=10.0,
                         status_descriptor="X" * 100)


def test_input_validation_control_chars():
    """Test that control characters are rejected in string fields."""
    with pytest.raises(Exception):
        SystemTaskPayload(task_id="T1\x00\x01", target_identifier="KEY-01", primary_metric=10.0)


def test_input_validation_strips_whitespace():
    """Test that string fields are stripped of leading/trailing whitespace."""
    p = SystemTaskPayload(task_id="  T1  ", target_identifier="  KEY-01  ", primary_metric=10.0)
    assert p.task_id == "T1"
    assert p.target_identifier == "KEY-01"


def test_audit_trail_requires_secret_key():
    """Test that AuditTrail requires a secret key."""
    # Clear any existing env var
    original_key = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        with pytest.raises(SecurityException):
            AuditTrail()
    finally:
        # Restore original key
        if original_key:
            os.environ["AUDIT_SECRET_KEY"] = original_key


def test_audit_trail_weak_key_rejected():
    """Test that weak secret keys are rejected."""
    os.environ["AUDIT_SECRET_KEY"] = "short"
    try:
        with pytest.raises(SecurityException):
            AuditTrail()
    finally:
        # Restore working key
        os.environ["AUDIT_SECRET_KEY"] = "test-key-that-is-long-enough-2026"


def test_audit_trail_with_valid_key():
    """Test that AuditTrail works with a valid key."""
    os.environ["AUDIT_SECRET_KEY"] = "this-is-a-valid-secret-key-2026"
    try:
        trail = AuditTrail()
        entry = trail.log("test", "test_tier", "TEST_EVENT", {"data": "value"})
        assert entry["audit_id"].startswith("AUDIT-")
        assert trail.verify_integrity() is True
    finally:
        os.environ["AUDIT_SECRET_KEY"] = "test-key-that-is-long-enough-2026"


def test_batch_csv_processing(tmp_path):
    """Test batch CSV processing functionality."""
    import csv

    # Create a test CSV file
    input_csv = tmp_path / "test_input.csv"
    with open(input_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["task_id", "target_identifier", "primary_metric", "secondary_metric", "is_critical_flag", "status_descriptor"])
        writer.writerow(["BATCH-01", "TARGET-B1", "28.4", "14.2", "False", "DISCORDANT"])
        writer.writerow(["BATCH-02", "TARGET-B2", "12.0", "4.1", "False", "NOMINAL"])

    output_csv = tmp_path / "test_output.csv"
    result = main(["batch", "-i", str(input_csv), "-o", str(output_csv)])
    assert result == 0
    assert output_csv.exists()

    with open(output_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 2
    assert "overall_urgency" in rows[0]
