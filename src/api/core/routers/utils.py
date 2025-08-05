# -*- coding: utf-8 -*-

from typing import Optional

from pydantic import IPvAnyAddress
from fastapi import APIRouter, Request, Query, Depends


from api.core import utils
from api.config import config
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
    responses={401: {}, 422: {}, 503: {}},
    dependencies=[Depends(auth_api_key)],
)
def get_health(
    request: Request,
    device_ips: Optional[list[IPvAnyAddress]] = Query(default=None),
):
    _status_code = 200
    _message = "Everything is OK."
    _data = {
        "checks": {
            "api": {"status": "OK", "message": "API is up."},
            "devices": [],
        },
        "timestamp": utils.now_utc_dt(),
    }

    if not device_ips:
        device_ips = config.challenge.device_ips

    for _ip in device_ips:
        _device = {}
        if utils.is_reachable(host=str(_ip)):
            _device["status"] = "OK"
            _device["message"] = f"Device with '{_ip}' IP is reachable."
            _device["ip"] = str(_ip)
        else:
            _status_code = 503
            _message = "Some devices are not reachable!"
            _device["status"] = "FAIL"
            _device["message"] = f"Device with '{_ip}' IP is not reachable!"
            _device["ip"] = str(_ip)

        _data["checks"]["devices"].append(_device)

    return BaseResponse(
        request=request,
        content=_data,
        status_code=_status_code,
        message=_message,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


__all__ = ["router"]
