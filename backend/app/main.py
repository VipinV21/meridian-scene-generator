"""
FastAPI Server for The Meridian Company Epistemic Scene Generator.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from .models import SceneRequest, SceneResponse, CaseSample, EpistemicAudit
from .generator import generate_scene_for_character
from .epistemic_engine import get_epistemic_context, parse_episode_number
from .story_data import EPISODES

app = FastAPI(
    title="Meridian Company Epistemic Scene Generator",
    description="FastAPI backend enforcing epistemic boundaries on character point-of-view scene generation.",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Assessment 6 Test Cases Definition
TEST_CASES = [
    {
        "case_number": 1,
        "character": "Kamala",
        "point_in_story": "end of Ep 5",
        "scene_prompt": "Kamala confronts Dev in the empty auditorium about whether he still wants to be here.",
        "test_case_analysis": (
            "TRAP / BOUNDARY TEST: Kamala knows Dev missed an entire day in Ep 3 without explanation, took a suspicious call in Ep 1, "
            "and was 1 hour late to dress rehearsal in Ep 5. However, she DOES NOT KNOW Dev accepted a serial in Hyderabad (Ep 2), "
            "auditioned in Chennai (Ep 3), or plans to announce his departure from the gala stage (Ep 4). She confronts him about his "
            "perceived unreliability and detachment, but MUST NOT accuse him of leaving the company or specific un-communicated job offers."
        )
    },
    {
        "case_number": 2,
        "character": "Kamala",
        "point_in_story": "end of Ep 4",
        "scene_prompt": "Kamala goes over what she saw in the car park.",
        "test_case_analysis": (
            "MISCONCEPTION & PERCEPTION TEST: Kamala saw Tomas and Priya standing close together in the car park from 3 floors up on the "
            "fire escape (Ep 4), but heard NOTHING. She misinterprets this as Tomas undermining her by going around her to her staff. "
            "She DOES NOT KNOW Tomas told Priya he is selling the building. The scene must show her stewing over perceived management betrayal "
            "rather than the actual building sale."
        )
    },
    {
        "case_number": 3,
        "character": "Tomas",
        "point_in_story": "end of Ep 5",
        "scene_prompt": "Tomas walks through the empty auditorium the morning after signing the sale agreement.",
        "test_case_analysis": (
            "ISOLATED KNOWLEDGE TEST: Tomas signed the conditional sale agreement on Friday morning (Ep 5). He knows the lease non-renewal "
            "and his secret meetings with developers. However, he DOES NOT KNOW about Kamala's 2019 grant forgery, Dev's secret auditions, "
            "the lighting desk breakdown, or Wren replacing Dev in dress rehearsal. His perspective is cool, detached, and administrative."
        )
    },
    {
        "case_number": 4,
        "character": "Priya",
        "point_in_story": "end of Ep 5",
        "scene_prompt": "Priya writes up her notes after the dress rehearsal.",
        "test_case_analysis": (
            "HIGH-CONTEXT OBSERVER TEST: Priya holds extensive secret knowledge (knows building sale from Tomas, knows grant forgery from archive, "
            "paid for replacement lighting desk out of pocket, secretly set up Wren's understudy track). However, she ONLY suspects Dev is auditioning "
            "(doesn't know Hyderabad deal specifics) and DOES NOT know Kamala's private thought that Wren is better than Dev. Her notes reflect quiet, meticulous record-keeping."
        )
    },
    {
        "case_number": 5,
        "character": "Wren",
        "point_in_story": "end of Ep 6",
        "scene_prompt": "Wren walks home after closing night, thinking about next season.",
        "test_case_analysis": (
            "EPISTEMIC TRAP / DRAMATIC IRONY TEST: Wren performed brilliantly in dress rehearsal (Ep 5), heard Dev announce his departure from stage (Ep 6), "
            "and accepted Kamala's offer of lead roles for next season in the office (Ep 6). However, neither Kamala nor Wren mentions the building sale "
            "because NEITHER KNOWS IT IS SOLD! Wren's scene must be hopeful and focused on next season, unaware that the theatre building won't exist in 11 months."
        )
    },
    {
        "case_number": 6,
        "character": "Wren",
        "point_in_story": "end of Ep 5",
        "scene_prompt": "Wren tries to work out why Kamala has been so distracted lately.",
        "test_case_analysis": (
            "SPECULATIVE BOUNDARY TEST: At Ep 5, Wren has noticed Kamala's erratic behavior (abruptly cutting her scene, locking the grant file in her desk, "
            "uncharacteristically not pressing Dev for missing rehearsal). Wren must speculate based ONLY on visible clues. She DOES NOT KNOW about the lease, "
            "grant forgery, building sale, or Dev's Hyderabad deal."
        )
    }
]


@app.get("/api/health")
def health_check():
    return {"status": "ok", "system": "Meridian Epistemic Engine", "version": "1.0.0"}


@app.post("/api/generate-scene", response_model=SceneResponse)
def generate_scene(req: SceneRequest):
    try:
        res = generate_scene_for_character(
            character=req.character,
            point_in_story=req.point_in_story,
            scene_prompt=req.scene_prompt
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/samples", response_model=List[CaseSample])
def get_sample_cases():
    samples = []
    for tc in TEST_CASES:
        res = generate_scene_for_character(
            character=tc["character"],
            point_in_story=tc["point_in_story"],
            scene_prompt=tc["scene_prompt"]
        )
        samples.append(CaseSample(
            case_number=tc["case_number"],
            character=res.character,
            point_in_story=res.point_in_story,
            scene_prompt=res.scene_prompt,
            scene_text=res.scene_text,
            word_count=res.word_count,
            epistemic_audit=res.epistemic_audit,
            allowed_knowledge=res.allowed_knowledge,
            suspicions_and_misconceptions=res.suspicions_and_misconceptions,
            forbidden_knowledge=res.forbidden_knowledge,
            test_case_analysis=tc["test_case_analysis"],
            generation_mode=res.generation_mode
        ))
    return samples


@app.get("/api/story/epistemic-matrix")
def get_epistemic_matrix():
    characters = ["Kamala", "Tomas", "Priya", "Wren", "Dev"]
    episodes = [1, 2, 3, 4, 5, 6]
    matrix = {}
    for c in characters:
        matrix[c] = {}
        for ep in episodes:
            matrix[c][ep] = get_epistemic_context(c, f"end of Ep {ep}")
    return {"matrix": matrix, "episodes": EPISODES}
