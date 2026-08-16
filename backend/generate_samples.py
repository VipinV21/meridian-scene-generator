import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
samples = client.get('/api/samples').json()

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'samples')
os.makedirs(SAMPLES_DIR, exist_ok=True)

filenames = [
    'case1_kamala_ep5',
    'case2_kamala_ep4',
    'case3_tomas_ep5',
    'case4_priya_ep5',
    'case5_wren_ep6',
    'case6_wren_ep5'
]

for sample, fname in zip(samples, filenames):
    # Save JSON
    json_path = os.path.join(SAMPLES_DIR, f"{fname}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(sample, f, indent=2)
    
    # Save Markdown
    md_path = os.path.join(SAMPLES_DIR, f"{fname}.md")
    
    lines = []
    lines.append(f"# Assessment Case {sample['case_number']}: {sample['character']} ({sample['point_in_story']})")
    lines.append("")
    lines.append(f"**Scene Prompt:** {sample['scene_prompt']}")
    lines.append("")
    lines.append("## Test Case Epistemic Analysis")
    lines.append(sample['test_case_analysis'])
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## Generated Scene (~{sample['word_count']} words)")
    lines.append("")
    lines.append(f"*Generation mode: `{sample.get('generation_mode', 'unknown')}`*")
    lines.append("")
    lines.append(sample['scene_text'])
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Epistemic Audit & Verification Proof")
    lines.append("")
    status_str = "VALID" if sample['epistemic_audit']['is_epistemically_valid'] else "INVALID"
    lines.append(f"- **Status:** {status_str}")
    lines.append(f"- **Verification Score:** {sample['epistemic_audit']['verification_score']}/100")
    leaks_str = sample['epistemic_audit']['detected_leaks'] if sample['epistemic_audit']['detected_leaks'] else "None (0 leaks detected)"
    lines.append(f"- **Detected Leaks:** {leaks_str}")
    lines.append(f"- **Justification:** {sample['epistemic_audit']['justification']}")
    lines.append("")
    lines.append("### Allowed Knowledge Used:")
    for ak in sample['allowed_knowledge']:
        lines.append(f"- {ak}")
    lines.append("")
    if sample.get('suspicions_and_misconceptions'):
        lines.append("### Suspicions & Inferred Misconceptions:")
        for sm in sample['suspicions_and_misconceptions']:
            lines.append(f"- {sm}")
        lines.append("")
    lines.append("### Explicit Forbidden Facts Avoided:")
    for fk in sample['forbidden_knowledge']:
        lines.append(f"- {fk}")
    lines.append("")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

print("Successfully generated all sample outputs in samples/")
