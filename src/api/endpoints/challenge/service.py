# -*- coding: utf-8 -*-

import pathlib

from pydantic import validate_call
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.config import config

_src_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()


@validate_call(config={"arbitrary_types_allowed": True})
def get_web(request: Request) -> HTMLResponse:
    """Get the web interface for the challenge"""

    templates = Jinja2Templates(directory=str(_src_dir / "templates"))
    html_response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"challenger_url": config.challenger_url},
    )
    return html_response
