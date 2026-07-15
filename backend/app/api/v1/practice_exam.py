from __future__ import annotations

import json
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import Path as RoutePath
from pydantic import BaseModel, ConfigDict

from backend.app.config import PROJECT_ROOT

router = APIRouter(prefix="/practice", tags=["practice"])


class PracticeQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    topic: str
    content: str
    choices: list[str]
    correct_index: int
    explanation: str


class PracticeBank(BaseModel):
    bank_code: str
    title: str
    language: str
    version: int
    questions: list[PracticeQuestion]


@lru_cache(maxsize=4)
def _load_bank(bank_code: str) -> PracticeBank:
    if bank_code != "pdpa-50":
        raise FileNotFoundError
    source = PROJECT_ROOT / "data" / "question_banks" / "pdpa_50.json"
    return PracticeBank.model_validate(json.loads(source.read_text(encoding="utf-8")))


@router.get("/banks/{bank_code}", response_model=PracticeBank)
def get_practice_bank(
    bank_code: Annotated[str, RoutePath(pattern=r"^[a-z0-9-]+$", max_length=50)],
) -> PracticeBank:
    try:
        return _load_bank(bank_code)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=404, detail="Practice question bank not found") from error
