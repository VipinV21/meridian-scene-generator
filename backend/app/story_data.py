"""
Story Ledger & Epistemic Graph for The Meridian Company.
Encodes narrative events, direct observers, secrets, character inferences/misconceptions,
and forbidden facts per character across episodes 1 to 6.
"""

from typing import Dict, List, Any

EPISODES = [
    {
        "index": 1,
        "title": "Call Sheet",
        "events": [
            {
                "id": "1.1",
                "summary": "Kamala announces season close revival of 'The Winter Boarders' in green room. Dev Sethi applauds loudest. Wren Okonkwo takes notes. Tomas Ellery stands at back in coat.",
                "observers": ["Kamala", "Dev", "Wren", "Tomas"],
                "informed": ["Priya"],
                "secrets": []
            },
            {
                "id": "1.2",
                "summary": "Tomas tells Kamala privately in office lease expires in 11 months, will not renew automatically. Process has not started. Kamala asks 2 questions, gets unsatisfying answers, tells no one.",
                "observers": ["Tomas", "Kamala"],
                "informed": [],
                "secrets": ["Lease non-renewal process"]
            },
            {
                "id": "1.3a",
                "summary": "Priya Nair introduced as stage manager at the read-through, with a clipboard and a very quiet manner.",
                "observers": ["Kamala", "Dev", "Wren", "Priya", "Tomas"],
                "informed": [],
                "secrets": []
            },
            {
                "id": "1.3b",
                "summary": "Tomas arranged Priya's hire himself, by telephone, before Kamala ever saw an application.",
                "observers": ["Tomas", "Priya"],
                "informed": [],
                "secrets": ["Tomas arranged Priya's hire directly, bypassing the normal application process"]
            },
            {
                "id": "1.3c",
                "summary": "Priya is Tomas's sister's daughter -- his niece. Neither of them mentions this to anyone at the read-through or afterward.",
                "observers": ["Tomas", "Priya"],
                "informed": [],
                "secrets": ["Priya is Tomas's niece"]
            },
            {
                "id": "1.4",
                "summary": "Dev gets call from Mumbai casting agent during read-through. Excuses himself for 4 mins, lies that it was his brother-in-law.",
                "observers": ["Dev"],
                "informed": [],
                "witnessed_partial": {
                    "witnesses": ["Kamala", "Priya", "Wren"],
                    "perceived": "Dev received a phone call during read-through and claimed it was his brother-in-law."
                },
                "secrets": ["Dev's call was from a Mumbai casting agent"]
            }
        ]
    },
    {
        "index": 2,
        "title": "Blocking",
        "events": [
            {
                "id": "2.1",
                "summary": "Kamala cuts Wren's only scene in front of Dev and Priya to save 4 minutes. Tomas is absent.",
                "observers": ["Kamala", "Wren", "Dev", "Priya"],
                "informed": [],
                "secrets": []
            },
            {
                "id": "2.2",
                "summary": "Wren cries in costume store on hamper. Priya finds her, sits beside her. Priya tells no one.",
                "observers": ["Wren", "Priya"],
                "informed": [],
                "secrets": ["Wren cried in costume store", "Priya comforted Wren"]
            },
            {
                "id": "2.3",
                "summary": "Dev calls wife from car park: accepted serial in Hyderabad starting March, leaving company after closing night. Tells no one else.",
                "observers": ["Dev"],
                "informed": [],
                "secrets": ["Dev accepted Hyderabad serial starting March", "Dev leaving after closing night"]
            },
            {
                "id": "2.4",
                "summary": "Tomas meets property developer at hotel on Bellary Road, gets folder of drawings. Mentions to no one.",
                "observers": ["Tomas"],
                "informed": [],
                "secrets": ["Tomas meeting with property developer", "Building sale drawings"]
            },
            {
                "id": "2.5",
                "summary": "Kamala takes 2019 arts council grant file from archive and locks it in her desk drawer while alone in building.",
                "observers": ["Kamala"],
                "informed": [],
                "secrets": ["Kamala locked 2019 grant file in desk drawer"]
            }
        ]
    },
    {
        "index": 3,
        "title": "The Grant",
        "events": [
            {
                "id": "3.1",
                "summary": "14 years ago, Kamala forged co-founder's signature on grant application for roof. Roof was built. She never told anyone.",
                "observers": ["Kamala"],
                "informed": [],
                "secrets": ["Kamala forged grant signature 14 years ago"]
            },
            {
                "id": "3.2",
                "summary": "Priya digitising archive finds carbon-copied duplicate of 2019 grant application in box of programmes. Reads it, understands forgery, puts back, tells no one.",
                "observers": ["Priya"],
                "informed": [],
                "secrets": ["Priya found carbon copy of forged grant file", "Priya knows Kamala forged signature"]
            },
            {
                "id": "3.3",
                "summary": "Dev misses entire day of rehearsal for screen test in Chennai (went well). Kamala, Priya, Wren wait. Dev gives no reason, Kamala doesn't press. Tomas hears nothing.",
                "observers": ["Dev"],
                "informed": [],
                "witnessed_partial": {
                    "witnesses": ["Kamala", "Priya", "Wren"],
                    "perceived": "Dev missed an entire day of rehearsal without providing an explanation."
                },
                "secrets": ["Dev was in Chennai for screen test", "Screen test went well"]
            },
            {
                "id": "3.4",
                "summary": "Priya quietly rewrites understudy plot so Wren covers Dev's role. Doesn't clear with Kamala. Tells Wren to start learning.",
                "observers": ["Priya", "Wren"],
                "informed": [],
                "secrets": ["Priya assigned Dev's understudy track to Wren", "Wren learning Dev's role in secret"]
            }
        ]
    },
    {
        "index": 4,
        "title": "Car Park",
        "events": [
            {
                "id": "4.1",
                "summary": "Tomas tells Priya in car park after Tuesday rehearsal he is selling building. Wants no one to hear until after closing night. Priya agrees tacitly.",
                "observers": ["Tomas", "Priya"],
                "informed": [],
                "witnessed_partial": {
                    "witnesses": ["Kamala"],
                    "perceived": "Kamala saw Tomas and Priya standing close together in the car park from the 3rd floor fire escape. She heard nothing.",
                    "misconception": "Kamala concluded that Tomas is going around her to her own staff, and suspects the two of them are conspiring on company or lease business without her."
                },
                "secrets": ["Tomas is selling building", "Tomas told Priya about sale in car park"]
            },
            {
                "id": "4.2",
                "summary": "Tomas at board meeting describes tenancy as 'under review' and moves to next item.",
                "observers": ["Tomas", "Kamala"],
                "informed": ["Dev", "Wren", "Priya"],
                "secrets": []
            },
            {
                "id": "4.3",
                "summary": "Kamala announces fundraising gala on closing night. Asks Dev to headline. Dev agrees. Kamala says 'don't know what I'd do without you'.",
                "observers": ["Kamala", "Dev", "Wren", "Priya"],
                "informed": ["Tomas"],
                "secrets": []
            },
            {
                "id": "4.4",
                "summary": "Dev decides alone in dressing room to announce departure on gala stage so he doesn't watch Kamala's reaction.",
                "observers": ["Dev"],
                "informed": [],
                "secrets": ["Dev plans to announce departure from gala stage"]
            }
        ]
    },
    {
        "index": 5,
        "title": "Dry Run",
        "events": [
            {
                "id": "5.1",
                "summary": "Tech rehearsal overruns past midnight due to lighting desk failure. Kamala, Dev, Priya, Wren present till 1 AM. Tomas is NOT told.",
                "observers": ["Kamala", "Dev", "Priya", "Wren"],
                "informed": [],
                "secrets": ["Lighting desk failed during tech rehearsal"]
            },
            {
                "id": "5.2",
                "summary": "Priya pays for replacement lighting desk out of own account, files as hire charge. Mentions to no one.",
                "observers": ["Priya"],
                "informed": [],
                "secrets": ["Priya paid for replacement lighting desk from personal money"]
            },
            {
                "id": "5.3",
                "summary": "Dress rehearsal Thursday: Dev is 1 hr late. Kamala puts Wren on in Dev's part. Wren is extraordinary for 2.5 hours. Dev arrives late, apologises to Priya in car park, assumes run was cancelled. Nobody corrects him.",
                "observers": ["Kamala", "Priya", "Wren"],
                "witnessed_partial": {
                    "witnesses": ["Dev"],
                    "perceived": "Dev arrived 1 hour late, saw people leaving, assumed dress rehearsal was cancelled, apologised to Priya."
                },
                "secrets": [
                    "Wren performed Dev's role in dress rehearsal and was extraordinary",
                    "Dev believes dress rehearsal was cancelled"
                ],
                "private_knowledge": {
                    "Kamala": [
                        "Kamala privately admitted to herself, watching from the back of the stalls, that Wren is better in the part than Dev has been in six years. She told no one."
                    ]
                }
            },
            {
                "id": "5.4",
                "summary": "Tomas signs conditional sale agreement at developer's office on Friday morning.",
                "observers": ["Tomas"],
                "informed": [],
                "secrets": ["Tomas signed conditional sale agreement for building"]
            }
        ]
    },
    {
        "index": 6,
        "title": "Closing Night",
        "events": [
            {
                "id": "6.1",
                "summary": "Priya tells Wren in costume store she's sure Dev is auditioning elsewhere, tells Wren to learn whole part properly. Wren tells no one.",
                "observers": ["Priya", "Wren"],
                "informed": [],
                "secrets": ["Priya suspected Dev auditioning elsewhere", "Priya advised Wren to learn full lead part"]
            },
            {
                "id": "6.2",
                "summary": "House sells out. Gala performance occurs.",
                "observers": ["Kamala", "Dev", "Priya", "Wren", "Tomas"],
                "informed": [],
                "secrets": []
            },
            {
                "id": "6.3",
                "summary": "Dev announces from stage at end of gala that this was his last performance with company. Kamala in wings 11ft away hears it same time as audience.",
                "observers": ["Dev", "Kamala", "Priya", "Wren", "Tomas"],
                "informed": [],
                "secrets": []
            },
            {
                "id": "6.4",
                "summary": "Tomas leaves before curtain call. Company watches him go.",
                "observers": ["Tomas", "Kamala", "Priya", "Wren", "Dev"],
                "informed": [],
                "secrets": []
            },
            {
                "id": "6.5",
                "summary": "Kamala burns 2019 grant file in metal bin in alley behind scene dock.",
                "observers": ["Kamala"],
                "informed": [],
                "secrets": ["Kamala burned 2019 grant file"]
            },
            {
                "id": "6.6",
                "summary": "Priya stands at stage door, decides NOT to tell Kamala about sale, goes home.",
                "observers": ["Priya"],
                "informed": [],
                "secrets": ["Priya kept building sale secret from Kamala"]
            },
            {
                "id": "6.7",
                "summary": "Kamala offers Wren lead roles for next season in office. Wren accepts. Neither mentions building.",
                "observers": ["Kamala", "Wren"],
                "informed": [],
                "secrets": []
            }
        ]
    }
]


