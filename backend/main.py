"""FastAPI: обучающая система «Шифры для школьников» — только API по ТЗ."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ciphers.combined_steps import get_decryption_steps, get_encryption_steps
from models.schemas import ProcessRequest, ProcessResponse

app = FastAPI(title="Шифры для школьников", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/process", response_model=ProcessResponse)
def process(body: ProcessRequest) -> ProcessResponse:
    try:
        read_method = getattr(body, 'read_method', 'row')
        period = getattr(body, 'period', None)
        
        if body.operation == "encrypt":
            steps, final_text = get_encryption_steps(
                body.text,
                body.mode,
                sub_key=body.sub_key,
                period=period,
                m=body.m,
                n=body.n,
                read_method=read_method,
            )
        else:
            steps, final_text = get_decryption_steps(
                body.text,
                body.mode,
                sub_key=body.sub_key,
                period=period,
                m=body.m,
                n=body.n,
                read_method=read_method,
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ProcessResponse(steps=steps, final_text=final_text)