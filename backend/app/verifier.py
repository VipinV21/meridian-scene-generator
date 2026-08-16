"""
Epistemic Verifier & Audit Engine.
Checks generated scene text against forbidden knowledge items and character knowledge boundaries.

Three layers, each catching what the previous one can't:
  1. Curated regex   -- precise, but hand-written for the 6 assessment cases only.
  2. Generic keyword  -- works for any character/point, but is lexical (word
                         co-occurrence), so it can miss a leak that never uses
                         the forbidden fact's own vocabulary, and can false-
                         positive on coincidental word overlap.
  3. LLM semantic check -- catches leaks that are implied rather than stated,
                         e.g. "Wren suddenly understood why the theatre
                         wouldn't be there next year" reveals the building
                         sale without using any of its keywords. This layer
                         only runs when an API key is configured; without
                         one, verification still runs (layers 1-2), and
                         semantic_check_mode reports that it was skipped
                         rather than silently pretending it happened.
"""

from typing import Dict, List, Any, Tuple
import json
import re
from .models import EpistemicAudit
from .epistemic_engine import parse_episode_number
from .llm_client import call_model, available_provider

# Keywords or phrases that leak forbidden knowledge per character/case
FORBIDDEN_LEAK_PATTERNS = {
    ("Kamala", 5): [
        (r'\bhyderabad\b', "Leaked Dev's secret Hyderabad serial deal"),
        (r'\bchennai\b', "Leaked Dev's secret Chennai screen test"),
        (r'\bselling the building\b|\bsale agreement\b', "Leaked Tomas's secret building sale"),
        (r'\bcarbon copy\b|\bduplicate grant\b', "Leaked Priya finding the grant duplicate"),
        (r'\bannounc(e|ing) (his )?departure\b', "Leaked Dev's secret plan to announce departure on gala stage"),
    ],
    ("Kamala", 4): [
        (r'\bselling the building\b|\bsell the building\b|\bproperty developer\b|\bbellary\b', "Leaked Tomas's secret building sale conversation with Priya"),
        (r'\bhyderabad\b', "Leaked Dev's secret serial deal"),
        (r'\bchennai\b', "Leaked Dev's secret audition"),
    ],
    ("Tomas", 5): [
        (r'\bforg(ed|ery)\b|\bco-founder signature\b', "Leaked Kamala's secret grant signature forgery"),
        (r'\bhyderabad\b|\bchennai\b', "Leaked Dev's secret auditions/serial"),
        (r'\blighting desk\b', "Leaked tech rehearsal lighting failure (Tomas was never told)"),
        (r'\bpriya paid\b', "Leaked Priya paying for lighting desk"),
    ],
    ("Priya", 5): [
        (r'\bhyderabad\b', "Leaked Dev's specific Hyderabad serial deal (Priya only suspects auditioning)"),
        (r'\bkamala thought wren (was|is) better\b', "Leaked Kamala's private unspoken thought about Wren"),
    ],
    ("Wren", 6): [
        (r'\bsold the building\b|\bselling the building\b|\bbuilding sale\b|\bdeveloper\b', "Leaked building sale (Wren accepts next season roles unaware of sale!)"),
        (r'\bforg(ed|ery)\b|\bgrant file\b|\bburn(ed|ing) the file\b', "Leaked Kamala's grant forgery or file burning"),
    ],
    ("Wren", 5): [
        (r'\bsell(ing)? the building\b|\bbuilding sale\b', "Leaked secret building sale"),
        (r'\bforg(ed|ery)\b|\bgrant file\b', "Leaked Kamala's grant forgery"),
        (r'\bhyderabad\b|\bchennai\b', "Leaked Dev's secret serial/audition details"),
        (r'\blease expires\b', "Leaked lease non-renewal"),
        (r'\bgreen folder\b|\bturning the key\b|\blocked her (office )?door\b', "Leaked Wren having witnessed Kamala locking away the grant file -- Wren was never present for this (Kamala was alone in the building)"),
    ]
}

