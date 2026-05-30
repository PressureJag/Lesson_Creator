"""Generate lesson content via Claude API, with stub fallback when no key is set."""

import json
import os

_client = None
_demo_mode = not bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())

# ── Shared system prompt (cached via cache_control) ───────────────────────────

_SYSTEM_PROMPT = (
    "You are an experienced UK secondary maths teacher for Outwood Grange Academies Trust.\n"
    "You write maths lesson content for secondary school students in England (ages 11–16).\n\n"
    "Rules you always follow:\n"
    "- ALL maths must be correct — verify every calculation before writing it\n"
    "- Use plain-text notation: x^2, sqrt(x), fractions as a/b, × for multiply\n"
    "- Apply variation theory: vary ONE feature at a time across question sets\n"
    "- Fluency → Reasoning → Problem Solving arc in practice questions\n"
    "- Write for the specific objective given — never write generic filler content\n"
    "- Worked examples must use REAL specific numbers, not placeholders like 'X' or 'a value'\n"
)

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


def set_demo_mode(value: bool) -> None:
    global _demo_mode
    _demo_mode = value


def _get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def _call(prompt: str, max_tokens: int = 800,
          model: str = "claude-sonnet-4-6") -> str:
    """Plain-text API call with cached system prompt."""
    client = _get_client()
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[{
            "type": "text",
            "text": _SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def _call_json(prompt: str, schema: dict, max_tokens: int = 1500,
               model: str = "claude-opus-4-8") -> dict:
    """JSON API call using structured outputs — guarantees valid JSON matching schema."""
    client = _get_client()
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[{
            "type": "text",
            "text": _SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(msg.content[0].text)


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


# ── Public API ────────────────────────────────────────────────────────────────

def generate_retrieval_questions(prior_knowledge: list,
                                 objective: str,
                                 topic: str,
                                 vocabulary: list = None) -> dict:
    if _demo_mode:
        return _stub_retrieval(prior_knowledge)

    pk = "\n".join(f"- {p}" for p in prior_knowledge[:6])
    vocab_str = ""
    if vocabulary:
        vocab_str = f"\n\nKey vocabulary for this topic: {', '.join(vocabulary[:8])}"

    prompt = (
        f"Topic: {topic}\nObjective being taught next: {objective}\n\n"
        f"Prior knowledge students should have:\n{pk}{vocab_str}\n\n"
        "Write exactly 4 retrieval starter questions that test this prior knowledge.\n"
        "Each question must be answerable in 1–2 minutes (warm-up pace).\n"
        "Include a mix of recall, short calculation, and application. "
        "All maths must be correct with specific numbers, not variables.\n\n"
        "Return JSON with keys: questions (array of 4 strings), answers (array of 4 strings)."
    )
    return _call_json(prompt, _SCHEMA_RETRIEVAL, max_tokens=800, model="claude-sonnet-4-6")


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

    extra = (f"\n\nCommon Methods guidance:\n{methods_text[:600]}"
             if methods_text else "")
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
