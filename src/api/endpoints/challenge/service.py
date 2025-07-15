# -*- coding: utf-8 -*-

import pathlib

from pydantic import validate_call
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


_src_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()


@validate_call(config={"arbitrary_types_allowed": True})
def get_web(request: Request) -> HTMLResponse:
    """Get the web interface for the challenge"""

    _templates = Jinja2Templates(directory=(_src_dir / "api" / "templates"))
    _html_response = _templates.TemplateResponse(request=request, name="index.html")

    return _html_response
