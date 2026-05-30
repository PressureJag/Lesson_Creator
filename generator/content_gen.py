"""Generate lesson content via the local Claude Code CLI, with stub fallback."""

import json
import shutil
import subprocess

_demo_mode = not bool(shutil.which("claude"))
_class_profile: dict = {}
_class_rating: dict = {}


def set_class_profile(profile: dict) -> None:
    global _class_profile
    _class_profile = profile


def set_rating(rating: dict) -> None:
    global _class_rating
    _class_rating = rating


def _build_system_prompt() -> str:
    base = (
        "UK secondary maths teacher, Outwood Grange Academies Trust. "
        "Rules: all maths correct (verify every calculation); plain-text notation (x^2, sqrt, a/b, ×); "
        "vary ONE feature at a time; Fluency→Reasoning→Problem Solving arc; specific numbers not placeholders."
    )
    if _class_profile:
        base += (
            f"\nClass: {_class_profile.get('label', '')}. "
            f"Pitch: {_class_profile.get('pitch_guidance', '')} — apply to difficulty, scaffolding, notation."
        )
    if _class_rating:
        base += f"\nRating: {_class_rating.get('guidance', '')}"
    return base

# ── JSON schemas for structured outputs ──────────────────────────────────────

_SCHEMA_RETRIEVAL = {
    "type": "object",
    "properties": {
        "questions": {"type": "array", "items": {"type": "string"}},
        "answers":   {"type": "array", "items": {"type": "string"}},
    },
    "required": ["questions", "answers"],
    "additionalProperties": False,
}

_SCHEMA_WORKED_EXAMPLE = {
    "type": "object",
    "properties": {
        "heading": {"type": "string"},
        "example": {"type": "string"},
        "notes":   {"type": "string"},
    },
    "required": ["heading", "example", "notes"],
    "additionalProperties": False,
}

_SCHEMA_WE_DO = {
    "type": "object",
    "properties": {
        "heading": {"type": "string"},
        "problem": {"type": "string"},
        "steps":   {"type": "array", "items": {"type": "string"}},
        "answer":  {"type": "string"},
    },
    "required": ["heading", "problem", "steps", "answer"],
    "additionalProperties": False,
}

_SCHEMA_PRACTICE = {
    "type": "object",
    "properties": {
        "questions": {"type": "array", "items": {"type": "string"}},
        "answers":   {"type": "array", "items": {"type": "string"}},
    },
    "required": ["questions", "answers"],
    "additionalProperties": False,
}

_SCHEMA_WSWT = {
    "type": "object",
    "properties": {
        "pair_a": {"type": "string"},
        "pair_b": {"type": "string"},
    },
    "required": ["pair_a", "pair_b"],
    "additionalProperties": False,
}

_SCHEMA_TEACHING_SEQ = {
    "type": "object",
    "properties": {
        "i_do": {
            "type": "object",
            "properties": {
                "heading":        {"type": "string"},
                "worked_example": {"type": "string"},
                "notes":          {"type": "string"},
            },
            "required": ["heading", "worked_example", "notes"],
            "additionalProperties": False,
        },
        "we_do": {
            "type": "object",
            "properties": {
                "heading":  {"type": "string"},
                "question": {"type": "string"},
                "steps":    {"type": "array", "items": {"type": "string"}},
                "answer":   {"type": "string"},
            },
            "required": ["heading", "question", "steps", "answer"],
            "additionalProperties": False,
        },
        "you_do": {
            "type": "object",
            "properties": {
                "heading":  {"type": "string"},
                "question": {"type": "string"},
                "answer":   {"type": "string"},
            },
            "required": ["heading", "question", "answer"],
            "additionalProperties": False,
        },
    },
    "required": ["i_do", "we_do", "you_do"],
    "additionalProperties": False,
}

_SCHEMA_MINI_WB = {
    "type": "object",
    "properties": {
        "questions": {"type": "array", "items": {"type": "string"}},
        "answers":   {"type": "array", "items": {"type": "string"}},
    },
    "required": ["questions", "answers"],
    "additionalProperties": False,
}

_SCHEMA_INDEP_PRACTICE = {
    "type": "object",
    "properties": {
        "questions": {"type": "array", "items": {"type": "string"}},
        "answers":   {"type": "array", "items": {"type": "string"}},
    },
    "required": ["questions", "answers"],
    "additionalProperties": False,
}

