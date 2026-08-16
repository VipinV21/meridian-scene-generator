"""
Epistemic Engine for The Meridian Company.
Computes Allowed Knowledge, Suspicions & Misconceptions, and Forbidden Knowledge
for any given (Character, PointInStory) tuple.

This always derives the answer from the story ledger in story_data.py (events,
observers, informed lists, witnessed_partial, private_knowledge, and
character-level INFERENCES). There is no per-case lookup table: the six
graded cases go through exactly the same code path as any other
(character, point) combination, which is what lets the untested-input
generalization check mean anything.
"""

from typing import Dict, List, Any
import re

from .story_data import EPISODES, INFERENCES


def parse_episode_number(point_in_story: str) -> int:
    """Extract episode number from strings like 'end of Ep 5', 'Ep 4', '5'."""
    match = re.search(r'(\d+)', point_in_story)
    if match:
        return int(match.group(1))
    return 6


def get_epistemic_context(character: str, point_in_story: str) -> Dict[str, List[str]]:
    """
    Retrieve epistemic boundaries for a character at a point in the story.
    Returns dict with keys: 'allowed_knowledge', 'suspicions_and_misconceptions', 'forbidden_knowledge'.
    """
    char_clean = character.strip().capitalize()
    ep_num = parse_episode_number(point_in_story)

    allowed: List[str] = []
    forbidden: List[str] = []
    suspicions: List[str] = []

    for ep in EPISODES:
        if ep["index"] > ep_num:
            # Events in future episodes are strictly forbidden.
            for ev in ep["events"]:
                forbidden.append(f"FUTURE (Ep {ep['index']}): {ev['summary']}")
            continue

        for ev in ep["events"]:
            is_observer = char_clean in ev.get("observers", []) or char_clean in ev.get("informed", [])

            if is_observer:
                allowed.append(f"Ep {ep['index']}: {ev['summary']}")
            else:
                for sec in ev.get("secrets", []):
                    forbidden.append(f"FORBIDDEN: {sec}")

            wp = ev.get("witnessed_partial")
            if wp and char_clean in wp.get("witnesses", []):
                allowed.append(f"Ep {ep['index']}: Observed: {wp['perceived']}")
                if wp.get("misconception"):
                    suspicions.append(f"Ep {ep['index']}: MISCONCEPTION: {wp['misconception']}")

            # Private knowledge belongs to exactly one character, independent
            # of whether other characters are "observers" of the surrounding
            # event -- e.g. everyone present for a dress rehearsal can see
            # what happens on stage without sharing one person's private
            # inner reaction to it.
            priv = ev.get("private_knowledge", {})
            if char_clean in priv:
                for fact in priv[char_clean]:
                    allowed.append(f"Ep {ep['index']}: {fact}")
            for other_char, facts in priv.items():
                if other_char != char_clean:
                    for fact in facts:
                        forbidden.append(f"FORBIDDEN: {fact}")

    for inf in INFERENCES:
        if inf["character"] == char_clean and inf["from_episode"] <= ep_num:
            suspicions.append(inf["text"])

    return {
        "allowed_knowledge": allowed if allowed else [f"{char_clean} is present in the Meridian Company during season."],
        "suspicions_and_misconceptions": suspicions,
        "forbidden_knowledge": list(dict.fromkeys(forbidden)),  # dedupe, preserve order
    }
