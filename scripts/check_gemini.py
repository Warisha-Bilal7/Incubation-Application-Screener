#!/usr/bin/env python3
"""Run this FIRST when you get your Gemini API key (takes about 10 seconds).

    cd backend && python ../scripts/check_gemini.py

It (1) lists the Gemini models your key can call, (2) makes one tiny structured-output call with the
model in GEMINI_MODEL, and (3) tells you exactly what to put in backend/.env if something is wrong.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import get_settings  # noqa: E402


def main() -> int:
    s = get_settings()
    if not s.gemini_api_key:
        print("FAIL  GEMINI_API_KEY is empty. Create a key at https://aistudio.google.com/apikey and put it in backend/.env")
        return 1

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=s.gemini_api_key)

    print("Models available to this key (generateContent):")
    names = []
    try:
        for m in client.models.list():
            if "generateContent" in (getattr(m, "supported_actions", None) or []):
                n = m.name.replace("models/", "")
                if "gemini" in n:
                    names.append(n)
        for n in sorted(names):
            print("  ", n)
    except Exception as e:
        print("WARN  could not list models:", e)

    print(f"\nTesting GEMINI_MODEL={s.gemini_model!r} with a structured-output call...")
    try:
        resp = client.models.generate_content(
            model=s.gemini_model,
            contents='Return JSON {"ok": true, "word": "<any one word>"}',
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0),
        )
        data = json.loads(resp.text)
        print("PASS ", data)
    except Exception as e:
        print("FAIL ", type(e).__name__, str(e)[:300])
        if names:
            flash = [n for n in names if "flash" in n and "lite" not in n]
            print("\nTry one of these in backend/.env, e.g.  GEMINI_MODEL=" + (flash[0] if flash else names[0]))
        return 1

    print("\nNow test the full pipeline with a PDF:  python ../scripts/run_eval.py --limit 3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
