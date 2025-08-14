# -*- coding: utf-8 -*-

import os
import pathlib

import requests
from pydantic import validate_call
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.core import utils
from api.config import config

from .schemas import Fingerprinter


_API_DIR = str(pathlib.Path(__file__).resolve().parents[2])


@validate_call
def save_fingerprinter(fingerprinter: Fingerprinter) -> None:

    _fp_js_path = os.path.join(_API_DIR, "static", "js", "fingerprinter.js")
    utils.remove_file(_fp_js_path)

    with open(_fp_js_path, "w") as _file:
        _file.write(fingerprinter.fingerprinter_js)

    return


@validate_call(config={"arbitrary_types_allowed": True})
def get_web(request: Request) -> HTMLResponse:

    _templates = Jinja2Templates(directory=os.path.join(_API_DIR, "templates", "html"))
    _html_response: HTMLResponse = _templates.TemplateResponse(
        request=request,
        name="index.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
    return _html_response


@validate_call
def submit_fingerprint(order_id: int, fingerprint: str) -> None:

    _endpoint = "/_fingerprint"
    _base_url = str(config.challenge.base_url).rstrip("/")

    _url = f"{_base_url}{_endpoint}"
    _headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": config.challenge.api_key.get_secret_value(),
    }
    _payload = {"order_id": order_id, "fingerprint": fingerprint}
    _response = requests.post(_url, headers=_headers, json=_payload)
    _response.raise_for_status()

    return


__all__ = [
    "save_fingerprinter",
    "get_web",
    "submit_fingerprint",
]
