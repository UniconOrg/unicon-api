
import json
import requests
from fastapi import Request, status

from api.webhooks.v1.typeform.presentation.dtos import ResponseTypeformDto
from core.settings import settings
from core.utils.logger import logger
from core.utils.responses import (
    EnvelopeResponse,
)

from .routers import router

def upload_to_firebase(url, data):
    try:
        response = requests.put(f"{url}.json", json=data)
        if response.status_code == 200:
            print("Data uploaded successfully")
        else:
            print(f"Failed to upload data: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


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

    upload_to_firebase(url= f"{settings.FIREBASE_URL}/webhooks/typeform/{payload.event_id}", data=payload.model_dump())

    return EnvelopeResponse(
        data=payload.model_dump(),
        success=True,
        response_code=status.HTTP_201_CREATED,
    )
