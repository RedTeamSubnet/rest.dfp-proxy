# -*- coding: utf-8 -*-
import pathlib

from pydantic import validate_call
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

_src_dir = pathlib.Path(__file__).parent.parent.resolve()
static_path = _src_dir / "templates" / "static"


@validate_call(config={"arbitrary_types_allowed": True})
def add_mounts(app: FastAPI) -> None:
    """Add mounts to FastAPI app.

    Args:
        app (FastAPI): FastAPI app instance.
    """

    ## Add mounts here
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    return


__all__ = ["add_mounts"]
