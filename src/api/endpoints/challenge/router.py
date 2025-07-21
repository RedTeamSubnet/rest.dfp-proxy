# -*- coding: utf-8 -*-

import httpx
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, HTTPException, Request, Depends

from . import service
from api.logger import logger
from api.config import config
from api.endpoints.challenge.utils import verify_token
from api.endpoints.challenge.schemas import Fingerprinter

router = APIRouter(tags=["Challenge"])


@router.post(
    "/fpr",
    summary="Get Miner Fingerprinter",
    description="This endpoint retrieves the miner fingerprinter from the challenger container.",
    status_code=200,
    dependencies=[Depends(verify_token)],
)
def fpr(request: Request, fingerprinter: Fingerprinter) -> dict:
    """
    Receives and stores the miner fingerprinter data.
    """
    request_id = request.state.request_id
    logger.info(f"[{request_id}] - Storing miner fingerprinter...")

    try:
        service.write_fpr(request=request, fingerprinter=fingerprinter)
        logger.success(f"[{request_id}] - Successfully stored miner fingerprinter.")
        return {"status": "success", "message": "Fingerprinter stored."}
    except Exception as err:
        logger.error(f"[{request_id}] - Failed to store miner fingerprinter: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/_web",
    summary="Serves the webpage",
    description="This endpoint serves the webpage for the challenge.",
    response_class=HTMLResponse,
)
async def get_web(request: Request) -> HTMLResponse:
    """
    Serves the main challenge webpage.
    """
    request_id = request.state.request_id
    logger.info(f"[{request_id}] - Serving webpage...")

    try:
        html_response = service.get_web(request=request)
        logger.success(f"[{request_id}] - Successfully served webpage.")
        return html_response
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"[{request_id}] - Failed to serve webpage: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post(
    "/fp",
    summary="Syncs the fingerprint",
    description="This endpoint receives the fingerprint data and forwards it.",
)
async def sync_fp(request: Request) -> dict:
    """
    Receives fingerprint data and syncs it with another service.
    """
    request_id = request.state.request_id
    logger.info(f"[{request_id}] - Syncing fingerprint...")

    try:
        # Assumes service.sync_fp is an async function using httpx
        await service.async_fp(request=request)
        logger.success(f"[{request_id}] - Successfully synced fingerprint.")
        return {"status": "success", "message": "Fingerprint synced successfully."}
    except httpx.RequestError as err:
        logger.error(f"[{request_id}] - Failed to forward fingerprint data: {err}")
        raise HTTPException(
            status_code=502, detail="Bad Gateway: Upstream service failed."
        )
    except Exception as err:
        logger.error(f"[{request_id}] - Failed to sync fingerprint: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


__all__ = [
    "router",
]
