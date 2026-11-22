"""Gemini analyzer: PDF understanding + structured JSON output via the google-genai SDK."""
import json
import time

from ..models import AIEvaluation, ApplicationIn
from ..prompts import SYSTEM, build_user_prompt
from ..rubric import Rubric
from . import AnalysisError


class GeminiAnalyzer:
    name = "gemini"

    def __init__(self, api_key: str, model: str, client=None, retries: int = 2, sleep=time.sleep):
        self.model = model
        self.retries = retries
        self._sleep = sleep
        self.last_usage: tuple[int | None, int | None] = (None, None)
        if client is not None:
            self._client = client
        else:
            from google import genai

            self._client = genai.Client(api_key=api_key)

    def _build_contents(self, prompt: str, pdf_bytes: bytes | None):
        from google.genai import types

        parts = []
        if pdf_bytes:
            parts.append(types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"))
        parts.append(types.Part.from_text(text=prompt))
        return [types.Content(role="user", parts=parts)]

    def _config(self):
        from google.genai import types

        return types.GenerateContentConfig(
            system_instruction=SYSTEM,
            response_mime_type="application/json",
            response_schema=AIEvaluation,
            temperature=0.2,
        )

    def analyze(
        self, inp: ApplicationIn, rubric: Rubric, pdf_bytes: bytes | None, feedback: str | None = None
    ) -> AIEvaluation:
        prompt = build_user_prompt(inp, rubric, has_deck=bool(pdf_bytes), feedback=feedback)
        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                resp = self._client.models.generate_content(
                    model=self.model,
                    contents=self._build_contents(prompt, pdf_bytes),
                    config=self._config(),
                )
                usage = getattr(resp, "usage_metadata", None)
                self.last_usage = (
                    getattr(usage, "prompt_token_count", None),
                    getattr(usage, "candidates_token_count", None),
                )
                parsed = getattr(resp, "parsed", None)
                if isinstance(parsed, AIEvaluation):
                    return parsed
                text = getattr(resp, "text", None)
                if not text:
                    raise AnalysisError("Gemini returned an empty response (possibly blocked).")
                return AIEvaluation.model_validate(json.loads(text))
            except Exception as e:  # network, quota, bad JSON, schema mismatch
                last_err = e
                if attempt < self.retries:
                    self._sleep(1.5 * (attempt + 1))
        raise AnalysisError(f"Gemini call failed after {self.retries + 1} tries: {last_err}")
