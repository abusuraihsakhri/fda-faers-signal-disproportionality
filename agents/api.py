"""
FastAPI REST API Server for Fda Faers Signal Disproportionality.
"""
import os
import hmac
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from .base import AuditLogger, PHIGuard, SecurityException
from faers_sentinel.disproportionality import calculate_signal
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Fda Faers Signal Disproportionality API",
    description="Enterprise Distributed Component Platform (Pharmacovigilance (legacy operational telemetry))",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.exception_handler(SecurityException)
async def security_exception_handler(request: Request, exc: SecurityException):
    return JSONResponse(
        status_code=400,
        content={"error": "Security violation", "detail": str(exc)},
    )


@app.get("/", include_in_schema=False)
def browser_application():
    return FileResponse(Path(__file__).resolve().parents[1] / "web" / "index.html")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "fda-faers-signal-disproportionality", "domain": "Pharmacovigilance", "standard": "WHO-UMC & FDA FAERS Signal Detection", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()



class SignalCounts(BaseModel):
    a: int = Field(ge=0, le=10**12, strict=True)
    b: int = Field(ge=0, le=10**12, strict=True)
    c: int = Field(ge=0, le=10**12, strict=True)
    d: int = Field(ge=0, le=10**12, strict=True)
    continuity_correction: bool = False


@app.post("/api/signal")
def api_signal(req: SignalCounts):
    try:
        return calculate_signal(req.a, req.b, req.c, req.d, req.continuity_correction)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs(request: Request):
    # Never expose case identifiers and signed audit metadata anonymously.
    key = os.getenv("AUDIT_VIEW_TOKEN", "")
    supplied = request.headers.get("authorization", "")
    if not key or not hmac.compare_digest(supplied, "Bearer " + key):
        raise HTTPException(status_code=403, detail="Audit access is not configured or authorized.")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
