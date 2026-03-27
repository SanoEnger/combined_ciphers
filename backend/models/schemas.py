from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


Mode = Literal["substitution", "transposition", "sub_then_trans", "trans_then_sub"]
Operation = Literal["encrypt", "decrypt"]


class ProcessRequest(BaseModel):
    mode: Mode
    operation: Operation
    text: str = Field(..., min_length=1, description="Исходный текст или шифртекст")
    sub_key: str | None = Field(None, description="Ключ для лозунговой замены")
    m: int | None = Field(None, ge=1, description="Число строк матрицы")
    n: int | None = Field(None, ge=1, description="Число столбцов матрицы")

    @model_validator(mode="after")
    def check_fields_for_mode(self) -> ProcessRequest:
        if self.mode in ("substitution", "sub_then_trans", "trans_then_sub"):
            if not (self.sub_key and self.sub_key.strip()):
                raise ValueError("Укажите непустой ключ (sub_key) для режима с заменой")
        if self.mode in ("transposition", "sub_then_trans", "trans_then_sub"):
            if self.m is None or self.n is None:
                raise ValueError("Укажите размер матрицы m и n для режима с перестановкой")
        return self


class StepPayload(BaseModel):
    step: int
    title: str
    description: str
    text: str
    visualization: dict[str, Any] = Field(default_factory=dict)


class ProcessResponse(BaseModel):
    steps: list[dict[str, Any]]
    final_text: str
