"""The analysis pipeline.

    extract -> evaluate (LLM) -> verify quotes (code) --unverified?--> retry once with feedback
            -> rule checks (injection) -> score (code) -> Evaluation

The LLM scores criteria and writes text. Code verifies, does the arithmetic and sets the priority.
"""
from .ai import Analyzer
from .grounding import detect_injection, extract_pdf_text, form_text, norm
from .models import CONTENT_FIELDS, ApplicationIn, Evaluation
from .rubric import Rubric
from .scoring import build_criterion_results, completeness, overall_score, priority_for

MAX_RETRIES = 1
UNVERIFIED_SHARE_FOR_LOW_CONFIDENCE = 0.3


def _feedback(unverified) -> str:
    bad = "; ".join(f"[{r.key}] \"{r.evidence_quote}\"" for r in unverified)
    return (
        "These evidence quotes were NOT found verbatim in the application: "
        f"{bad}. Re-evaluate. Each evidence_quote must be copied exactly from the application text "
        "(max 25 words), or left empty if nothing supports the score."
    )


def run_analysis(
    inp: ApplicationIn, rubric: Rubric, analyzer: Analyzer, pdf_bytes: bytes | None = None
) -> Evaluation:
    pdf_text = extract_pdf_text(pdf_bytes) if pdf_bytes else ""
    corpus_norm = norm(form_text(inp) + "\n" + pdf_text)

    attempts, feedback = 0, None
    best = None  # (results, warnings, ai, usage)
    while True:
        attempts += 1
        ai = analyzer.analyze(inp, rubric, pdf_bytes, feedback)
        usage = getattr(analyzer, "last_usage", (None, None))
        results, warnings = build_criterion_results(ai, rubric, corpus_norm)
        unverified = [r for r in results if r.evidence_verified is False]
        if best is None or len(unverified) <= sum(1 for r in best[0] if r.evidence_verified is False):
            best = (results, warnings, ai, usage)
        if not unverified or attempts > MAX_RETRIES:
            break
        feedback = _feedback(unverified)

    results, warnings, ai, usage = best
    n_unverified = sum(1 for r in results if r.evidence_verified is False)

    # rule-based checks the model cannot be trusted with
    fields = {f: str(getattr(inp, f)) for f in CONTENT_FIELDS}
    fields["deck"] = pdf_text
    injected = detect_injection(fields)
    red_flags = list(ai.red_flags)
    if injected:
        red_flags.insert(0, "Instruction-like text found in: " + ", ".join(injected) + ". It was ignored; review manually.")

    confidence = ai.confidence
    if injected or (results and n_unverified / len(results) > UNVERIFIED_SHARE_FOR_LOW_CONFIDENCE):
        confidence = "low"
    if n_unverified:
        warnings.append(f"{n_unverified} evidence quote(s) could not be matched to the application text.")

    score = overall_score(results)
    return Evaluation(
        summary=ai.summary.strip(),
        criteria=results,
        strengths=ai.strengths,
        risks=ai.risks,
        riskiest_assumptions=ai.riskiest_assumptions,
        interview_questions=ai.interview_questions,
        red_flags=red_flags,
        missing_info=ai.missing_info,
        confidence=confidence,
        overall_score=score,
        priority=priority_for(score),
        completeness=completeness(inp),
        unverified_quotes=n_unverified,
        injection_detected=bool(injected),
        attempts=attempts,
        warnings=warnings,
        rubric_version=rubric.version,
        tokens_in=usage[0],
        tokens_out=usage[1],
    )
