from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SceneRequest(BaseModel):
    character: str = Field(..., description="Target character name (Kamala, Tomas, Priya, Wren, Dev)")
    point_in_story: str = Field(..., description="Episode point, e.g., 'end of Ep 5', 'end of Ep 4'")
    scene_prompt: str = Field(..., description="Prompt describing the scene to generate")

class EpistemicAudit(BaseModel):
    is_epistemically_valid: bool
    verification_score: int = Field(..., description="Score 0 to 100")
    detected_leaks: List[str] = Field(default_factory=list)
    allowed_knowledge_used: List[str] = Field(default_factory=list)
    forbidden_knowledge_avoided: List[str] = Field(default_factory=list)
    justification: str
    semantic_check_mode: str = Field(
        default="skipped_no_key",
        description="Whether the LLM-based semantic leak check ran: the provider used "
                     "(e.g. 'openai_gpt4o'), or 'skipped_no_key' when no API key was "
                     "configured, in which case only the two lexical layers ran."
    )

class SceneResponse(BaseModel):
    character: str
    point_in_story: str
    scene_prompt: str
    scene_text: str
    word_count: int
    epistemic_audit: EpistemicAudit
    allowed_knowledge: List[str]
    suspicions_and_misconceptions: List[str]
    forbidden_knowledge: List[str]
    generation_mode: str = Field(
        default="unknown",
        description="How this scene was produced: openai_gpt4o, gemini_1.5_pro, "
                     "or a *_using_curated_fallback / *_no_fallback_available variant "
                     "when no API key was configured or the live call failed."
    )

class CaseSample(BaseModel):
    case_number: int
    character: str
    point_in_story: str
    scene_prompt: str
    scene_text: str
    word_count: int
    epistemic_audit: EpistemicAudit
    allowed_knowledge: List[str]
    suspicions_and_misconceptions: List[str]
    forbidden_knowledge: List[str]
    test_case_analysis: str
    generation_mode: str = "unknown"
