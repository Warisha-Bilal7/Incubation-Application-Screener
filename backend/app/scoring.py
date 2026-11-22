"""Deterministic scoring. The model scores each criterion 1-5; code does all the arithmetic."""
from .grounding import verify_quote
from .models import ApplicationIn, AIEvaluation, CriterionResult
from .rubric import Rubric

HIGH_THRESHOLD = 70.0  # overall >= 70  -> high review priority   (avg criterion score >= 3.8)
MEDIUM_THRESHOLD = 45.0  # overall >= 45  -> medium                  (avg criterion score >= 2.8)

OPTIONAL_FIELDS = ("target_customers", "traction", "business_model", "team_background", "ask")


def clamp_score(value) -> int:
    try:
        return max(1, min(5, int(round(float(value)))))
    except (TypeError, ValueError):
        return 1


def build_criterion_results(
    ai: AIEvaluation, rubric: Rubric, corpus_norm: str
) -> tuple[list[CriterionResult], list[str]]:
    by_key = {c.key: c for c in ai.criteria}
    results, warnings = [], []
    for crit in rubric.criteria:
        got = by_key.get(crit.key)
        if got is None:
            warnings.append(f"Model did not score '{crit.key}'; defaulted to 1.")
            results.append(CriterionResult(
                key=crit.key, name=crit.name, weight=crit.weight, score=1,
                reasoning="Not scored by the model.", evidence_quote="", evidence_verified=None,
            ))
            continue
        results.append(CriterionResult(
            key=crit.key, name=crit.name, weight=crit.weight,
            score=clamp_score(got.score), reasoning=got.reasoning.strip(),
            evidence_quote=got.evidence_quote.strip(),
            evidence_verified=verify_quote(got.evidence_quote, corpus_norm),
        ))
    return results, warnings


def overall_score(results: list[CriterionResult]) -> float:
    """Weighted average of 1-5 scores mapped to 0-100 (1 -> 0, 5 -> 100)."""
    total_w = sum(r.weight for r in results)
    if total_w <= 0:
        return 0.0
    avg = sum(r.weight * r.score for r in results) / total_w
    return round((avg - 1) / 4 * 100, 1)


def priority_for(score: float) -> str:
    if score >= HIGH_THRESHOLD:
        return "high"
    if score >= MEDIUM_THRESHOLD:
        return "medium"
    return "low"


def completeness(inp: ApplicationIn) -> float:
    filled = sum(1 for f in OPTIONAL_FIELDS if len(getattr(inp, f).strip()) >= 15)
    return round(filled / len(OPTIONAL_FIELDS) * 100, 1)
