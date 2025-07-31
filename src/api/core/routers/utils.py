# -*- coding: utf-8 -*-

from typing import Optional

from pydantic import IPvAnyAddress
from fastapi import APIRouter, Request, Query, Depends

from api.core.schemas import BaseResPM
from api.core.responses import BaseResponse
from api.core.dependencies.auth import auth_api_key


router = APIRouter(tags=["Utils"])


@router.get(
    "/",
    summary="Base",
    description="Base path for all API endpoints.",
    response_model=BaseResPM,
)
async def get_base(request: Request):
    return BaseResponse(request=request, message="Welcome to the REST API service!")


@router.get(
    "/ping",
    summary="Ping",
    description="Check if the service is up and running.",
    response_model=BaseResPM,
)
async def get_ping(request: Request):
    return BaseResponse(
        request=request, message="Pong!", headers={"Cache-Control": "no-cache"}
    )


@router.get(
    "/health",
    summary="Health",
    description="Check health of all related backend services.",
    response_model=BaseResPM,
    dependencies=[Depends(auth_api_key)],
)
async def get_health(
    request: Request, device_ips: Optional[list[IPvAnyAddress]] = Query(default=None)
):
    _message = "Everything is OK."
    _data = {"api": {"message": "API is up.", "is_alive": True}}

    return BaseResponse(
        request=request,
        content=_data,
        message=_message,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


__all__ = ["router"]
