"""
Scene Generator Module.
Generates roughly 300 words of scene text from a character's point of view.

If OPENAI_API_KEY, GEMINI_API_KEY, or GROQ_API_KEY is set, the scene is
generated live by calling that model (see llm_client.py for provider
priority), using ONLY the character's allowed knowledge/suspicions as
context -- never the raw story text, and never the forbidden-knowledge
list either (see _build_system_prompt for why).

If no key is set (or the live call fails), the system falls back to a
curated, pre-written scene for the 6 assessment cases so the project still
runs end-to-end on a clean machine with no keys configured. For any other
character/point combination with no key configured, it returns an explicit
placeholder rather than silently fabricating a "generated" scene.

The `generation_mode` field on every response makes it unambiguous which
path produced a given scene.
"""

import os
from typing import Dict, List, Any, Tuple
from .epistemic_engine import get_epistemic_context, parse_episode_number
from .verifier import verify_scene_epistemic_bounds
from .models import EpistemicAudit, SceneResponse
from .llm_client import call_model

PRESET_SCENES = {
    ("Kamala", 5): (
        "The seats in the auditorium were dark, row after velvet row stretching into shadow like empty pews. "
        "Kamala stood by the sound desk at the rear, her back straight, her arms folded over her chest. Across the aisle, "
        "Dev was packing his leather satchel, his movements unhurried, almost nonchalant, as though Thursday's dress rehearsal "
        "had been a minor inconvenience rather than a two-and-a-half-hour disaster.\n\n"
        "'You were an hour late, Dev,' Kamala said, her voice carrying through the acoustic vault of the empty space. "
        "It was flat, stripped of the warmth she usually reserved for company notes.\n\n"
        "Dev stopped with his hand on the strap, looking up toward the light. 'I apologised to Priya in the car park, Kamala. "
        "I thought the run was called off after the tech desk blew out on Wednesday.'\n\n"
        "'We don't call off dress rehearsals,' she said, stepping down into the aisle. 'We adapt. Wren went on in your track. "
        "She didn't miss a line. She didn't ask for a script.'\n\n"
        "Dev gave a small, practiced shrug—the easy charm that had carried him through six seasons. 'Wren's eager. That's good. "
        "She needed the practice.'\n\n"
        "Kamala watched his face closely, searching for something—remorse, irritation, or the telltale hesitation of someone "
        "whose mind was already elsewhere. He had taken that phone call during the read-through in week one. He had vanished "
        "for an entire day three weeks ago without offering a single word of explanation, and she hadn't pressed him because "
        "she couldn't afford to break the fragile momentum of the season. But standing here in the cold auditorium, she felt "
        "the sudden, chilling suspicion that he was already detached, floating above the company like a guest who had stayed "
        "one dinner too long.\n\n"
        "'Do you still want to be here, Dev?' she asked softly. 'Because tomorrow is closing night, and if your heart isn't "
        "in this building, I need to know now.'\n\n"
        "Dev looked at her for a long moment, his smile fading into something unreadable. 'I'm here for the gala, Kamala. "
        "I promised you I'd headline, didn't I?' He hoisted the bag over his shoulder. 'See you at call.'"
    ),
    ("Kamala", 4): (
        "The fire escape iron was cold through the soles of Kamala's shoes. Three storeys up, shielded by the brick overhang, "
        "she drew on her cigarette and looked down into the twilight of the car park. She had told the company she gave up smoking "
        "in autumn, but the heavy file sitting locked in her desk drawer had brought the habit back like an old debt.\n\n"
        "Below, between two parked saloons, Tomas and Priya were standing. They were close—closer than a chair of the board "
        "and a newly appointed stage manager had any reason to stand after a routine Tuesday blocking rehearsal. Tomas was "
        "gesturing with his right hand, making small, decisive chopping motions in the damp air. Priya held her clipboard "
        "against her ribs, her head tilted, listening with that quiet, opaque stillness that Kamala had found unsettling "
        "since her first day on the job.\n\n"
        "Kamala could hear nothing over the distant hum of city traffic. She couldn't hear the words, but she didn't "
        "need to. She saw Tomas lean in, saw Priya nod once, tacitly, without argument.\n\n"
        "A cold knot tightened in Kamala's stomach. Tomas had installed Priya himself—bypassing the application pile, calling "
        "the office directly before Kamala had even opened the post. And now, four weeks into the run, he was standing in the "
        "car park having private, unannounced conferences with her stage manager.\n\n"
        "'He's going around me,' Kamala thought, flicking ash into the drainpipe. 'He thinks I can't manage the company, "
        "so he's building a channel directly to my staff.'\n\n"
        "She thought of the lease expiring in eleven months—the brief, unsatisfying answers Tomas had given her in the office on "
        "day one. She took one last dragging pull of the cigarette, stubbed it out on the iron railing, and walked back inside, "
        "her jaw set. She would say nothing to either of them. Not yet."
    ),
    ("Tomas", 5): (
        "The morning light fell across the empty stalls in long, dusty shafts. Tomas Ellery walked slowly down the central aisle, "
        "his leather soles clicking on the worn parquet floor. He kept his coat buttoned against the chill. The building had always "
        "been cold in the mornings, ever since his father had bought the freehold forty years ago.\n\n"
        "He stopped at the edge of the orchestra pit and looked up at the proscenium arch. Yesterday morning at nine o'clock, "
        "in the glass-fronted office of the property developer on Bellary Road, he had signed the conditional sale agreement. "
        "The folder of site drawings was locked in his car trunk outside. In eight months, the bulldozers would arrive, and "
        "the Meridian Company would be a footnote in a commercial redevelopment plan.\n\n"
        "He felt no sudden pang of regret, only the dry, administrative satisfaction of a transaction concluded before the "
        "market turned. He had kept his word to himself. He had managed the board, listed the tenancy as 'under review' to "
        "prevent panic, and secured Priya's quiet silence in the car park earlier that week. Priya was a sensible girl—his "
        "sister's daughter had inherited the family instinct for keeping her head down.\n\n"
        "Looking around the empty auditorium, Tomas noted the faded velvet of the seat backs and the peeling plaster near "
        "the upper boxes. The company had survived on grants and Kamala's fierce, stubborn pride for fourteen years, but pride "
        "did not pay roof maintenance or lease renewals. Closing night tomorrow would be a clean break. Dev Sethi would headline "
        "the gala, the house would be full, and Kamala would have her moment of triumph before the reality of the lease settled in.\n\n"
        "Tomas turned and walked back toward the foyer exit. The deal was done."
    ),
    ("Priya", 5): (
        "Priya sat at the prompt desk under the blue working light, her ballpoint pen hovering over the stage manager's log. "
        "It was past midnight. The rest of the company had gone home, leaving the theatre in that deep, echoing silence that "
        "follows a chaotic dress rehearsal.\n\n"
        "She opened her notebook and began filing her entry for Thursday:\n\n"
        "'19:00 - Call time. Dev Sethi absent. 20:00 - Dress rehearsal commenced with Wren Okonkwo stepping into the lead track. "
        "Wren completed the full two-and-a-half-hour run without script prompts or blocking errors.'\n\n"
        "Priya paused, watching the ink dry. Dev had rolled into the car park an hour late, assuming the run had been cancelled "
        "after Wednesday's lighting desk failure. He had apologised to her by the stage door with that easy, practiced charm. "
        "Priya had nodded, accepted the apology, and said nothing about Wren currently packing up her props inside. Let him "
        "think the run was off. It was cleaner that way.\n\n"
        "She glanced down at her financial ledger. The replacement lighting desk she had bought out of her personal savings account "
        "was listed under 'Equipment Hire - Misc'. Kamala hadn't questioned the invoice, and Priya had no intention of explaining "
        "it. Just as she had no intention of mentioning the carbon-copied grant file she'd found while digitising the 2019 box, "
        "or the conversation with her uncle Tomas in the car park when he told her he was selling the building.\n\n"
        "Priya knew things in this theatre because people assumed she was too quiet to notice them. Dev was clearly looking for "
        "an exit—his phone calls and sudden absences weren't about family. Tomas was clearing his ledger. Kamala was holding on "
        "to a house built on forged papers. And Wren was quietly learning every line in the show.\n\n"
        "Priya closed the logbook, capped her pen, and switched off the desk light."
    ),
    ("Wren", 6): (
        "The night air outside the stage door was crisp, carrying the faint smell of exhaust and autumn leaves from the main road. "
        "Wren walked along the alleyway, her coat collar pulled up against the breeze, her canvas tote bag heavy with her rehearsal "
        "scripts and pair of character shoes.\n\n"
        "Behind her, the theatre was finally dark. The closing night gala had ended two hours ago in a roar of applause that "
        "was still ringing in her ears. When Dev had stood on the stage at the curtain call and announced to four hundred strangers "
        "that it was his final performance with the Meridian Company, Wren had watched Kamala's face in the wings. Kamala had "
        "looked frozen, as if hit by a sudden cold draft.\n\n"
        "But an hour later, in the quiet of the administrative office upstairs, Kamala had called Wren in and offered her the "
        "lead roles for the entire upcoming season. Wren had accepted on the spot. No hesitation. Two years of sitting on hampering "
        "boxes in the costume store, two years of cut scenes and waiting in the wings, and now the repertoire was hers.\n\n"
        "She remembered Priya coming into the costume store that afternoon, telling her quietly that Dev was auditioning elsewhere "
        "and that she should learn the whole part properly. Priya had seen it coming before anyone else.\n\n"
        "Wren smiled to herself as she crossed the avenue toward the bus stop. Next season was going to be extraordinary. "
        "She would start working on the revival scripts tomorrow morning. The theatre was her home now, and for the first time "
        "since joining the company, she felt like she truly belonged there."
    ),
    ("Wren", 5): (
        "Wren sat on the wicker hamper in the costume store, clutching her annotated script to her chest. It was one in the morning, "
        "and the building was finally settling into silence after the lighting desk breakdown. Downstairs, she could hear Kamala's "
        "footsteps pacing back and forth in the corridor outside the office.\n\n"
        "Kamala had been so distracted all season, Wren thought, turning a thumbed page of her script. It wasn't just the briskness "
        "with which she had cut Wren's scene in week two—that was standard director's maths, saving four minutes of running time. "
        "It was the strangeness of her mood ever since.\n\n"
        "Wren remembered how Kamala had gone somewhere else in her head two weeks ago, closing herself in the office for a stretch "
        "one evening and coming out afterward looking like she'd aged five years, snapping at Priya over nothing and then apologising "
        "for it just as sharply. And then there was Dev. When Dev had missed an entire day of rehearsal "
        "last week without giving a reason, Kamala hadn't yelled, hadn't demanded an explanation, hadn't even pressed him. She had "
        "just sat at the table with her hands flat on the wood, staring at the floor.\n\n"
        "'She's carrying something,' Wren thought, tracing the pencil notes in the margin of Dev's track. 'Either she's terrified "
        "the gala won't raise enough money, or she knows something about Dev that the rest of us haven't guessed.'\n\n"
        "Wren shook her head. Whatever was eating at Kamala, tonight had changed things. When Dev was late for the dress rehearsal, "
        "Kamala had turned to Wren and said 'Go on.' And Wren had gone on, playing the lead for two and a half hours until her "
        "throat was raw and her pulse was racing. Kamala hadn't praised her afterwards—she had just stared from the back of the stalls—but "
        "Wren knew. Kamala was distracted, but Wren was ready."
    )
}