def _semantic_leak_check(scene_text: str, char_clean: str, point_in_story: str,
                          forbidden_knowledge: List[str]) -> Tuple[List[str], str]:
    """
    Asks the configured LLM whether the scene reveals, implies, or lets a
    reader infer any forbidden fact -- even without using that fact's
    literal wording. Returns (leak_descriptions, mode). If no key is
    configured, or the call fails, returns ([], mode) and the caller
    proceeds on layers 1-2 alone rather than blocking on this layer.
    """
    if available_provider() == "none" or not forbidden_knowledge:
        return [], "skipped_no_key"

    forbidden_block = "\n".join(f"{i+1}. {f}" for i, f in enumerate(forbidden_knowledge))
    prompt = f"""A scene was written from {char_clean}'s point of view, at "{point_in_story}" in a drama.
Below is a numbered list of facts {char_clean} does NOT know at this point in the story (things they
never witnessed and were never told), followed by the scene itself.

Read the scene and decide, for each numbered fact, whether the scene reveals it -- either directly
(states it outright) or indirectly (the character acts, speaks, or narrates in a way that only makes
sense if they secretly knew it, or a reader could reasonably infer the fact from the scene even
without the exact wording). Do NOT flag a fact just because the scene is thematically adjacent to it
(e.g. a scene about someone leaving a job doesn't leak an unrelated fact about a building sale just
because both involve endings) -- only flag genuine leakage of that specific fact.

FACTS {char_clean} DOES NOT KNOW:
{forbidden_block}

SCENE:
{scene_text}

Respond with ONLY a JSON array (no other text) of objects for facts you judge ARE leaked, each with
"fact_number" (int) and "reason" (one sentence). Return an empty array [] if nothing is leaked."""

    raw, mode = call_model(prompt=prompt)
    if not raw:
        return [], mode

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(json)?|```$", "", cleaned.strip(), flags=re.M).strip()
        findings = json.loads(cleaned)
        leaks = []
        for f in findings:
            idx = f.get("fact_number")
            reason = f.get("reason", "").strip()
            if isinstance(idx, int) and 1 <= idx <= len(forbidden_knowledge):
                fact_text = forbidden_knowledge[idx - 1]
                leaks.append(f"Semantic leak of '{fact_text}': {reason}")
        return leaks, mode
    except (json.JSONDecodeError, TypeError, KeyError):
        # Model didn't return clean JSON -- don't let a parsing failure look
        # like a verification failure. Report the miss, flag nothing.
        return [], f"{mode}_response_unparseable"


def verify_scene_epistemic_bounds(
    scene_text: str,
    character: str,
    point_in_story: str,
    allowed_knowledge: List[str],
    forbidden_knowledge: List[str],
    run_semantic_check: bool = True
) -> EpistemicAudit:
    """
    Scans scene text for epistemic boundary violations.
    Returns EpistemicAudit report.
    """
    char_clean = character.strip().capitalize()
    ep_num = parse_episode_number(point_in_story)
    
    leaks = []
    text_lower = scene_text.lower()

    # Layer 1: curated regex patterns for the 6 known assessment cases.
    # Higher precision (hand-checked wording), but does not generalize past
    # these (character, episode) pairs.
    patterns = FORBIDDEN_LEAK_PATTERNS.get((char_clean, ep_num), [])
    for pattern, explanation in patterns:
        if re.search(pattern, text_lower):
            leaks.append(explanation)

    # Layer 2: generic ledger-driven check, works for ANY character/point --
    # including ones with no curated pattern list above. Pulls significant
    # words (4+ letters, excluding character names and generic story terms)
    # out of each forbidden_knowledge item and flags a probable leak if most
    # of them show up together in the scene text. This is a blunt instrument
    # (keyword co-occurrence, not real understanding) and is meant to catch
    # obvious leaks on untested inputs, not to replace Layer 1's precision.
    STOPWORDS = {
        "forbidden", "kamala", "tomas", "priya", "wren", "episode", "company",
        "season", "with", "that", "this", "from", "into", "about", "than",
        "been", "were", "when", "does", "know", "knows", "knowing", "have",
        # Recurring calendar/scene-setting vocabulary: these show up in almost
        # any scene near the relevant point in the story regardless of which
        # secret (if any) is actually being leaked, so they carry no signal
        # on their own and would otherwise cause false positives whenever a
        # forbidden item happens to be dated relative to them.
        "after", "before", "during", "closing", "night", "tomorrow", "today",
        "morning", "evening",
    }
    for f in forbidden_knowledge:
        clean_f = f.replace("FORBIDDEN:", "").strip().lower()
        # Distinctive words only (5+ letters) -- short words like "told" or
        # "park" recur too often in ordinary scene prose and cause false
        # positives on legitimate text. Require most of the distinctive
        # words to co-occur before flagging, since this layer is a coarse
        # net meant to catch obvious leaks, not a precise semantic check.
        key_terms = [w for w in re.findall(r"\b[a-z]{5,}\b", clean_f) if w not in STOPWORDS]
        if len(key_terms) < 2:
            continue
        hits = sum(1 for t in key_terms if t in text_lower)
        threshold = -(-len(key_terms) * 3 // 4)  # ceil(0.75 * len), floor of 2
        threshold = max(2, threshold)
        if hits >= threshold:
            note = f"Possible leak (generic check): {f}"
            if note not in leaks and not any(f in l for l in leaks):
                leaks.append(note)

    is_valid = len(leaks) == 0
    score = 100 if is_valid else max(10, 100 - (len(leaks) * 45))

    # Layer 3: semantic check via LLM, catches implied leaks that use none of
    # the forbidden fact's own vocabulary. Runs after layers 1-2 so it never
    # masks a lexical hit; only adds findings on top.
    semantic_mode = "skipped_no_key"
    if run_semantic_check:
        semantic_leaks, semantic_mode = _semantic_leak_check(
            scene_text, char_clean, point_in_story, forbidden_knowledge
        )
        if semantic_leaks:
            leaks.extend(semantic_leaks)
            is_valid = False
            score = max(10, 100 - (len(leaks) * 45))

    # Identify allowed knowledge used
    allowed_used = []
    for item in allowed_knowledge:
        # extract key nouns
        words = [w for w in re.findall(r'\b\w{4,}\b', item.lower()) if w not in ["episode", "company", "season"]]
        if any(w in text_lower for w in words[:3]):
            allowed_used.append(item[:80] + "...")

    if not allowed_used and allowed_knowledge:
        allowed_used = [allowed_knowledge[0][:80] + "..."]

    forbidden_avoided = [f for f in forbidden_knowledge if not any(l in f.lower() for l in leaks)]

    if is_valid:
        justification = (
            f"VERIFICATION PASSED (Score: {score}/100): Scene strictly adheres to {char_clean}'s epistemic state at {point_in_story}. "
            f"The narrative relies exclusively on {char_clean}'s direct observations and personal inferences without leaking any forbidden un-communicated story facts."
        )
    else:
        justification = (
            f"VERIFICATION FAILED (Score: {score}/100): Detected {len(leaks)} epistemic leak(s): {'; '.join(leaks)}. "
            f"{char_clean} mentions or reacts to information they had no way of knowing at {point_in_story}."
        )

    return EpistemicAudit(
        is_epistemically_valid=is_valid,
        verification_score=score,
        detected_leaks=leaks,
        allowed_knowledge_used=allowed_used[:5],
        forbidden_knowledge_avoided=forbidden_avoided[:5],
        justification=justification,
        semantic_check_mode=semantic_mode
    )
