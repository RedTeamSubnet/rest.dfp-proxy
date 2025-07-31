# -*- coding: utf-8 -*-

import pathlib

from pydantic import validate_call
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


_API_DIR = pathlib.Path(__file__).parent.resolve()
_STATIC_PATH = str(_API_DIR / "static")


@validate_call(config={"arbitrary_types_allowed": True})
def add_mounts(app: FastAPI) -> None:
    """Add mounts to FastAPI app.

    Args:
        app (FastAPI): FastAPI app instance.
    """

    ## Add mounts here
    app.mount("/static", StaticFiles(directory=_STATIC_PATH), name="static")

    return


__all__ = ["add_mounts"]
