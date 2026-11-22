"""Checks that run in plain code, not in the model:
- quote verification (is the evidence quote really in the application?)
- prompt-injection detection
- PDF text extraction (used only to verify quotes; Gemini reads the PDF itself)
"""
import io
import re

from .models import CONTENT_FIELDS, ApplicationIn

_NON_ALNUM = re.compile(r"[^\w]+", re.UNICODE)


def norm(text: str) -> str:
    return _NON_ALNUM.sub(" ", (text or "").lower()).strip()


def form_text(inp: ApplicationIn) -> str:
    """The startup content the AI is allowed to see (no identity fields)."""
    return "\n".join(f"{f}: {getattr(inp, f)}" for f in CONTENT_FIELDS if getattr(inp, f))


def verify_quote(quote: str, corpus_norm: str) -> bool | None:
    """True/False if the quote is (not) in the corpus. None when no quote was given.
    Quotes with '...' are split and every fragment must appear."""
    if not quote or not quote.strip():
        return None
    fragments = [f for f in re.split(r"\.\.\.|…", quote) if norm(f)]
    fragments = [norm(f) for f in fragments]
    fragments = [f for f in fragments if len(f) >= 6]
    if not fragments:
        return False
    return all(f in corpus_norm for f in fragments)


INJECTION_PATTERNS = [
    r"ignore (all |any |the )?(previous|prior|above|earlier) (instructions|prompts?|rules)",
    r"disregard (all |any |the )?(previous|prior|above|earlier)",
    r"(give|assign|award|score) (this|us|me|it)[^.\n]{0,40}\b(5|five|full|maximum|top|highest|perfect)\b",
    r"(system|developer) (prompt|message|instruction)",
    r"you are (now )?(an?|the) (ai|assistant|model|reviewer|evaluator)",
    r"\bscore (this|it) (a )?(5|five|10|100)\b",
    r"override (the )?(rubric|scoring|instructions)",
]
_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def detect_injection(fields: dict[str, str]) -> list[str]:
    """Return the names of fields that contain instruction-like text."""
    hits = []
    for name, value in fields.items():
        if value and any(r.search(value) for r in _INJECTION_RE):
            hits.append(name)
    return hits


def extract_pdf_text(pdf_bytes: bytes, max_pages: int = 30) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages[:max_pages]:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)
    except Exception:
        return ""
