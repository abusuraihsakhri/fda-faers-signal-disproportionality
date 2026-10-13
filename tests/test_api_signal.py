"""API schema and authorization regressions."""
import pytest
from pydantic import ValidationError


def test_signal_endpoint_and_validation():
    from agents.api import SignalCounts, api_signal
    from fastapi import HTTPException
    r = api_signal(SignalCounts(a=30, b=70, c=20, d=880))
    assert r["prr"] == pytest.approx(13.5)
    assert r["evans_screening_flag"] is True
    with pytest.raises(ValidationError):
        SignalCounts(a=True, b=1, c=1, d=1)
    with pytest.raises(ValidationError):
        SignalCounts(a=-1, b=1, c=1, d=1)
    with pytest.raises(HTTPException) as error:
        api_signal(SignalCounts(a=0, b=0, c=0, d=0))
    assert error.value.status_code == 422


def test_audit_logs_fail_closed(monkeypatch):
    from agents.api import api_audit_logs
    from fastapi import HTTPException
    from starlette.requests import Request

    def request(bearer=""):
        return Request({"type": "http", "headers":
                        [(b"authorization", bearer.encode("utf-8"))]})

    monkeypatch.delenv("AUDIT_VIEW_TOKEN", raising=False)
    with pytest.raises(HTTPException) as denied:
        api_audit_logs(request())
    assert denied.value.status_code == 403

    monkeypatch.setenv("AUDIT_VIEW_TOKEN", "random-protected-access-token")
    with pytest.raises(HTTPException) as denied:
        api_audit_logs(request("Bearer wrong-token"))
    assert denied.value.status_code == 403
    assert api_audit_logs(request("Bearer random-protected-access-token"))["verified"] is True
