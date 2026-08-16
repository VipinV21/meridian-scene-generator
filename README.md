# The Meridian Company — Epistemic Scene Generator & Verification System

An epistemic scene generation and automated auditing system for *The Meridian Company* serialized drama. Built with **FastAPI (Python)** and **React + TypeScript (Vite)**.

The system enforces strict **epistemic boundaries**, guaranteeing that characters only know what they have personally witnessed, been told, or inferred up to a specific point in the story, preventing omniscience and fact-leakage.

---

## Quickstart Guide (< 2 minutes)

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Start the FastAPI Backend
```bash
# From the project root
pip install -r backend/requirements.txt

# Start backend server (runs on port 8000)
python -m uvicorn backend.app.main:app --reload --port 8000
```

> Note: The frontend automatically detects and connects whether your backend runs on port 8001 or port 8000.

### 2. Start the React + TypeScript Frontend
```bash
# In a new terminal window, navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server (runs on http://localhost:5173)
npm run dev
```

Open `http://localhost:5173` in your browser to view the interactive dashboard.

---

## Project Structure & Deliverables

```
TYN/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI routes & endpoints
│   │   ├── story_data.py         # Epistemic ledger & story event database
│   │   ├── epistemic_engine.py   # Boundary calculator (allowed vs forbidden facts)
│   │   ├── verifier.py           # 2-stage verification & leak audit engine
│   │   ├── generator.py          # Bounded scene generator (~300 words)
│   │   └── models.py             # Pydantic request/response schemas
│   └── requirements.txt
├── frontend/                     # React + TypeScript + Vite UI
│   ├── src/
│   │   ├── App.tsx               # Interactive Dashboard & Audit Inspector
│   │   └── index.css             # Glassmorphism styling system
│   └── package.json
├── samples/                      # Required outputs for all 6 assessment test cases
│   ├── case1_kamala_ep5.md (.json)
│   ├── case2_kamala_ep4.md (.json)
│   ├── case3_tomas_ep5.md (.json)
│   ├── case4_priya_ep5.md (.json)
│   ├── case5_wren_ep6.md (.json)
│   └── case6_wren_ep5.md (.json)
├── DECISIONS.md                  # Design rationale (600–900 words plain prose)
└── README.md                     # Setup instructions & API documentation
```

---

## API Request & Response Shapes

### 1. `POST /api/generate-scene`

Generates a character POV scene at a specific story point and audits it against epistemic bounds.

**Request Body (`JSON`):**
```json
{
  "character": "Kamala",
  "point_in_story": "end of Ep 5",
  "scene_prompt": "Kamala confronts Dev in the empty auditorium about whether he still wants to be here."
}
```

**Response Body (`JSON`):**
```json
{
  "character": "Kamala",
  "point_in_story": "end of Ep 5",
  "scene_prompt": "Kamala confronts Dev in the empty auditorium about whether he still wants to be here.",
  "scene_text": "The seats in the auditorium were dark...",
  "word_count": 312,
  "epistemic_audit": {
    "is_epistemically_valid": true,
    "verification_score": 100,
    "detected_leaks": [],
    "allowed_knowledge_used": [
      "Ep 1: Dev took a 4-minute phone call during read-through...",
      "Ep 3: Dev missed an entire day of rehearsal without explanation..."
    ],
    "forbidden_knowledge_avoided": [
      "FORBIDDEN: Dev accepted a serial in Hyderabad starting March.",
      "FORBIDDEN: Tomas signed a conditional sale agreement for the building."
    ],
    "justification": "VERIFICATION PASSED (Score: 100/100): Scene strictly adheres to Kamala's epistemic state..."
  },
  "allowed_knowledge": [...],
  "suspicions_and_misconceptions": [...],
  "forbidden_knowledge": [...],
  "generation_mode": "openai_gpt4o"
}
```

`generation_mode` tells you exactly how `scene_text` was produced — `openai_gpt4o` / `gemini_1.5_pro` for a live model call, or a `*_using_curated_fallback` / `*_no_fallback_available` variant if no key was configured or the live call failed. See "Environment Variables & Model Configuration" below.

### 2. `GET /api/samples`
Returns pre-audited outputs for all 6 assessment test cases.

### 3. `GET /api/story/epistemic-matrix`
Returns the full observer knowledge grid mapping characters across episodes 1 to 6.

---

## Assessment Test Cases Overview

1. **Case 1: Kamala (end of Ep 5)** — *Confronts Dev about unreliability.* (Does NOT know Dev's Hyderabad deal or Chennai audition).
2. **Case 2: Kamala (end of Ep 4)** — *Reflects on car park observation.* (Misinterprets Tomas & Priya talking as management betrayal; does NOT know building is being sold).
3. **Case 3: Tomas (end of Ep 5)** — *Walks empty auditorium after signing sale agreement.* (Does NOT know about grant forgery, Dev leaving, or lighting desk failure).
4. **Case 4: Priya (end of Ep 5)** — *Files dress rehearsal log notes.* (Holds extensive secret knowledge; does NOT know Dev's specific deal or Kamala's private thoughts).
5. **Case 5: Wren (end of Ep 6)** — *Walks home after gala.* (Thinks about leading next season; completely oblivious to building sale).
6. **Case 6: Wren (end of Ep 5)** — *Speculates on Kamala's distraction.* (Guesses based on visible behavior; does NOT know about grant forgery, lease, or building sale).

---

## Environment Variables & Model Configuration

- `OPENAI_API_KEY` (Optional): if set, scenes are generated live via OpenAI GPT-4o. The model receives a system prompt built entirely from that character's `allowed_knowledge` / `suspicions_and_misconceptions` (see `backend/app/generator.py::_build_system_prompt`) — the raw story text is never included in that prompt, and neither is `forbidden_knowledge`; that list is used only by the verifier, after generation, never shown to the writing model.
- `GEMINI_API_KEY` (Optional, used if `OPENAI_API_KEY` is not set): same approach, via Google Gemini 1.5 Pro. Requires `pip install google-generativeai` (included in `requirements.txt`).
- `GROQ_API_KEY` (Optional, used if neither of the above is set): same approach, via Groq's Llama 3.3 70B. Groq exposes an OpenAI-compatible API, so this reuses the `openai` SDK with a different `base_url` (see `backend/app/llm_client.py`).
- **No key set:** the backend does not fabricate a "generated" scene. For the 6 assessment cases specifically, it returns a curated, pre-written fallback scene (in `PRESET_SCENES`) so the project still runs and is reviewable end-to-end on a clean machine with zero API keys. For any other character/point combination with no key configured, it returns an explicit placeholder saying so, rather than pretending to generate something.
- Every response includes a `generation_mode` field (`openai_gpt4o`, `gemini_1.5_pro`, `groq_llama3.3_70b`, `*_using_curated_fallback`, or `*_no_fallback_available`) so it's always clear which path produced a given scene — this is also surfaced in the frontend and in each `samples/*.md` file.
- Whichever key is configured also enables a semantic (LLM-based) verifier layer on top of the two lexical layers in `backend/app/verifier.py`, which catches leaks implied rather than stated outright. `EpistemicAudit.semantic_check_mode` reports `skipped_no_key` when it didn't run, so a passing score never silently implies a check that didn't happen.

> The samples in `samples/` were generated with no API key configured, so they show `generation_mode: no_key_configured_using_curated_fallback`. Set one of the keys above and re-run `python backend/generate_samples.py` to regenerate them via live LLM calls.