# Character-specific inferences: conclusions a character draws by connecting
# facts they already legitimately hold, rather than a fact anyone told them.
# These are NOT sourced from a single event, so they don't live on an event's
# "secrets"/"private_knowledge" -- instead each entry declares which character
# holds it and from which episode it becomes plausible for them to have formed
# it. The engine surfaces an inference once ep_num >= from_episode, for any
# point in the story, not just the six graded cases -- this is what keeps
# suspicions/misconceptions generalizable instead of being hand-pasted per case.
INFERENCES = [
    {
        "character": "Kamala",
        "from_episode": 5,
        "text": (
            "SUSPICION: Dev seems disengaged or unreliable -- based on the phone call he took "
            "during the read-through, the day of rehearsal he missed without explanation, and his "
            "lateness to dress rehearsal -- though she does not know why."
        ),
    },
    {
        "character": "Priya",
        "from_episode": 5,
        "text": (
            "SUSPICION: Dev may be auditioning or seeking work elsewhere, based on the phone call "
            "in week one, his unexplained missing day, and his lateness to dress rehearsal -- the "
            "specifics (Hyderabad, Chennai) remain unknown to her."
        ),
    },
    {
        "character": "Wren",
        "from_episode": 2,
        "text": (
            "PUZZLE: Wren notices Kamala has seemed unusually brisk and distracted (cutting her scene "
            "abruptly, not explaining why) but does not know the cause."
        ),
    },
    {
        "character": "Wren",
        "from_episode": 5,
        "text": (
            "PUZZLE: Wren wonders why Kamala has been so distracted and uncharacteristically lenient "
            "with Dev -- not pressing him about his missing day, locking a drawer -- without knowing why."
        ),
    },
    {
        "character": "Tomas",
        "from_episode": 4,
        "text": (
            "BELIEF: Tomas believes the sale of the building is proceeding smoothly and privately, and "
            "assumes Priya will keep it to herself until after closing night as agreed."
        ),
    },
]
