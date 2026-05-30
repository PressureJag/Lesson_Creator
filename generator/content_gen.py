"""Generate lesson content via Claude API, with stub fallback when no key is set."""

import json
import os
import re

_client = None
_demo_mode = not bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def set_demo_mode(value: bool) -> None:
    global _demo_mode
    _demo_mode = value


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
            f"[Same method — ONE feature deliberately changed, e.g. sign / form / number of steps]\n\n"
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

    extra = f"\n\nTeaching method from the school's Common Methods document (follow this approach):\n{methods_text[:800]}" \
            if methods_text else ""
    prompt = f"""You are an experienced UK secondary maths teacher for Outwood Grange Academies Trust.

Topic: {topic}
Objective: {objective}{extra}

Write ONE complete worked example teaching this objective using the I Do model (teacher demonstration).

Requirements:
- Choose a concrete numerical example with specific, realistic values — not just variables or 'a number'
- Show EVERY line of working; after each step add a brief annotation in brackets explaining WHY that step is taken
- After the numerical example, write one line beginning "In general:" that states the generalised method
- Keep the example at middling difficulty — not trivial, but not examination-hard
- Plain text notation only: x^2, sqrt(x), fractions as a/b, × for multiply — no LaTeX

All maths MUST be correct. Verify every calculation before writing it.

Respond ONLY with valid JSON:
{{"heading": "short heading (5-8 words)", "example": "full annotated worked example", "notes": "1-2 sentences: what to emphasise when modelling AND the most common error students make here"}}"""
    text = _call(prompt, max_tokens=1000)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return _stub_worked_example(objective, methods_text)


def generate_we_do(objective: str, topic: str,
                   methods_text: str = "") -> dict:
    if _demo_mode:
        return _stub_we_do(objective)

    extra = (f"\n\nCommon Methods guidance:\n{methods_text[:600]}"
             if methods_text else "")
    prompt = f"""You are an experienced UK secondary maths teacher for Outwood Grange Academies Trust.

Topic: {topic}
Objective: {objective}{extra}

Write a 'We Do' guided practice problem for the class to work through TOGETHER immediately after the I Do demonstration.

Requirements:
- Use the same method and same number of steps as the I Do example — only the specific values should change (near-variation, not a different problem type)
- The problem statement must include specific numerical values — not abstract or symbolic
- The 4 scaffold steps must be method-specific prompts for THIS objective, not generic advice. Each step should name what to do (e.g. "Write the multiplier as a decimal: 1 + ...") without giving the answer
- The answer must show every line of working, with the final answer clearly stated

Respond ONLY with valid JSON:
{{
  "heading": "We Do — short descriptor (4-6 words)",
  "problem": "specific problem statement with numerical values (1-3 sentences)",
  "steps": [
    "Step 1: method-specific prompt for this objective (prompt only, not the answer)",
    "Step 2: ...",
    "Step 3: ...",
    "Step 4: ..."
  ],
  "answer": "full worked solution showing every step and the final answer with units"
}}

All maths must be correct. Verify every numerical answer. Plain text notation only (^2, sqrt(), fractions as a/b)."""
    text = _call(prompt, max_tokens=900)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return _stub_we_do(objective)


def generate_practice_questions(objective: str, topic: str,
                                level: str = "mixed") -> dict:
    if _demo_mode:
        return _stub_practice(objective)

    prompt = f"""You are an experienced UK secondary maths teacher for Outwood Grange Academies Trust.

Topic: {topic}
Objective: {objective}

Write exactly 8 practice questions using VARIATION THEORY and the Fluency → Reasoning → Problem Solving model.

FLUENCY — questions a, b, c (vary ONE element at a time to build conceptual understanding):
  a) The simplest case: integer values, single step, no context
  b) Same structure as a) — vary exactly ONE feature (e.g. use a decimal, change a sign, reverse the operation)
  c) Same structure as b) — vary ONE more feature (e.g. introduce a fraction, add a step, change the form)
  These three questions must form a deliberate progression — a student should notice what changes and what stays the same.

REASONING — questions d, e, f (require interpretation, not just calculation):
  d) Single-step context problem (shopping, measurement, sport, etc.) — students must identify what to calculate
  e) Multi-step context problem — requires two or more calculations, or an embedded decision
  f) Comparison or justification: "Which is greater / better value / more efficient?" OR "Is this answer correct? Explain."

PROBLEM SOLVING — questions g, h (non-routine — students must choose their own strategy):
  g) A problem where the approach is not immediately obvious; the method must be decided by the student
  h) A problem requiring generalisation, multiple valid approaches, OR finding all possible solutions

Each question must fit on one line (concise wording). All maths MUST be correct — calculate and verify every answer.
Plain text notation: ^2 for squared, sqrt() for roots, fractions as a/b.

Respond ONLY with valid JSON:
{{"questions": ["q_a", "q_b", "q_c", "q_d", "q_e", "q_f", "q_g", "q_h"],
  "answers":   ["a_a", "a_b", "a_c", "a_d", "a_e", "a_f", "a_g", "a_h"]}}"""
    text = _call(prompt, max_tokens=1500)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return _stub_practice(objective)


