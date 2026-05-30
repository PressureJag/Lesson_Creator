"""Generate teaching approach options for each objective block."""

import json
import re


# ── Stub options (demo mode) ─────────────────────────────────────────────────

def _diagram_for(obj_lower: str):
    """Return (diagram_type, friendly_name) for an objective."""
    if any(w in obj_lower for w in ["percent", "fraction", "ratio", "proportion"]):
        return "percentage_bar", "percentage bar model"
    if any(w in obj_lower for w in ["inequalit", "integer", "number line"]):
        return "number_line", "number line"
    if any(w in obj_lower for w in ["expand", "bracket", "factoris", "grid", "multipl"]):
        return "area_grid", "area / grid model"
    if any(w in obj_lower for w in ["angle", "parallel", "polygon", "triangle"]):
        return "angle", "angle diagram"
    if any(w in obj_lower for w in ["bar", "segment", "share", "collect", "like term"]):
        return "bar_model", "bar model"
    return None, "step-by-step annotated working"


def _context_for(obj_lower: str) -> str:
    if any(w in obj_lower for w in ["percent", "discount", "tax", "interest"]):
        return "shopping / finance"
    if any(w in obj_lower for w in ["speed", "distance", "time", "travel"]):
        return "sport / travel"
    if any(w in obj_lower for w in ["ratio", "recipe", "mixture", "scale"]):
        return "cooking / scale models"
    if any(w in obj_lower for w in ["angle", "parallel", "polygon"]):
        return "architecture / engineering"
    if any(w in obj_lower for w in ["algebra", "equation", "formula"]):
        return "science / coding patterns"
    return "everyday problem solving"


def _stub_options(objective: str) -> list:
    obj_lower = objective.lower()
    diag_type, diag_name = _diagram_for(obj_lower)
    context = _context_for(obj_lower)

    options = [
        {
            "label": f"{diag_name.capitalize()} + {context} hook",
            "description": f"Visual: {diag_name}. Hook context: {context}. Standard I/We/You Do sequence.",
            "diagram": diag_type,
            "skip": False,
        },
        {
            "label": "Algebraic / symbolic approach",
            "description": "Focus on generalised method with symbolic notation. Abstract hook: 'when does this pattern break?'",
            "diagram": None,
            "skip": False,
        },
        {
            "label": "Concrete → Pictorial → Abstract sequence",
            "description": "Start with a physical/visual model, bridge to pictorial representation, then symbolic.",
            "diagram": diag_type,
            "skip": False,
        },
        {
            "label": "Problem-first (low threshold, high ceiling)",
            "description": "Pose an open problem before the method is taught; method emerges from student attempts.",
            "diagram": None,
            "skip": False,
        },
        {
            "label": "Skip this objective",
            "description": "Omit this objective block from the deck entirely.",
            "diagram": None,
            "skip": True,
        },
    ]
    return options


# ── AI-generated options (full mode) ────────────────────────────────────────

def _ai_options(objective: str, topic: str, methods_text: str) -> list:
    from generator import content_gen

    prompt = f"""You are an experienced UK secondary maths teacher for Outwood Grange Academies Trust.

Topic: {topic}
Objective: {objective}
Common Methods guidance: {methods_text[:400] if methods_text else "Not provided"}

Generate exactly 4 distinct teaching approaches for this objective.
Each approach should differ meaningfully in: diagram choice, hook/context, or pedagogical sequence.
All approaches must align with the school's Consistent Methodology (I Do / We Do / You Do).
Label: 5-8 words. Description: 1 short sentence.

Respond ONLY with valid JSON:
{{"options": [
  {{"label": "...", "description": "...", "diagram": "bar_model|number_line|area_grid|percentage_bar|angle|null"}},
  {{"label": "...", "description": "...", "diagram": "..."}},
  {{"label": "...", "description": "...", "diagram": "..."}},
  {{"label": "...", "description": "...", "diagram": "..."}}
]}}"""

    try:
        text = content_gen._call(prompt, max_tokens=600)
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            opts = []
            for o in data["options"]:
                diag = o.get("diagram") or None
                if diag == "null":
                    diag = None
                opts.append({
                    "label": o["label"],
                    "description": o["description"],
                    "diagram": diag,
                    "skip": False,
                })
            opts.append({
                "label": "Skip this objective",
                "description": "Omit this objective block from the deck entirely.",
                "diagram": None,
                "skip": True,
            })
            return opts
    except Exception:
        pass

    return _stub_options(objective)


# ── Public API ───────────────────────────────────────────────────────────────

def get_options(objective: str, topic: str, methods_text: str) -> list:
    """
    Return list of option dicts for this objective. Each dict has:
      label: str, description: str, diagram: str|None, skip: bool
    """
    from generator import content_gen
    if content_gen._demo_mode:
        return _stub_options(objective)
    return _ai_options(objective, topic, methods_text)


def to_prompt_list(options: list) -> list:
    """Convert option dicts to (label, description) tuples for prompt_choice."""
    return [(o["label"], o["description"]) for o in options]