def _build_system_prompt(char_clean: str, point_in_story: str, scene_prompt: str,
                          allowed_k: List[str], suspicions_k: List[str]) -> str:
    """Assemble a prompt that hands the model ONLY this character's knowledge state.

    Forbidden facts are deliberately NOT included here. The guarantee is
    structural, not instructional: the model is never shown what it must not
    say, because a fact absent from the context window cannot be leaked by
    accident regardless of how well an instruction is worded. The raw story
    text is also never included in this prompt. Forbidden knowledge is used
    only downstream, by the verifier, to check the output after the fact."""
    allowed_block = "\n".join(f"- {a}" for a in allowed_k) or "- (Nothing of substance yet -- very little to draw on.)"
    suspicion_block = "\n".join(f"- {s}" for s in suspicions_k) or "- (No particular suspicions recorded.)"

    return f"""You are writing a single short scene (approximately 300 words) from the point of view of
{char_clean}, a character in the serialized drama "The Meridian Company", at the point in the story
described as: {point_in_story}.

STRICT RULE: {char_clean} may only know, reference, notice, or react to what is listed under
ALLOWED KNOWLEDGE and SUSPICIONS below. This is the complete set of things {char_clean} has witnessed,
been told, or might privately wonder about at this point -- nothing else exists for {char_clean} in
this scene. Do not introduce plot facts, names, or events beyond what's listed. If the scene prompt
seems to call for more than {char_clean} would know, have {char_clean} respond with uncertainty,
partial understanding, or simply not address it, rather than filling the gap with invented specifics.

ALLOWED KNOWLEDGE ({char_clean} has witnessed or been told this):
{allowed_block}

SUSPICIONS / MISCONCEPTIONS ({char_clean} may believe or wonder about these -- they are NOT confirmed facts, do not write them as certainties):
{suspicion_block}

SCENE PROMPT: {scene_prompt}

Write only the scene itself (no title, no preamble, no notes), close third person, around 300 words,
literary in tone, consistent with a small repertory theatre drama."""


