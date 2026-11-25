
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
import csv
import io

from backend.app.models.scan import Scan
from backend.app.models.threat_indicator import ThreatIndicator
from backend.app.api.dependencies import get_db, get_current_user
from backend.app.models.user import User
from backend.app.schemas.scan import ScanRequest, ScanResponse
from backend.app.services.scan_service import create_scan

router = APIRouter(
    prefix="/api/v1/scans",
    tags=["URL Scanning"]
)


@router.post(
    "/",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED
)
def scan_url(
    data: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_scan(
        db=db,
        url=str(data.url),
        user_id=current_user.id
    )


@router.post(
    "/public",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED
)
def scan_url_public(
    data: ScanRequest,
    db: Session = Depends(get_db)
):
    """
    Public unauthenticated scan endpoint for guest users.
    Performs static feature extraction, ML inference, and threat intel lookup.
    Persists scan anonymously without associating a user_id.
    """
    return create_scan(
        db=db,
        url=str(data.url),
        user_id=None
    )


@router.get("/stats")
def get_scan_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggregates user-specific telemetry and global threat intelligence indicators.
    """
    user_scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.scanned_at.desc())
        .all()
    )

    total = len(user_scans)
    phishing = sum(1 for s in user_scans if s.verdict in ("phishing", "malware"))
    legitimate = sum(1 for s in user_scans if s.verdict == "legitimate")
    suspicious = sum(1 for s in user_scans if s.verdict == "suspicious")

    # Global active indicators count
    try:
        active_threats = (
            db.query(ThreatIndicator)
            .filter(ThreatIndicator.is_active == True)
            .count()
        )
    except Exception:
        active_threats = 0

    recent = [
        {
            "id": s.id,
            "url": s.url,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "verdict": s.verdict,
            "threat_type": s.threat_type,
            "scanned_at": s.scanned_at.isoformat() if s.scanned_at else None
        }
        for s in user_scans[:5]
    ]

    return {
        "total_scans": total,
        "phishing_scans": phishing,
        "legitimate_scans": legitimate,
        "suspicious_scans": suspicious,
        "active_threat_indicators": active_threats,
        "recent_scans": recent
    }


@router.get("/export")
def export_scans(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exports the authenticated user's scan history in JSON or CSV format.
    """
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.scanned_at.desc())
        .all()
    )

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "URL", "Risk Score", "Risk Level",
            "Verdict", "Threat Type", "Match Type", "Scanned At"
        ])
        for s in scans:
            writer.writerow([
                s.id,
                s.url,
                s.risk_score,
                s.risk_level,
                s.verdict,
                s.threat_type or "None",
                s.match_type or "None",
                s.scanned_at.isoformat() if s.scanned_at else ""
            ])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=phishguard_scans.csv"}
        )

    # Default JSON export
    data = [
        {
            "id": s.id,
            "url": s.url,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "verdict": s.verdict,
            "threat_type": s.threat_type,
            "match_type": s.match_type,
            "threat_sources": s.threat_sources,
            "explanation": s.explanation,
            "scanned_at": s.scanned_at.isoformat() if s.scanned_at else None
        }
        for s in scans
    ]
    return data


@router.get("/history", response_model=list[ScanResponse])
def get_scan_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.scanned_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return scans
