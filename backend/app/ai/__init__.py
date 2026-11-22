from typing import Protocol

from ..models import AIEvaluation, ApplicationIn
from ..rubric import Rubric


class AnalysisError(RuntimeError):
    pass


class Analyzer(Protocol):
    name: str  # "gemini" | "mock"
    model: str

    def analyze(
        self, inp: ApplicationIn, rubric: Rubric, pdf_bytes: bytes | None, feedback: str | None = None
    ) -> AIEvaluation: ...

    last_usage: tuple[int | None, int | None]
