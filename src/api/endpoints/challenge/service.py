# -*- coding: utf-8 -*-

import os
import pathlib

import requests
from pydantic import validate_call
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.core.constants import ErrorCodeEnum
from api.core import utils
from api.config import config
from api.core.exceptions import BaseHTTPException
from api.logger import logger

from .schemas import Fingerprinter


_API_DIR = str(pathlib.Path(__file__).resolve().parents[2])


@validate_call
def save_fingerprinter(request_id: str, fingerprinter: Fingerprinter) -> None:

    logger.info(f"[{request_id}] - Saving fingerprinter...")
    try:
        _fp_js_path = os.path.join(_API_DIR, "static", "js", "fingerprinter.js")
        utils.remove_file(_fp_js_path)

        with open(_fp_js_path, "w") as _file:
            _file.write(fingerprinter.fingerprinter_js)

        logger.info(f"[{request_id}] - Successfully saved fingerprinter.js.")
    except Exception:
        logger.exception(f"[{request_id}] - Failed to to save fingerprinter.js!")
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.INTERNAL_SERVER_ERROR,
            message="Failed to save fingerprinter.js!",
        )

    return


@validate_call(config={"arbitrary_types_allowed": True})
def get_web(request: Request, order_id: int) -> HTMLResponse:

    _request_id = request.state.request_id
    _html_response: HTMLResponse

    logger.info(f"[{_request_id}] - Rendering HTML template for order ID {order_id}...")
    try:
        _templates = Jinja2Templates(
            directory=os.path.join(_API_DIR, "templates", "html")
        )
        _html_response = _templates.TemplateResponse(request=request, name="index.html")
        logger.info(
            f"[{_request_id}] - Successfully rendered HTML template for order ID {order_id}."
        )
    except Exception:
        logger.exception(
            f"[{_request_id}] - Failed to render HTML template for order ID {order_id}!"
        )
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.INTERNAL_SERVER_ERROR,
            message="Failed to render HTML template!",
        )

    return _html_response


@validate_call
def submit_fingerprint(request_id: str, order_id: int, fingerprint: str) -> None:

    logger.info(f"[{request_id}] - Submitting fingerprint for order ID {order_id}...")
    try:
        _endpoint = "/fingerprint"
        _base_url = str(config.challenge.base_url)
        if _base_url.endswith("/"):
            _base_url = _base_url.rstrip("/")

        _url = f"{_base_url}{_endpoint}"
        _headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": config.challenge.api_key.get_secret_value(),
        }
        _payload = {"order_id": order_id, "fingerprint": fingerprint}
        _response = requests.post(_url, headers=_headers, json=_payload)
        _response.raise_for_status()

        logger.info(
            f"[{request_id}] - Successfully submitted fingerprint for order ID {order_id}."
        )
    except Exception:
        logger.exception(
            f"[{request_id}] - Failed to submit fingerprint for order ID {order_id}!"
        )
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.INTERNAL_SERVER_ERROR,
            message="Failed to submit fingerprint!",
        )

    return


__all__ = [
    "save_fingerprinter",
    "get_web",
    "submit_fingerprint",
]
