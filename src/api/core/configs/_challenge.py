# -*- coding: utf-8 -*-

from pydantic import Field, SecretStr, AnyHttpUrl, IPvAnyAddress
from pydantic_settings import SettingsConfigDict

from api.core.constants import ENV_PREFIX
from ._base import FrozenBaseConfig


class ChallengeConfig(FrozenBaseConfig):
    api_key: SecretStr = Field(..., min_length=8, max_length=128)
    base_url: AnyHttpUrl = Field(...)
    device_ips: list[IPvAnyAddress] = Field(default_factory=list)

    model_config = SettingsConfigDict(env_prefix=f"{ENV_PREFIX}CHALLENGE_")


__all__ = [
    "ChallengeConfig",
]
