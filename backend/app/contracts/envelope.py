from typing import Any

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)
    hint: str | None = None


class SuccessEnvelope(BaseModel):
    data: dict[str, Any]
    meta: dict[str, Any]
    error: None = None


class ErrorEnvelope(BaseModel):
    data: None = None
    meta: dict[str, Any]
    error: ErrorBody
