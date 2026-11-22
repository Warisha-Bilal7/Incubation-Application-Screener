import json
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "rubric.default.json"


class Criterion(BaseModel):
    key: str = Field(min_length=2, max_length=40, pattern=r"^[a-z][a-z0-9_]*$")
    name: str
    weight: float = Field(gt=0, le=100)
    description: str
    anchors: dict[str, str] = {}
    hint_fields: list[str] = []  # used only by the mock analyzer


class Rubric(BaseModel):
    version: int = 1
    name: str = "Default incubator rubric"
    criteria: list[Criterion]

    @field_validator("criteria")
    @classmethod
    def _valid(cls, v: list[Criterion]) -> list[Criterion]:
        if len(v) < 2:
            raise ValueError("a rubric needs at least 2 criteria")
        if len({c.key for c in v}) != len(v):
            raise ValueError("criterion keys must be unique")
        return v


def load_default_rubric() -> Rubric:
    return Rubric.model_validate(json.loads(DEFAULT_PATH.read_text(encoding="utf-8")))
