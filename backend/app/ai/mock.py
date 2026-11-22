"""Offline stand-in for Gemini so the frontend and tests work with no API key.

It is a simple heuristic (length + specifics), NOT real analysis. Every response is labelled
ai_mode="mock" and the UI must show a MOCK badge. Do not demo this as the product.
"""
import re

from ..models import AIEvaluation, AICriterion, ApplicationIn
from ..rubric import Rubric

_SPECIFIC = re.compile(r"\d|%|pkr|rs\.?|₨|\busd\b", re.IGNORECASE)


def _first_sentence(text: str, limit: int = 140) -> str:
    text = " ".join((text or "").split())
    if not text:
        return ""
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    s = m.group(1) if m else text
    return s[:limit].rstrip()


class MockAnalyzer:
    name = "mock"
    model = "mock-heuristic"

    def __init__(self):
        self.last_usage = (None, None)

    def analyze(self, inp: ApplicationIn, rubric: Rubric, pdf_bytes=None, feedback=None) -> AIEvaluation:
        criteria, low, high = [], [], []
        for c in rubric.criteria:
            texts = [getattr(inp, f, "") for f in (c.hint_fields or [c.key])]
            text = " ".join(t for t in texts if t).strip()
            n = len(text)
            score = 1 if n == 0 else 2 if n < 80 else 3 if n < 200 else 4
            if n and _SPECIFIC.search(text):
                score += 1
            score = max(1, min(5, score))
            quote = _first_sentence(next((t for t in texts if t), ""))
            criteria.append(AICriterion(
                key=c.key, score=score,
                reasoning=("No information provided." if n == 0 else
                           f"Heuristic score from detail and specifics ({n} characters)."),
                evidence_quote=quote,
            ))
            (low if score <= 2 else high if score >= 4 else []).append(c.name)

        missing = [f for f in ("traction", "business_model", "team_background") if not getattr(inp, f).strip()]
        return AIEvaluation(
            summary=f"[MOCK] {inp.startup_name}: {inp.one_liner}"[:300],
            criteria=criteria,
            strengths=[f"Detailed on: {n}" for n in high[:3]] or ["(mock) none detected"],
            risks=[f"Thin on: {n}" for n in low[:3]] or ["(mock) none detected"],
            riskiest_assumptions=[
                f"Target customers will pay for: {inp.solution[:80]}" if inp.solution else "Customers will pay",
                "The team can ship the solution within the stated timeline",
            ],
            interview_questions=[
                f"What is the strongest evidence that '{inp.problem[:60]}' is painful enough to pay to fix?",
                "Who are your first five customers, and how will you reach them?",
                "What would make you stop working on this in six months?",
            ],
            red_flags=[],
            missing_info=[m.replace("_", " ") for m in missing],
            confidence="low" if len(missing) >= 2 else "medium",
        )
