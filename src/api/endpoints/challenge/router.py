# -*- coding: utf-8 -*-

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, HTTPException, Request, Depends, Query, Body

from api.core.constants import ErrorCodeEnum, ALPHANUM_HYPHEN_REGEX
from api.core.schemas import BaseResPM
from api.core.responses import BaseResponse
from api.core.exceptions import BaseHTTPException
from api.core.dependencies.auth import auth_api_key
from api.logger import logger

from . import service
from .schemas import Fingerprinter


router = APIRouter(tags=["Challenge"])


@router.post(
    "/_fp-js",
    summary="Save miner fingerprinter",
    description="This endpoint retrieves the miner fingerprinter from the challenger container.",
    response_model=BaseResPM,
    responses={401: {}, 422: {}},
    dependencies=[Depends(auth_api_key)],
)
def post_fingerprinter(request: Request, fingerprinter: Fingerprinter):

    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Saving miner fingerprinter...")
    try:
        service.save_fingerprinter(request_id=_request_id, fingerprinter=fingerprinter)
        logger.success(f"[{_request_id}] - Successfully saved miner fingerprinter.")
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"[{_request_id}] - Failed to save miner fingerprinter!")
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.INTERNAL_SERVER_ERROR,
            message="Failed to save miner fingerprinter!",
        )

    _response = BaseResponse(
        request=request,
        message="Successfully saved miner fingerprinter.",
    )
    return _response


@router.get(
    "/web",
    summary="Serves the webpage",
    description="This endpoint serves the webpage for the challenge.",
    responses={422: {}},
    response_class=HTMLResponse,
)
def get_web(request: Request, order_id: int = Query(..., gt=0, lt=1000000)):

    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Serving webpage for order ID {order_id}...")
    try:
        _html_response = service.get_web(request=request, order_id=order_id)
        logger.success(
            f"[{_request_id}] - Successfully served webpage for order ID {order_id}."
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception(
            f"[{_request_id}] - Failed to serve webpage for order ID {order_id}!"
        )
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.INTERNAL_SERVER_ERROR,
            message="Failed to serve webpage!",
        )

    return _html_response


@router.post(
    "/fingerprint",
    summary="Submit the fingerprint",
    description="This endpoint receives the fingerprint data and submit it to challenger service.",
    response_model=BaseResPM,
    responses={422: {}},
)
def post_fingerprint(
    request: Request,
    order_id: int = Body(..., gt=0, lt=1000000),
    fingerprint: str = Body(
        ..., min_length=1, max_length=128, pattern=ALPHANUM_HYPHEN_REGEX
    ),
):

    request_id = request.state.request_id
    logger.info(f"[{request_id}] - Submitting fingerprint for order ID {order_id}...")
    try:
        service.submit_fingerprint(
            request_id=request_id, order_id=order_id, fingerprint=fingerprint
        )
        logger.success(
            f"[{request_id}] - Successfully submitted fingerprint for order ID {order_id}."
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception(
            f"[{request_id}] - Failed to submit fingerprint for order ID {order_id}!"
        )
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.INTERNAL_SERVER_ERROR,
            message="Failed to submit fingerprint!",
        )

    _response = BaseResponse(
        request=request,
        message="Successfully submitted fingerprint.",
    )
    return _response


__all__ = [
    "router",
]
