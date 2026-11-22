"""All data shapes. API-CONTRACT.md is the human-readable version of these."""
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Stage = Literal["idea", "prototype", "mvp", "launched", "revenue"]
Status = Literal["pending", "analyzing", "done", "failed"]
Priority = Literal["high", "medium", "low"]
Confidence = Literal["low", "medium", "high"]
DecisionValue = Literal["shortlist", "interview", "hold", "decline"]

# Fields that identify the applicant. They are NEVER sent to the AI.
IDENTITY_FIELDS = ("founder_name", "founder_email", "organization")
# Fields the AI may see (the startup itself).
CONTENT_FIELDS = (
    "startup_name", "one_liner", "sector", "stage", "problem", "solution",
    "target_customers", "traction", "business_model", "team_background", "ask",
)


class ApplicationIn(BaseModel):
    startup_name: str = Field(min_length=2, max_length=120)
    one_liner: str = Field(min_length=5, max_length=300)
    sector: str = Field(default="", max_length=80)
    stage: Stage = "idea"
    problem: str = Field(min_length=10, max_length=4000)
    solution: str = Field(min_length=10, max_length=4000)
    target_customers: str = Field(default="", max_length=3000)
    traction: str = Field(default="", max_length=3000)
    business_model: str = Field(default="", max_length=3000)
    team_background: str = Field(default="", max_length=3000)
    ask: str = Field(default="", max_length=2000)
    # identity (blind-review hides these; the AI never sees them)
    founder_name: str = Field(min_length=2, max_length=120)
    founder_email: str = Field(max_length=200)
    organization: str = Field(default="", max_length=160)

    @field_validator("founder_email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("enter a valid email")
        return v


# ---------- what Gemini returns (no defaults / constraints: keeps the schema Gemini-friendly) ----------
class AICriterion(BaseModel):
    key: str
    score: int
    reasoning: str
    evidence_quote: str


class AIEvaluation(BaseModel):
    summary: str
    criteria: list[AICriterion]
    strengths: list[str]
    risks: list[str]
    riskiest_assumptions: list[str]
    interview_questions: list[str]
    red_flags: list[str]
    missing_info: list[str]
    confidence: Literal["low", "medium", "high"]


# ---------- what we store and serve ----------
class CriterionResult(BaseModel):
    key: str
    name: str
    weight: float
    score: int  # 1..5
    reasoning: str
    evidence_quote: str
    evidence_verified: Optional[bool] = None  # None = no quote given


class Evaluation(BaseModel):
    summary: str
    criteria: list[CriterionResult]
    strengths: list[str]
    risks: list[str]
    riskiest_assumptions: list[str]
    interview_questions: list[str]
    red_flags: list[str]
    missing_info: list[str]
    confidence: Confidence
    overall_score: float  # 0..100, computed by code (never by the model)
    priority: Priority  # review priority, NOT an admission decision
    completeness: float  # 0..100, share of optional fields filled
    unverified_quotes: int = 0
    injection_detected: bool = False
    attempts: int = 1
    warnings: list[str] = []
    rubric_version: int = 1
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None


class DecisionRecord(BaseModel):
    decision: DecisionValue
    note: str = Field(default="", max_length=2000)
    reviewer: str = Field(default="", max_length=120)
    decided_at: str = ""


class DecisionIn(BaseModel):
    decision: DecisionValue
    note: str = Field(default="", max_length=2000)
    reviewer: str = Field(default="", max_length=120)


class Application(BaseModel):
    id: str
    created_at: str
    status: Status = "pending"
    error: Optional[str] = None
    input: ApplicationIn
    has_deck: bool = False
    deck_filename: Optional[str] = None
    evaluation: Optional[Evaluation] = None
    decision: Optional[DecisionRecord] = None
    ai_mode: Optional[str] = None  # "gemini" | "mock"
    model: Optional[str] = None
    analysis_seconds: Optional[float] = None
