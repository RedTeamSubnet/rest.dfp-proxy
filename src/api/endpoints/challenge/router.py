# -*- coding: utf-8 -*-

import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from api.logger import logger
from api.config import config

from . import service

# router = APIRouter(prefix="/", tags=["Tasks"])
router = APIRouter(tags=["Challenge"])


@router.get(
    "/_web",
    summary="Serves the webpage",
    description="This endpoint serves the webpage for the challenge.",
    response_class=HTMLResponse,
    responses={429: {}},
)
def get_web(request: Request):

    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Getting webpage...")

    _html_response: HTMLResponse
    try:
        _html_response = service.get_web(request=request)

        logger.success(f"[{_request_id}] - Successfully got the webpage.")
    except Exception as err:
        if isinstance(err, HTTPException):
            raise

        logger.error(
            f"[{_request_id}] - Failed to get the webpage!",
        )
        raise

    return _html_response


@router.post(
    "/sync-fp",
    summary="Syncs the fingerprint",
    description="This endpoint receives the fingerprint data from the client and sends it to another server.",
    responses={200: {}, 500: {}},
)
async def sync_fp(request: Request):
    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Sending fingerprint...")

    try:
        payload = await request.json()
        logger.info(f"[{_request_id}] - Sending fingerprint data: {payload}")
        _url = config.challenger_url

        try:
            requests.post(
                url=_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {config.api.security.auth_key}",
                },
            )
        except requests.RequestException as e:
            logger.error(f"[{_request_id}] - Request failed: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to send fingerprint data"
            )

        logger.info(f"[{_request_id}] - Fingerprint data received successfully.")
    except Exception as err:
        logger.error(f"[{_request_id}] - Failed to send fingerprint: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Fingerprint received successfully."}


__all__ = [
    "router",
    "get_web",
    "sync_fp",
]
