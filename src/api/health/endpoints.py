import json

from fastapi import APIRouter, status
from pydantic import BaseModel

from core.settings import settings
from core.utils.logger import logger
from core.utils.responses import EnvelopeResponse

router = APIRouter(tags=["Health Check"])

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health service",
    response_model=EnvelopeResponse,
    tags=["Health"],
)
def health_check() -> EnvelopeResponse:
    logger.info("Health")
    result = {
        "status": "ok",
        "message": "The service is online and functioning properly.",
        "timestamp": settings.TIMESTAP,
    }
    return EnvelopeResponse(
        errors=None,
        body=result,
        response_code=status.HTTP_200_OK,
        success=True,
        successful=True,
        message="The service is online and functioning properly.",
    )