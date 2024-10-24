
import json
from fastapi import Request, status

from api.webhooks.v1.typeform.presentation.dtos import ResponseTypeformDto
from core.utils.logger import logger
from core.utils.responses import (
    EnvelopeResponse,
)

from .routers import router


@router.post(
    "",
    summary="Recibe un nuevo registro de typefrom",
    status_code=status.HTTP_201_CREATED,
    response_model=EnvelopeResponse,
)
async def create(
    request: Request,
    payload: ResponseTypeformDto,
):
    logger.info("Create Code")

    print(json.dumps(payload.model_dump(), indent=2))

    return EnvelopeResponse(
        data=payload.model_dump(),
        success=True,
        response_code=status.HTTP_201_CREATED,
    )
