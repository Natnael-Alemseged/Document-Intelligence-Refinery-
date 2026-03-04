"""Pydantic models for extraction_rules.yaml."""

from typing import List

from pydantic import BaseModel, Field


class FastTextRules(BaseModel):
    min_chars_per_page: int = 100
    max_image_ratio: float = 0.50
    min_char_density: float = 0.02
    min_confidence: float = 0.5


class VisionRules(BaseModel):
    budget_per_document_usd: float = 1.0
    model_cheap: str = "google/gemini-2.0-flash-lite-001"
    model_quality: str = "anthropic/claude-3-5-sonnet"
    max_retries: int = 2


class ExtractionRules(BaseModel):
    fast_text: FastTextRules = Field(default_factory=FastTextRules)
    confidence_escalation_threshold: float = 0.5
    vision: VisionRules = Field(default_factory=VisionRules)