def generate_reasoning_task(objective: str, topic: str,
                            task_type: str = "asn") -> str:
    if _demo_mode:
        return _stub_reasoning(objective, task_type)

    if task_type == "asn":
        prompt = f"""You are an experienced UK secondary maths teacher.

Topic: {topic}
Objective: {objective}

Write an 'Always, Sometimes or Never?' task with exactly 4 statements about this objective.

Rules for high-quality ASN statements:
- At least one statement must be ALWAYS true (a general mathematical truth about this method)
- At least one must be SOMETIMES true — with a non-obvious condition that separates the true and false cases. Avoid trivial conditions like "when the number is positive"
- At least one must be NEVER true — based on a genuine misconception students commonly hold about this topic
- Every statement must be genuinely ambiguous on first reading — do not make any statement obviously true or false
- Statements should be complete mathematical claims (not vague generalisations)

After the 4 statements, add one line: "Think about what happens when..." — give a hint that unlocks the hardest statement, without revealing the answer.

Write plain text only — no bullet points, no LaTeX. All maths must be correct."""

    elif task_type == "open":
        prompt = f"""You are an experienced UK secondary maths teacher.

Topic: {topic}
Objective: {objective}

Write a Problem Solving task that requires students to apply: {objective}

Requirements:
- The problem must be multi-step: students need to decide on a strategy, not just follow a given procedure
- Include a specific numerical scenario with all necessary information provided
- The method to use should not be stated — students must recognise it from the context
- Students must show working AND justify their final answer (not just calculate)
- The problem should be solvable in 5–10 minutes with correct working
- Do NOT write "Explain how you would approach..." — write a genuine problem to solve

Write plain text only. No LaTeX. All maths must be correct and the problem must have a definite answer."""

    else:
        prompt = f"""You are an experienced UK secondary maths teacher.

Topic: {topic}
Objective: {objective}

Write a reasoning task that deepens understanding of this objective.
Keep it concise (suitable for one slide). All maths must be correct.
Write plain text only — no LaTeX."""

    return _call(prompt, max_tokens=600)


def generate_wswt_pair(objective: str, topic: str) -> dict:
    if _demo_mode:
        return _stub_wswt(objective)

    prompt = f"""You are an experienced UK secondary maths teacher.

Topic: {topic}
Objective: {objective}

Create a 'What's the Same? What's Different?' task using deliberate variation:

Requirements:
- Both examples must use the same mathematical method / structure
- Exactly ONE key feature must differ between them — this should be a mathematically significant change, not just different numbers (e.g. a sign change, integer vs fraction, factored vs expanded form, one extra step, a reversed operation)
- The difference must reveal something important about the mathematics — students should gain insight, not just notice a surface change
- Show full step-by-step working for both examples
- End pair_b with this exact question on its own line: "What changed? What stayed the same? Why does it matter?"
- State the intended variation clearly in the first line of pair_b (e.g. "Note: in this example, the value is negative.")

All maths must be correct. Plain text notation only (x^2, sqrt(), fractions as a/b).

Respond ONLY with valid JSON:
{{"pair_a": "first example with full working", "pair_b": "second example with full working, variation note, and prompt question"}}"""
    text = _call(prompt, max_tokens=700)
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
