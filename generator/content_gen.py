"""Generate lesson content via Claude API, with stub fallback when no key is set."""

import json
import os
import re

_client = None
_demo_mode = not bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def _get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def _call(prompt: str, max_tokens: int = 1200) -> str:
    client = _get_client()
    import anthropic
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


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
        f"Step 1: Read the problem carefully.\n"
        f"Step 2: Identify what you are being asked to find.\n"
        f"Step 3: Apply the method for {objective}.\n"
        f"Step 4: Check your answer makes sense.\n\n"
        f"[Full worked example will be generated with API key]"
    )
    return {
        "heading": heading,
        "example": example,
        "notes": "Teacher note: model each step before students attempt independently.",
    }


def _stub_practice(objective: str) -> dict:
    labels = ["a", "b", "c", "d", "e", "f", "g", "h"]
    descs = [
        "straightforward calculation",
        "straightforward calculation",
        "straightforward calculation",
        "applied / worded problem",
        "applied / worded problem",
        "applied / worded problem",
        "problem-solving extension",
        "reasoning extension",
    ]
    return {
        "questions": [f"({l}) [{objective[:40]}] — {d}" for l, d in zip(labels, descs)],
        "answers":   ["[Answer]"] * 8,
    }


def _stub_reasoning(objective: str, task_type: str) -> str:
    if task_type == "asn":
        return (
            f"Always, Sometimes or Never?\n\n"
            f"A) '{objective}' always gives a whole number answer.\n"
            f"B) You can apply this method without knowing prior steps.\n"
            f"C) The answer is always positive.\n\n"
            f"Justify your answer with an example or counter-example."
        )
    return (
        f"Explain how you would approach the following problem related to: {objective}.\n\n"
        f"Show all your working and justify each step.\n\n"
        f"[Full reasoning task will be generated with API key]"
    )


def _stub_wswt(objective: str) -> dict:
    return {
        "pair_a": f"Example A: A straightforward application of\n{objective}.\n\nWorking shown step by step.",
        "pair_b": f"Example B: A variation of the same method where one condition changes.\n\nWorking shown step by step.",
    }


# ── Public API ────────────────────────────────────────────────────────────────

def generate_retrieval_questions(prior_knowledge: list,
                                 objective: str,
                                 topic: str) -> dict:
    if _demo_mode:
        return _stub_retrieval(prior_knowledge)

    pk = "\n".join(f"- {p}" for p in prior_knowledge[:6])
    prompt = f"""You are an experienced UK secondary maths teacher for Outwood Grange Academies Trust.

Topic being taught next: {topic} — Objective: {objective}

Prior knowledge students should have:
{pk}

Generate exactly 4 retrieval starter questions that test this prior knowledge.
Questions should be concise, appropriate for a warm-up (answerable in 1-2 minutes each).
Include a mix of recall, application, and short calculation questions.
All maths must be correct. Verify every numerical answer.

Respond ONLY with valid JSON in this exact format:
{{"questions": ["q1", "q2", "q3", "q4"], "answers": ["a1", "a2", "a3", "a4"]}}"""

    text = _call(prompt)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return _stub_retrieval(prior_knowledge)


def generate_hook(objective: str, topic: str,
                  personal_development: list) -> str:
    if _demo_mode:
        return _stub_hook(objective)

    pd = "\n".join(f"- {p}" for p in personal_development[:4])
    prompt = f"""You are an experienced UK secondary maths teacher.

Maths topic: {topic}
Objective: {objective}

Real-world connections suggested by the school:
{pd}

Write a short, engaging real-world hook scenario (4-6 sentences) that motivates WHY students
need to learn this objective. Use a relatable context (shopping, sport, social media, etc.).
Make it feel genuine. Do not use bullet points — write it as flowing text."""
    return _call(prompt, max_tokens=400)


def generate_worked_example(objective: str, topic: str,
                             methods_text: str = "") -> dict:
    if _demo_mode:
        return _stub_worked_example(objective, methods_text)

    extra = f"\n\nPedagogical guidance from the school's Common Methods document:\n{methods_text[:800]}" \
            if methods_text else ""
    prompt = f"""You are an experienced UK secondary maths teacher for Outwood Grange Academies Trust.

Topic: {topic}
Objective: {objective}{extra}

Write ONE clear worked example that teaches this objective.
Use clear step-by-step working. Include the numerical/visual approach first, then the generalised method.
Use standard GCSE notation. All maths must be correct — verify every step.
Do not use LaTeX — use plain text notation (e.g. x^2, sqrt(x), 3/4).

Respond ONLY with valid JSON:
{{"heading": "short heading (5-8 words)", "example": "full worked example text", "notes": "brief teaching note for teacher (1-2 sentences)"}}"""
    text = _call(prompt, max_tokens=800)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return _stub_worked_example(objective, methods_text)


def generate_practice_questions(objective: str, topic: str,
                                level: str = "mixed") -> dict:
    if _demo_mode:
        return _stub_practice(objective)

    prompt = f"""You are an experienced UK secondary maths teacher for Outwood Grange Academies Trust.

Topic: {topic}
Objective: {objective}
Question level: {level} (a-c = straightforward, d-f = applied/worded, g-h = extension)

Write exactly 8 practice questions for this objective, in ascending difficulty.
Questions a-c: direct skill practice (numerical only)
Questions d-f: applied / worded problems
Questions g-h: problem solving / reasoning extension

All maths MUST be correct. Calculate and verify every answer before writing it.
Use plain text notation (^2 for squared, sqrt() for roots, fractions as a/b).

Respond ONLY with valid JSON:
{{"questions": ["q_a", "q_b", "q_c", "q_d", "q_e", "q_f", "q_g", "q_h"],
  "answers":   ["a_a", "a_b", "a_c", "a_d", "a_e", "a_f", "a_g", "a_h"]}}"""
    text = _call(prompt, max_tokens=1000)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return _stub_practice(objective)


def generate_reasoning_task(objective: str, topic: str,
                            task_type: str = "asn") -> str:
    if _demo_mode:
        return _stub_reasoning(objective, task_type)

    descriptions = {
        "asn":  "an 'Always, Sometimes or Never' true statement about this objective (write 3-4 statements for students to classify)",
        "wswt": "a 'What's the same, what's different?' comparison task using two related examples",
        "open": "an open-ended mathematical reasoning problem",
    }
    prompt = f"""You are an experienced UK secondary maths teacher.

Topic: {topic}
Objective: {objective}

Write {descriptions.get(task_type, 'a reasoning task')} that deepens understanding of this objective.
Keep it concise (suitable for one slide). All maths must be correct.
Write plain text only — no bullet points, no LaTeX."""
    return _call(prompt, max_tokens=400)


def generate_wswt_pair(objective: str, topic: str) -> dict:
    if _demo_mode:
        return _stub_wswt(objective)

    prompt = f"""You are an experienced UK secondary maths teacher.

Topic: {topic}
Objective: {objective}

Create a 'What's the Same? What's Different?' task:
Two related worked examples or expressions that look similar but differ in an important way.
Students compare them and identify similarities and differences.
All maths must be correct. Use plain text notation.

Respond ONLY with valid JSON:
{{"pair_a": "first example with working", "pair_b": "second example with working"}}"""
    text = _call(prompt, max_tokens=500)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return _stub_wswt(objective)


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
