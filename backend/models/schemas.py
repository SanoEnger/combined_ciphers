from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


Mode = Literal["substitution", "transposition", "sub_then_trans", "trans_then_sub"]
Operation = Literal["encrypt", "decrypt"]
ReadMethod = Literal["row", "snake_left_right", "snake_right_left", "snake_top_down", "snake_bottom_up"]


class ProcessRequest(BaseModel):
    mode: Mode
    operation: Operation
    text: str = Field(..., min_length=1, description="Исходный текст или шифртекст")
    sub_key: str | None = Field(None, description="Лозунг для построения алфавита")
    period: int | None = Field(None, ge=1, le=33, description="Период (количество алфавитов замены)")
    m: int | None = Field(None, ge=1, description="Число строк матрицы")
    n: int | None = Field(None, ge=1, description="Число столбцов матрицы")
    read_method: ReadMethod = Field("row", description="Метод чтения матрицы")

    @model_validator(mode="after")
    def check_fields_for_mode(self) -> ProcessRequest:
        # Валидация для замены
        if self.mode in ("substitution", "sub_then_trans", "trans_then_sub"):
            if not (self.sub_key and self.sub_key.strip()):
                raise ValueError("Укажите непустой лозунг (sub_key) для режима с заменой")
            if self.period is None or self.period < 1:
                raise ValueError("Укажите период (period) для режима с заменой (от 1 до 33)")

        # Валидация для перестановки
        if self.mode in ("transposition", "sub_then_trans", "trans_then_sub"):
            if self.operation == "decrypt":
                # При расшифровании нужны m и n
                if self.m is None or self.n is None:
                    raise ValueError("Укажите размер матрицы m и n для расшифрования")
            # При шифровании m,n могут быть None (будут вычислены автоматически)
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