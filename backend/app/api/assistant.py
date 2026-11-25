
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db, get_current_user
from backend.app.models.user import User
from backend.app.models.scan import Scan
from backend.app.schemas.rag import (
    AssistantRequest,
    AssistantResponse,
)
from backend.app.services.rag_service import (
    answer_question,
    answer_scan_question,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/assistant",
    tags=["Cybersecurity Assistant"],
)


@router.post(
    "/ask",
    response_model=AssistantResponse,
)
def ask_assistant(
    data: AssistantRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return answer_question(
            question=data.question,
            top_k=data.top_k,
        )

    except FileNotFoundError as exc:
        logger.error(
            "Cybersecurity knowledge base is unavailable: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cybersecurity knowledge base is not available.",
        ) from exc

    except RuntimeError as exc:
        logger.error(
            "Cybersecurity assistant service failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cybersecurity assistant service is unavailable.",
        ) from exc

    except ValueError as exc:
        logger.warning(
            "Invalid assistant operation: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The assistant could not process the request.",
        ) from exc


@router.post(
    "/ask-scan/{scan_id}",
    response_model=AssistantResponse,
)
def ask_about_scan(
    scan_id: int,
    data: AssistantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scan = (
        db.query(Scan)
        .filter(
            Scan.id == scan_id,
            Scan.user_id == current_user.id,
        )
        .first()
    )

    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found.",
        )

    try:
        return answer_scan_question(
            question=data.question,
            scan=scan,
            top_k=data.top_k,
        )

    except RuntimeError as exc:
        logger.error(
            "Scan assistant service failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The cybersecurity assistant is temporarily unavailable.",
        ) from exc

    except ValueError as exc:
        logger.warning(
            "Invalid scan assistant operation: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The assistant could not process the request.",
        ) from exc