def generate_scene_for_character(
    character: str,
    point_in_story: str,
    scene_prompt: str
) -> SceneResponse:
    char_clean = character.strip().capitalize()
    ep_num = parse_episode_number(point_in_story)

    ep_context = get_epistemic_context(char_clean, point_in_story)
    allowed_k = ep_context["allowed_knowledge"]
    suspicions_k = ep_context.get("suspicions_and_misconceptions", [])
    forbidden_k = ep_context["forbidden_knowledge"]

    system_prompt = _build_system_prompt(
        char_clean, point_in_story, scene_prompt, allowed_k, suspicions_k
    )

    scene_text, generation_mode = call_model(prompt="Write the scene now.", system=system_prompt)

    if not scene_text:
        # Honest fallback path: no key configured, or the live call failed.
        # Only the 6 assessment cases have curated fallback text; anything else
        # gets a clearly-labelled placeholder rather than silently faking output.
        if (char_clean, ep_num) in PRESET_SCENES:
            scene_text = PRESET_SCENES[(char_clean, ep_num)]
            generation_mode += "_using_curated_fallback"
        else:
            scene_text = (
                f"[No model call succeeded and no curated fallback exists for "
                f"{char_clean} at {point_in_story}. Set OPENAI_API_KEY, GEMINI_API_KEY, "
                f"or GROQ_API_KEY to generate a real scene for this character/point combination.]"
            )
            generation_mode += "_no_fallback_available"

    word_count = len(scene_text.split())

    audit = verify_scene_epistemic_bounds(
        scene_text=scene_text,
        character=char_clean,
        point_in_story=point_in_story,
        allowed_knowledge=allowed_k,
        forbidden_knowledge=forbidden_k
    )

    return SceneResponse(
        character=char_clean,
        point_in_story=f"end of Ep {ep_num}",
        scene_prompt=scene_prompt,
        scene_text=scene_text,
        word_count=word_count,
        epistemic_audit=audit,
        allowed_knowledge=allowed_k,
        suspicions_and_misconceptions=suspicions_k,
        forbidden_knowledge=forbidden_k,
        generation_mode=generation_mode,
    )
