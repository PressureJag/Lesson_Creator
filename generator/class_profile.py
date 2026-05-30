"""Collect class profile (year group and teaching pitch) interactively."""

from .notification import prompt_choice, notify, header

_YEAR_GROUPS = [
    "Year 7",
    "Year 8",
    "Year 9",
    "Year 10",
    "Year 11",
    "KS4 (Mixed)",
]

_PITCHES = [
    (
        "Nurture",
        "Below age-related expectations — simple numbers, extra scaffolding, plain language",
    ),
    (
        "Core",
        "Age-related expectations — standard GCSE content, balanced scaffolding",
    ),
    (
        "Core Plus",
        "At or above expected — GCSE Higher content, reasoning and justification emphasis",
    ),
    (
        "Extension",
        "High attainers — GCSE grade 8–9, proof, generalisation, minimal scaffolding",
    ),
]

_PITCH_GUIDANCE = {
    "Nurture": (
        "This is a nurture-level class. "
        "Use simple integers first and introduce decimals only once the core method is secure. "
        "Add extra scaffold steps and write in short, accessible sentences. "
        "Avoid complex notation. Focus on building confidence and procedural fluency before reasoning."
    ),
    "Core": (
        "This is a core-level class. "
        "Use a balance of integers, decimals, and simple fractions. "
        "Standard GCSE content and notation. "
        "Include clear scaffolding in guided examples but expect independence in You Do."
    ),
    "Core Plus": (
        "This is a core plus (higher-ability) class. "
        "Include reasoning questions and GCSE Higher content. "
        "Use varied and precise notation. "
        "Expect students to explain and justify answers. "
        "Practice questions should reach reasoning and problem-solving levels."
    ),
    "Extension": (
        "This is an extension (highest-attaining) class. "
        "Include challenging examples with complex values (surds, algebraic fractions, negatives, etc.). "
        "Push to GCSE grade 8–9 difficulty and beyond. "
        "Include proof, generalisation, and non-routine problems. "
        "Minimal scaffolding — students are expected to select and apply methods independently."
    ),
}

_DEFAULT_PITCH_INDEX = {
    "Nurture":   0,
    "Core":      1,
    "Core Plus": 2,
    "Extension": 3,
}


def select_profile(
    year: str = None,
    pitch: str = None,
    default_pitch: str = "Core Plus",
) -> dict:
    """
    Interactively collect year group and teaching pitch.

    Returns a dict:
      year_group      — e.g. "Year 9"
      pitch           — e.g. "Core Plus"
      pitch_guidance  — full instructions for the AI
      label           — e.g. "Year 9 — Core Plus"
    """
    header("CLASS PROFILE", "Tell me about the class you are teaching")

    # Year group
    if year and year.strip():
        year_group = year.strip()
        notify(f"Year group: {year_group}", "info")
    else:
        yg_opts = [(yg, "") for yg in _YEAR_GROUPS]
        yi = prompt_choice("YEAR GROUP", yg_opts, default=0, timeout=120)
        year_group = _YEAR_GROUPS[yi]

    # Pitch / ability level
    if pitch and pitch.strip():
        pitch_key = pitch.strip().title()
        if pitch_key not in _PITCH_GUIDANCE:
            pitch_key = default_pitch
        notify(f"Pitch: {pitch_key}", "info")
    else:
        default_idx = _DEFAULT_PITCH_INDEX.get(default_pitch, 2)
        pi = prompt_choice(
            "TEACHING PITCH  (ability level of this class)",
            _PITCHES,
            default=default_idx,
            timeout=120,
        )
        pitch_key = _PITCHES[pi][0]

    guidance = _PITCH_GUIDANCE[pitch_key]
    label = f"{year_group} — {pitch_key}"
    notify(f"Class profile set: {label}", "success")

    return {
        "year_group":     year_group,
        "pitch":          pitch_key,
        "pitch_guidance": guidance,
        "label":          label,
    }
