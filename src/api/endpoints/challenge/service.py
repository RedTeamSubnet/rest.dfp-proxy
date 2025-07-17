# -*- coding: utf-8 -*-
import os
import httpx
import pathlib
import requests

from fastapi import Request
from pydantic import validate_call
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates

from api.config import config
from api.logger import logger
from api.endpoints.challenge.schemas import Fingerprinter

_src_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()


@validate_call(config={"arbitrary_types_allowed": True})
def get_web(request: Request) -> HTMLResponse:
    """Get the web interface for the challenge"""

    templates = Jinja2Templates(directory=str(_src_dir / "templates"))
    html_response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"sync_url": config.sync_url},
    )
    return html_response


@validate_call(config={"arbitrary_types_allowed": True})
async def sync_fp(request: Request):
    """
    Asynchronously syncs the fingerprint by forwarding the request body
    to the challenger service.
    """
    request_id = request.state.request_id
    logger.info(f"[{request_id}] - Syncing fingerprint with challenger...")

    try:
        payload = await request.json()
        challenger_url = (
            f"http://{config.challenger_hostname}:{config.challenger_port}/get-fp"
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=challenger_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()

        logger.success(f"[{request_id}] - Successfully synced fingerprint.")

    except httpx.RequestError as err:
        logger.error(
            f"[{request_id}] - Failed to sync fingerprint with challenger: {err}"
        )
        raise HTTPException(
            status_code=503, detail="Challenger service is unavailable."
        )
    except Exception as err:
        logger.error(
            f"[{request_id}] - An unexpected error occurred during sync: {err}"
        )
        raise HTTPException(status_code=500, detail="Failed to sync fingerprint.")


@validate_call(config={"arbitrary_types_allowed": True})
def write_fpr(request: Request, fingerprinter: Fingerprinter):
    """Sync the fingerprint with the challenger container"""

    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Syncing fingerprint with challenger...")

    try:
        _fingerprinter_js_path = (
            _src_dir / "static" / "fingerprinter" / "fingerprinter.js"
        )
        _fingerprinter_js_content = fingerprinter.fingerprinter_js

        os.makedirs(_fingerprinter_js_path.parent, exist_ok=True)

        with open(_fingerprinter_js_path, "w") as _fingerprinter_js_file:
            _fingerprinter_js_file.write(_fingerprinter_js_content)

        logger.success(f"[{_request_id}] - Successfully synced fingerprint.")

    except requests.RequestException as err:
        logger.error(f"[{_request_id}] - Failed to sync fingerprint: {err}")
        raise HTTPException(status_code=500, detail="Failed to sync fingerprint")
