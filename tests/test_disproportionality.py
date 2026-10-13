"""Independent numerical and security regressions for 2x2 reporting statistics."""
import math
import pytest
from faers_sentinel.disproportionality import calculate_signal


def test_known_example_and_intervals():
    result = calculate_signal(30, 70, 20, 880)
    assert result["prr"] == pytest.approx(13.5)
    assert result["ror"] == pytest.approx(18.857142857142858)
    assert result["chi_square_yates"] == pytest.approx(140.4093567251462)
    assert result["ic_crude_log2_observed_expected"] == pytest.approx(math.log2(6))
    assert result["evans_screening_flag"] is True
    assert result["ror_ci95"][0] < result["ror"] < result["ror_ci95"][1]
    assert result["prr_ci95"][0] < result["prr"] < result["prr_ci95"][1]
    assert not result["continuity_correction_applied"]


def test_independence_and_low_counts():
    result = calculate_signal(10, 90, 20, 180)
    assert result["prr"] == pytest.approx(1)
    assert result["ror"] == pytest.approx(1)
    assert result["ic_crude_log2_observed_expected"] == pytest.approx(0)
    assert result["evans_screening_flag"] is False
    assert calculate_signal(2, 1, 1, 200)["evans_screening_flag"] is False


def test_zeros_are_explicitly_undefined_without_correction():
    result = calculate_signal(3, 0, 1, 100)
    assert result["prr"] is None
    assert result["ror"] is None
    assert result["ror_ci95"] is None
    assert result["continuity_correction_applied"] is False
    corrected = calculate_signal(3, 0, 1, 100, True)
    assert corrected["prr"] is not None
    assert corrected["ror"] is not None
    assert corrected["continuity_correction_applied"] is True
    assert corrected["evans_screening_flag"] is False


@pytest.mark.parametrize("counts", [
    (-1, 2, 3, 4), (1.5, 2, 3, 4), (True, 2, 3, 4),
    ("1", 2, 3, 4), (0, 0, 0, 0)
])
def test_invalid_counts(counts):
    with pytest.raises(ValueError):
        calculate_signal(*counts)


def test_cli_signal_output(capsys):
    from faers_sentinel.cli import main
    import json
    assert main(["signal", "--a", "30", "--b", "70", "--c", "20", "--d", "880"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["prr"] == pytest.approx(13.5)


def test_audit_chain_rejects_tampering():
    from agents.base import AuditTrail
    audit = AuditTrail(secret_key="isolated-test-key-with-adequate-length")
    audit.log("tester", "dev", "EVALUATE", {"input": "example"})
    assert audit.verify_integrity()
    audit.logs[0]["event_type"] = "ALTERED"
    assert not audit.verify_integrity()
    audit.logs[0]["event_type"] = "EVALUATE"
    assert audit.verify_integrity()
    audit.logs[0]["current_hash"] = "0" * 64
    assert not audit.verify_integrity()