_SCHEMA_PLENARY = {
    "type": "object",
    "properties": {
        "summary":  {"type": "string"},
        "question": {"type": "string"},
        "answer":   {"type": "string"},
    },
    "required": ["summary", "question", "answer"],
    "additionalProperties": False,
}


def set_demo_mode(value: bool) -> None:
    global _demo_mode
    _demo_mode = value


def _call(prompt: str, max_tokens: int = 800,
          model: str = "claude-sonnet-4-6") -> str:
    """Non-interactive call to the local claude CLI."""
    full_prompt = f"{_build_system_prompt()}\n\n{prompt}"
    proc = subprocess.run(
        ["claude", "--print", "--model", model, "--output-format", "json"],
        input=full_prompt,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {(proc.stderr or proc.stdout).strip()}")
    data = json.loads(proc.stdout)
    return data.get("result", "").strip()


def _call_json(prompt: str, schema: dict = None, max_tokens: int = 1500,
               model: str = "claude-opus-4-8") -> dict:
    """Call the local claude CLI and parse a JSON response."""
    json_instruction = "\n\nReturn ONLY valid JSON — no markdown fences, no explanation."
    if schema:
        json_instruction += f"\nSchema: {json.dumps(schema)}"
    text = _call(prompt + json_instruction, max_tokens=max_tokens, model=model)
    # Strip accidental code fences
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.split("```")[0].strip()
    return json.loads(text)


# ── Stub helpers (no API) ────────────────────────────────────────────────────

def _stub_retrieval(prior_knowledge: list) -> dict:
    qs = (prior_knowledge[:4] + ["Recall a key fact from this topic"] * 4)[:4]
    return {
        "questions": [f"What do you know about: {q}?" for q in qs],
        "answers":   ["[Answer to be added]"] * 4,
    }


def _stub_hook(objective: str) -> str:
    return (
        f"Think about where you encounter {objective.lower()} in everyday life. "
        "From shopping and cooking to architecture and sport, this skill appears "
        "more often than you might expect. By the end of this lesson you will be "
        "able to apply it confidently in a range of real-world situations."
    )


def _stub_worked_example(objective: str, methods_text: str) -> dict:
    heading = objective[:60] if len(objective) > 60 else objective
    example = methods_text[:600].strip() if methods_text else (
        f"Example: [Specific numerical problem involving {objective[:50]}]\n\n"
        f"Step 1: [Identify what you're given] → write down the known values\n"
        f"        [Why: organising information prevents errors]\n\n"
        f"Step 2: [Choose and apply the method] → show every line of working\n"
        f"        [Why: each line follows from the last — no jumps]\n\n"
        f"Step 3: [Complete the calculation] → state the answer with units\n"
        f"        [Why: units confirm you've answered the right question]\n\n"
        f"Step 4: [Check] → does this answer make sense in context?\n\n"
        f"In general: [state the generalised method in one line]\n\n"
        f"[Full example with real numbers will be generated with API key]"
    )
    return {
        "heading": heading,
        "example": example,
        "notes": (
            "Teacher note: annotate WHY each step is taken, not just what. "
            "Pause after Step 2 — this is where most errors occur."
        ),
    }


def _stub_practice(objective: str) -> dict:
    short = objective[:45]
    return {
        "questions": [
            f"[{short}] — simplest case (integer values, single step)",
            f"[{short}] — same method, one feature varied (e.g. decimal or negative value)",
            f"[{short}] — same method, second feature varied (e.g. fraction or reversed)",
            "Context problem: single step — interpret a real-world scenario",
            "Context problem: multi-step or embedded decision required",
            "Is this working correct? Explain your reasoning. [Show incorrect working]",
            "Non-routine: decide your own method — no obvious starting point given",
            "Generalise or find all solutions: write a rule or prove a statement",
        ],
        "answers": ["[Answer]"] * 8,
    }


def _stub_we_do(objective: str) -> dict:
    return {
        "heading": f"We Do — {objective[:45]}",
        "problem": (
            f"[Near-variation of the I Do example — same method, different values]\n\n"
            f"A problem: {objective[:60]}\n\n"
            "[Full problem with specific numbers will be generated with API key]"
        ),
        "steps": [
            "Step 1: What are we finding? Underline the key information in the question.",
            "Step 2: What method do we use? Write the formula / rule before substituting.",
            "Step 3: Substitute and calculate — show every line of working.",
            "Step 4: Does the answer make sense? Check with an estimate or reverse operation.",
        ],
        "answer": (
            f"[Full step-by-step solution for: {objective[:55]}]\n\n"
            "Step 1: → [values identified]\n"
            "Step 2: → [method/formula written out]\n"
            "Step 3: → [calculation shown line by line]\n"
            "Step 4: → [answer stated with units; check shown]\n\n"
            "[Will be generated with API key]"
        ),
    }


def _stub_reasoning(objective: str, task_type: str) -> str:
    if task_type == "asn":
        short = objective[:55]
        return (
            f"Always, Sometimes or Never? Justify each answer.\n\n"
            f"A) When you apply '{short}', the result is always greater than the original value.\n"
            f"   [ALWAYS / SOMETIMES / NEVER] — because...\n\n"
            f"B) You can use this method when the starting value is negative.\n"
            f"   [ALWAYS / SOMETIMES / NEVER] — because...\n\n"
            f"C) Two different starting values always give two different results.\n"
            f"   [ALWAYS / SOMETIMES / NEVER] — because...\n\n"
            f"D) The method still works if you change the order of the steps.\n"
            f"   [ALWAYS / SOMETIMES / NEVER] — because...\n\n"
            f"Think about: what happens when the value is 0, negative, or a fraction?\n\n"
            f"[Real statements tailored to this objective will be generated with API key]"
        )
    return (
        f"Problem Solving Task\n\n"
        f"[A multi-step problem requiring you to apply: {objective[:55]}]\n\n"
        f"You will need to:\n"
        f"  1. Decide on a strategy — the method is not given to you\n"
        f"  2. Apply your knowledge to a non-routine situation\n"
        f"  3. Show all working and justify your final answer\n\n"
        f"[Full problem with specific scenario will be generated with API key]"
    )


def _stub_wswt(objective: str) -> dict:
    short = objective[:55]
    return {
        "pair_a": (
            f"Example A: [{short}]\n\n"
            f"[Specific numerical example — simple case]\n\n"
            f"Step 1: → ...\n"
            f"Step 2: → ...\n"
            f"Answer: ..."
        ),
        "pair_b": (
            f"Example B: [{short}]\n\n"
            f"[Same method — ONE feature deliberately changed]\n\n"
            f"Step 1: → ...\n"
            f"Step 2: → ...\n"
            f"Answer: ...\n\n"
            f"What changed? What stayed the same? Why does it matter?\n\n"
            f"[Real paired examples will be generated with API key]"
        ),
    }


def _stub_teaching_seq(objective: str, methods_text: str) -> dict:
    short = objective[:55]
    example_base = (
        f"[DEMO — real example generated with API]\n\n"
        f"Following the Common Method shown on the left:\n\n"
        f"Step 1: [identify given values]  →  e.g. value = ?\n"
        f"        [Why: organising information prevents errors]\n\n"
        f"Step 2: [write the method/rule before substituting]\n"
        f"        [Why: always write before substituting]\n\n"
        f"Step 3: [apply the method — show every line of working]\n"
        f"        [Why: each line follows from the last — no jumps]\n\n"
        f"Step 4: [state the answer with units and check]\n"
        f"        [Why: units confirm you've answered the right question]\n\n"
        f"In general: [method stated in one sentence]\n\n"
        f"Objective: {short}"
    )
    return {
        "i_do": {
            "heading": f"I Do — {short[:50]}",
            "worked_example": example_base,
            "notes": (
                "Teacher note: annotate WHY each step is taken. "
                "Pause after Step 2 — most errors occur here."
            ),
        },
        "we_do": {
            "heading": f"We Do — {short[:50]}",
            "question": (
                f"[Near-variation of I Do — same method, different numbers]\n\n"
                f"Problem: {short}\n\n"
                "[Full problem with specific numbers generated with API key]"
            ),
            "steps": [
                "Step 1: What are we finding? Identify the key information.",
                "Step 2: Write the method/rule before substituting.",
                "Step 3: Substitute and calculate — show every line.",
                "Step 4: Does the answer make sense? Check your working.",
            ],
            "answer": (
                "Step 1: → [values identified]\n"
                "Step 2: → [method written out]\n"
                "Step 3: → [calculation shown line by line]\n"
                "Step 4: → [answer with check]\n\n"
                "[Will be generated with API key]"
            ),
        },
        "you_do": {
            "heading": f"You Do — {short[:50]}",
            "question": (
                f"[Further variation — same method, new numbers]\n\n"
                f"Problem: {short}\n\n"
                "[Full problem generated with API key]"
            ),
            "answer": "[Answer generated with API key]",
        },
    }


def _stub_mini_wb(objective: str) -> dict:
    short = objective[:45]
    return {
        "questions": [
            f"[{short}]  Simple case — integer values",
            f"[{short}]  Same method — one value changes",
            f"[{short}]  Same structure — decimal input",
            f"[{short}]  Same structure — negative value",
            f"[{short}]  Same structure — fraction involved",
            f"[{short}]  Two-step variation",
            f"[{short}]  Given the answer, find the input",
            f"[{short}]  Which is correct? A or B — justify",
            f"[{short}]  Word context — identify the calculation",
            f"[{short}]  Hardest variation — non-routine value",
        ],
        "answers": [f"[Answer {i + 1}]" for i in range(10)],
    }


def _stub_indep_practice(objective: str) -> dict:
    short = objective[:45]
    return {
        "questions": [
            f"[{short}] — simplest case (integer, 1 step)",
            f"[{short}] — vary one feature (decimal or reversed)",
            f"[{short}] — vary second feature (fraction or negative)",
            f"[{short}] — vary third feature (one extra step)",
            f"[{short}] — vary fourth feature (different form)",
            f"Context: single-step real-world scenario",
            f"Context: multi-step or embedded decision",
            f"Is this working correct? Explain your reasoning.",
            f"Non-routine: decide your own method — no starting point given",
            f"Generalise: write a rule or find all possible solutions",
        ],
        "answers": [f"[Answer {i + 1}]" for i in range(10)],
    }


def _stub_plenary(objective: str) -> dict:
    short = objective[:60]
    return {
        "summary": (
            f"In this lesson we have learned to: {short}.\n\n"
            "We practised using worked examples, class tasks and independent questions, "
            "building confidence through carefully varied problems."
        ),
        "question": f"[Final check question for: {short}]\n[Real question generated with API key]",
        "answer":   "[Answer generated with API key]",
    }


# ── Public API ────────────────────────────────────────────────────────────────

def generate_retrieval_questions(prior_knowledge: list,
                                 objective: str,
                                 topic: str,
                                 vocabulary: list = None) -> dict:
    if _demo_mode:
        return _stub_retrieval(prior_knowledge)

    pk = "; ".join(prior_knowledge[:5])
    vocab_str = (f"\nVocabulary: {', '.join(vocabulary[:6])}" if vocabulary else "")

    prompt = (
        f"Topic: {topic}\nObjective: {objective}\nPrior knowledge: {pk}{vocab_str}\n\n"
        "Write 4 retrieval starter questions testing prior knowledge. "
        "Mix recall, short calculation, and application. All maths correct with specific numbers.\n"
        "JSON: {\"questions\": [4 strings], \"answers\": [4 strings]}"
    )
    return _call_json(prompt, max_tokens=600, model="claude-haiku-4-5-20251001")


def generate_hook(objective: str, topic: str,
                  personal_development: list) -> str:
    if _demo_mode:
        return _stub_hook(objective)

    pd = "\n".join(f"- {p}" for p in personal_development[:4])
    prompt = (
        f"Maths topic: {topic}\nObjective: {objective}\n\n"
        f"Real-world connections from the school's SoW:\n{pd}\n\n"
        "Write a short, engaging real-world hook (4–6 sentences) that motivates WHY "
        "students need this objective. Use a relatable context (shopping, sport, social media, etc.). "
        "Be genuine — avoid clichés. No bullet points; write as flowing text."
    )
    return _call(prompt, max_tokens=400, model="claude-sonnet-4-6")


def generate_worked_example(objective: str, topic: str,
                             methods_text: str = "",
                             vocabulary: list = None,
                             misconceptions: list = None) -> dict:
    if _demo_mode:
        return _stub_worked_example(objective, methods_text)

    extra = (f"\n\nTeaching method from the school's Common Methods document:\n{methods_text[:800]}"
             if methods_text else "")
    vocab_str = (f"\n\nKey vocabulary: {', '.join(vocabulary[:8])}"
                 if vocabulary else "")
    misconc_str = (f"\n\nCommon misconception to address: {misconceptions[0]}"
                   if misconceptions else "")

    prompt = (
        f"Topic: {topic}\nObjective: {objective}{extra}{vocab_str}{misconc_str}\n\n"
        "Write ONE complete I Do (teacher demonstration) worked example.\n\n"
        "REQUIREMENTS:\n"
        "- Use a SPECIFIC numerical example with real numbers "
        "(e.g. 'Find 35% of 240', not 'Find X% of Y')\n"
        "- Show EVERY line of working; after each step add [why this step is taken] in brackets\n"
        "- End with one line starting 'In general:' that states the generalised method\n"
        "- Middle difficulty — accessible but not trivial\n"
        "- Verify all arithmetic before writing it\n\n"
        "Return JSON with keys: heading (5–8 words), example (full annotated working), "
        "notes (1–2 sentences on what to emphasise and the most common error here)."
    )
    return _call_json(prompt, _SCHEMA_WORKED_EXAMPLE, max_tokens=1200, model="claude-opus-4-8")


def generate_we_do(objective: str, topic: str,
                   methods_text: str = "",
                   vocabulary: list = None) -> dict:
    if _demo_mode:
        return _stub_we_do(objective)

    extra = (
        f"\n\nMANDATORY METHOD — use this exact approach from the school's Common Methods doc:\n\n"
        f"{methods_text}"
        if methods_text else ""
    )
    vocab_str = (f"\n\nKey vocabulary: {', '.join(vocabulary[:6])}"
                 if vocabulary else "")

    prompt = (
        f"Topic: {topic}\nObjective: {objective}{extra}{vocab_str}\n\n"
        "Write a 'We Do' guided practice problem for the class to work TOGETHER "
        "immediately after the I Do demonstration.\n\n"
        "REQUIREMENTS:\n"
        "- Same method and same number of steps as I Do — only the specific numbers change "
        "(near-variation, not a different problem type)\n"
        "- Problem statement must include specific numerical values (not abstract)\n"
        "- 4 scaffold steps must be method-specific prompts for THIS objective "
        "(e.g. 'Write the multiplier as a decimal: 1 + ...') — no answers in steps\n"
        "- Answer must show every line of working with the final answer clearly stated\n"
        "- Verify all arithmetic\n\n"
        "Return JSON with keys: heading (4–6 words), problem (specific problem with numbers), "
        "steps (array of 4 method-specific prompt strings), "
        "answer (full worked solution with every step)."
    )
    return _call_json(prompt, _SCHEMA_WE_DO, max_tokens=1000, model="claude-opus-4-8")


def generate_practice_questions(objective: str, topic: str,
                                 vocabulary: list = None,
                                 misconceptions: list = None) -> dict:
    if _demo_mode:
        return _stub_practice(objective)

    vocab_str = (f"\n\nKey vocabulary: {', '.join(vocabulary[:8])}"
                 if vocabulary else "")
    misconc_str = (f"\n\nCommon misconception: {misconceptions[0]}"
                   if misconceptions else "")

    prompt = (
        f"Topic: {topic}\nObjective: {objective}{vocab_str}{misconc_str}\n\n"
        "Write exactly 8 practice questions using VARIATION THEORY and the "
        "Fluency → Reasoning → Problem Solving model.\n\n"
        "FLUENCY (questions a, b, c — vary ONE element at a time):\n"
        "  a) Simplest case: integer values, single step, no context\n"
        "  b) Same structure — vary exactly ONE feature "
        "(e.g. use a decimal, change a sign, reverse the operation)\n"
        "  c) Same structure — vary ONE more feature "
        "(e.g. fraction, extra step, different form)\n"
        "  Students must be able to see WHAT CHANGES and WHAT STAYS THE SAME across a–c.\n\n"
        "REASONING (questions d, e, f):\n"
        "  d) Single-step context problem — student identifies what to calculate\n"
        "  e) Multi-step context — two or more calculations, or embedded decision\n"
        "  f) Comparison or justification: 'Which is greater/better value?' "
        "OR 'Is this working correct? Explain.'\n\n"
        "PROBLEM SOLVING (questions g, h):\n"
        "  g) Non-routine — approach not immediately obvious; student decides method\n"
        "  h) Generalise or find all solutions / multiple valid approaches\n\n"
        "Each question must fit on one line. All maths MUST be correct with specific numbers.\n\n"
        "Return JSON with keys: questions (array of 8 strings a–h), "
        "answers (array of 8 strings a–h)."
    )
    return _call_json(prompt, _SCHEMA_PRACTICE, max_tokens=1800, model="claude-opus-4-8")


def generate_reasoning_task(objective: str, topic: str,
                             task_type: str = "asn") -> str:
    if _demo_mode:
        return _stub_reasoning(objective, task_type)

    if task_type == "asn":
        prompt = (
            f"Topic: {topic}\nObjective: {objective}\n\n"
            "Write an 'Always, Sometimes or Never?' task with exactly 4 statements.\n\n"
            "Rules for high-quality ASN statements:\n"
            "- At least one ALWAYS true (a genuine mathematical truth)\n"
            "- At least one SOMETIMES true — non-obvious condition separates true and false cases "
            "(avoid trivial conditions like 'when the number is positive')\n"
            "- At least one NEVER true — based on a genuine misconception students hold\n"
            "- Every statement must be ambiguous on first reading\n"
            "- Statements must be complete mathematical claims, not vague generalisations\n\n"
            "After the 4 statements, add one line: 'Think about what happens when...' — "
            "give a hint that unlocks the hardest statement without revealing the answer.\n\n"
            "Plain text only. All maths must be correct."
        )
    elif task_type == "open":
        prompt = (
            f"Topic: {topic}\nObjective: {objective}\n\n"
            "Write a Problem Solving task requiring students to apply this objective.\n\n"
            "Requirements:\n"
            "- Multi-step: students decide the strategy, method not given\n"
            "- Specific numerical scenario with all necessary information provided\n"
            "- Students must show working AND justify their answer (not just calculate)\n"
            "- Solvable in 5–10 minutes with correct working\n"
            "- Do NOT write 'Explain how you would...' — write a genuine problem with a "
            "definite answer\n\n"
            "Plain text only. All maths must be correct."
        )
    else:
        prompt = (
            f"Topic: {topic}\nObjective: {objective}\n\n"
            "Write a reasoning task that deepens understanding of this objective. "
            "Keep it concise (suitable for one slide). All maths must be correct. "
            "Plain text only."
        )

    return _call(prompt, max_tokens=600, model="claude-sonnet-4-6")


def generate_wswt_pair(objective: str, topic: str,
                       vocabulary: list = None) -> dict:
    if _demo_mode:
        return _stub_wswt(objective)

    vocab_str = (f"\n\nKey vocabulary: {', '.join(vocabulary[:6])}"
                 if vocabulary else "")

    prompt = (
        f"Topic: {topic}\nObjective: {objective}{vocab_str}\n\n"
        "Create a 'What's the Same? What's Different?' task using deliberate variation.\n\n"
        "Requirements:\n"
        "- Both examples use the same mathematical method / structure\n"
        "- Exactly ONE key feature differs — a mathematically significant change "
        "(e.g. sign change, integer vs fraction, factored vs expanded, one extra step)\n"
        "- The difference must reveal something important about the maths\n"
        "- Show full step-by-step working for both examples\n"
        "- Start pair_b with a 'Note:' line naming the variation "
        "(e.g. 'Note: in this example the value is negative.')\n"
        "- End pair_b with: 'What changed? What stayed the same? Why does it matter?'\n\n"
        "All maths correct. Plain text notation.\n\n"
        "Return JSON with keys: pair_a (first example with full working), "
        "pair_b (second example with variation note, full working, and prompt question)."
    )
    return _call_json(prompt, _SCHEMA_WSWT, max_tokens=800, model="claude-sonnet-4-6")


def select_diagram_type(objective: str):
    """
    Decide which diagram type best illustrates this objective.
    Returns: 'bar_model' | 'number_line' | 'area_grid' | 'percentage_bar' | 'angle' | None
    """
    obj_lower = objective.lower()
    if any(w in obj_lower for w in ["percent", "fraction", "ratio", "proportion"]):
        return "percentage_bar"
    if any(w in obj_lower for w in ["inequalit", "number line", "integer"]):
        return "number_line"
    if any(w in obj_lower for w in ["expand", "bracket", "multiply", "grid", "factoris"]):
        return "area_grid"
    if any(w in obj_lower for w in ["angle", "parallel", "polygon", "triangle"]):
        return "angle"
    if any(w in obj_lower for w in ["bar", "segment", "share", "collect", "like term"]):
        return "bar_model"
    return None


# ── New structured sequence generators ───────────────────────────────────────

def generate_teaching_sequence(objective: str, topic: str,
                                methods_text: str = "",
                                vocabulary: list = None,
                                misconceptions: list = None) -> dict:
    """Generate I Do / We Do / You Do for one objective in one API call."""
    if _demo_mode:
        return _stub_teaching_seq(objective, methods_text)

    extra = (
        f"\n\nMandatory method (Common Methods doc) — use this exact approach, not an equivalent:\n{methods_text}"
        if methods_text else ""
    )
    vocab_str = (f"\nVocabulary: {', '.join(vocabulary[:6])}" if vocabulary else "")
    misconc_str = (f"\nMisconception to address: {misconceptions[0]}" if misconceptions else "")

    prompt = (
        f"Topic: {topic}\nObjective: {objective}{extra}{vocab_str}{misconc_str}\n\n"
        "Write I Do / We Do / You Do slides using near-variation (same method, one feature changes each time).\n\n"
        "I DO: one specific numbered worked example; every working line shown; "
        "[why] after each step; end 'In general: ...'; "
        "heading 5–8 words; notes 1–2 sentences on emphasis and common error.\n\n"
        "WE DO: near-variation (same method, new numbers); heading 4–6 words; "
        "question with specific numbers; steps: 4 method-specific scaffold prompts (no answers); "
        "answer: full worked solution.\n\n"
        "YOU DO: another near-variation; heading 4–6 words; question; answer with working.\n\n"
        "All maths correct. "
        "JSON: {\"i_do\": {\"heading\": str, \"worked_example\": str, \"notes\": str}, "
        "\"we_do\": {\"heading\": str, \"question\": str, \"steps\": [4 strings], \"answer\": str}, "
        "\"you_do\": {\"heading\": str, \"question\": str, \"answer\": str}}"
    )
    return _call_json(prompt, max_tokens=2000, model="claude-opus-4-8")


def generate_mini_whiteboard_questions(objective: str, topic: str,
                                        methods_text: str = "") -> dict:
    """Generate 10 mini whiteboard questions — subtly varied, one per slide."""
    if _demo_mode:
        return _stub_mini_wb(objective)

    extra = (f"\nMethod: {methods_text}" if methods_text else "")

    prompt = (
        f"Topic: {topic}\nObjective: {objective}{extra}\n\n"
        "Write 10 mini whiteboard questions using variation theory (one feature change per question). "
        "Q1–4: fluency (increasing complexity). Q5–7: reasoning (context, reverse, comparison). "
        "Q8–10: problem solving. Each fits on one line. All maths correct with specific numbers.\n"
        "JSON: {\"questions\": [10 strings], \"answers\": [10 strings]}"
    )
    return _call_json(prompt, max_tokens=1000, model="claude-haiku-4-5-20251001")


def generate_independent_practice(objective: str, topic: str,
                                   vocabulary: list = None,
                                   methods_text: str = "") -> dict:
    """Generate 10 independent practice questions — incremental, consistent style."""
    if _demo_mode:
        return _stub_indep_practice(objective)

    vocab_str = (f"\nVocabulary: {', '.join(vocabulary[:6])}" if vocabulary else "")
    extra = (f"\nMethod: {methods_text}" if methods_text else "")

    prompt = (
        f"Topic: {topic}\nObjective: {objective}{vocab_str}{extra}\n\n"
        "Write 10 independent practice questions using variation theory (one change per question):\n"
        "1. Simplest (integer, 1-step)  2. decimal  3. negative  4. fraction/reversed  5. +1 step\n"
        "6. Real-world single-step  7. Multi-step context  8. Comparison/justification\n"
        "9. Non-routine (student decides method)  10. Generalise/find all solutions\n"
        "Style matches I Do/We Do/You Do. All maths correct. Each fits on one line.\n"
        "JSON: {\"questions\": [10 strings], \"answers\": [10 strings]}"
    )
    return _call_json(prompt, max_tokens=1200, model="claude-haiku-4-5-20251001")


def generate_plenary(objective: str, topic: str) -> dict:
    """Generate plenary summary and final mini whiteboard check question."""
    if _demo_mode:
        return _stub_plenary(objective)

    prompt = (
        f"Topic: {topic}\nObjective: {objective}\n\n"
        "Write a plenary: summary (2–3 sentences past tense, names key method, connects to next lesson); "
        "question (one final mini-whiteboard check with specific numbers, short); "
        "answer (correct answer with brief working).\n"
        "All maths correct. JSON: {\"summary\": str, \"question\": str, \"answer\": str}"
    )
    return _call_json(prompt, max_tokens=400, model="claude-haiku-4-5-20251001")
