# -*- coding: utf-8 -*-
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from api.config import config


def verify_token(authorization: str = Depends(HTTPBearer())):
    if authorization.credentials != config.api.security.auth_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


__all__ = ["verify_token"]
