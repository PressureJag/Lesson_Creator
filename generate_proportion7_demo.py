#!/usr/bin/env python3
"""
Complete single-objective demo — Proportion 7 Core Plus
Objective: Find the whole given a part and its percentage

All maths manually verified. No API calls.
Run with:
    python3 generate_proportion7_demo.py
"""

import os
from pptx import Presentation
from generator import slide_builder, diagram_gen, theme as T

TOPIC     = "Proportion 7 Core Plus"
OUTPUT    = "Output/Proportion7_Find_The_Whole.pptx"
OBJECTIVE = "Find the whole given a part and its percentage"

# ── Intro content ─────────────────────────────────────────────────────────────

BIG_QUESTION = "If you know a part and its percentage, how do you find the whole?"

PRIOR = [
    "Convert between fractions, decimals and percentages",
    "Find a percentage of an amount using a multiplier",
    "Calculate percentage increase and decrease",
    "Understand that 100% represents the whole",
    "Divide accurately, including dividing by a decimal",
]

FUTURE = [
    "Reverse percentage — find original value before a % change",
    "Percentage profit, loss and VAT problems",
    "Compound interest and exponential growth/decay",
    "Direct proportion and proportion equations",
    "Multi-step problems combining percentage operations",
]

VOCAB = [
    "whole — the complete amount (100%)",
    "part — a portion of the whole, expressed as a % or fraction",
    "unitary method — find 1% first, then scale to 100%",
    "decimal equivalent — a percentage written as a decimal (e.g. 30% = 0.30)",
    "reverse — working backwards from a known result to find the original",
    "divisor — the number you divide by (here, the decimal form of the %)",
]

# ── Starter (retrieval from prior learning) ───────────────────────────────────

STARTER_Q = [
    "Write 45% as a decimal.",
    "Find 30% of £180.",
    "What percentage is 12 out of 48?",
    "The multiplier for a 25% decrease is ____.",
]

STARTER_A = [
    "0.45",
    "£54\n(180 × 0.30 = 54)",
    "25%\n(12 ÷ 48 = 0.25 = 25%)",
    "0.75\n(1 − 0.25 = 0.75)",
]

# ── Common Methods (left panel of I Do slide) ─────────────────────────────────

METHODS_TEXT = """\
UNITARY METHOD

Find 1%:
  part ÷ percentage

Find 100%:
  answer × 100

One-step shortcut:
  whole = part ÷ decimal

e.g.  18 is 30%:
  18 ÷ 0.30 = 60\
"""

# ── I Do ──────────────────────────────────────────────────────────────────────

IDO_HEADING  = "18 is 30% of what number?"

IDO_EXAMPLE = """\
Find the whole when 18 is 30% of the whole.

Step 1:  Set up the ratio table
         We know: 30% of the whole = 18
         We want: 100% of the whole = ?

Step 2:  Find the multiplier that takes 30% → 100%
         100 ÷ 30 = 10/3 … or more simply:
         Divide by the decimal: ÷ 0.30

Step 3:  Apply to the known value
         18 ÷ 0.30 = 60

Answer:  The whole is 60.

In general: whole = part ÷ (percentage ÷ 100)
"""

IDO_NOTES = (
    "Stress that dividing by the decimal is the same as the two-step unitary method. "
    "Ask: 'What is 30% of 60?' — students should get 18, confirming the answer. "
    "Common error: students multiply instead of divide (e.g. 18 × 0.30). "
    "Emphasise the ratio table arrow going ÷ 0.30 in both columns."
)

# ── We Do ─────────────────────────────────────────────────────────────────────

WEDO_HEADING  = "£35 is 25% of what amount?"
WEDO_QUESTION = (
    "In a sale, a customer saves £35. This saving is 25% of the original price. "
    "Find the original price using the ratio table / unitary method."
)
WEDO_STEPS = [
    "Step 1 — Write what you know.\n£35 = 25% of the whole.",
    "Step 2 — Find 1%.\n£35 ÷ 25 = ?",
    "Step 3 — Find 100%.\nYour answer × 100 = ?",
    "Step 4 — Check.\nIs 25% of your whole = £35?",
]

# ── You Do ────────────────────────────────────────────────────────────────────

YOUDO_HEADING  = "42 is 70% of what number?"
YOUDO_QUESTION = (
    "In a class test, Kai scored 42 marks. "
    "His score is 70% of the total marks available. "
    "Find the total marks using the division method."
)
YOUDO_ANSWER = "42 ÷ 0.70 = 60  (check: 70% of 60 = 42 ✓)"

# ── Mini Whiteboard × 10 ─────────────────────────────────────────────────────

MWB_Q = [
    "10 is 50% of what number?",
    "6 is 20% of what number?",
    "15 is 25% of what number?",
    "8 is 40% of what number?",
    "£12 is 30% of what amount?",
    "21 is 35% of what number?",
    "A saving of £15 is 12.5% of the original price.\nFind the original price.",
    "63 is 90% of what number?",
    "18 students walk to school.\nThis is 45% of the class.\nHow many students are in the class?",
    "A discount of £7.50 is 15% of the original price.\nFind the original price.",
]

MWB_A = [
    "20  (10 ÷ 0.50)",
    "30  (6 ÷ 0.20)",
    "60  (15 ÷ 0.25)",
    "20  (8 ÷ 0.40)",
    "£40  (12 ÷ 0.30)",
    "60  (21 ÷ 0.35)",
    "£120  (15 ÷ 0.125)",
    "70  (63 ÷ 0.90)",
    "40 students  (18 ÷ 0.45)",
    "£50  (7.50 ÷ 0.15)",
]

# ── Independent Practice × 10 ────────────────────────────────────────────────

IP_Q = [
    "12 is 40% of what number?",
    "8 is 32% of what number?",
    "£36 is 45% of what amount?",
    "48 is 60% of what number?",
    "35 is 7% of what number?",
    "In a sale, £18 is saved. This saving is 15% of the original price.\nFind the original price.",
    "A train arrives 18 minutes late. This represents 30% of the scheduled journey time.\nFind the scheduled journey time in minutes.",
    "3.6 is 4.5% of what number?",
    "77 is 55% of what number?",
    "A school has 1,260 pupils on roll. This is 63% of the school's total capacity.\nFind the total capacity.",
]

IP_A = [
    "30  (12 ÷ 0.40 = 30)",
    "25  (8 ÷ 0.32 = 25)",
    "£80  (36 ÷ 0.45 = 80)",
    "80  (48 ÷ 0.60 = 80)",
    "500  (35 ÷ 0.07 = 500)",
    "£120  (18 ÷ 0.15 = 120)",
    "60 minutes  (18 ÷ 0.30 = 60)",
    "80  (3.6 ÷ 0.045 = 80)",
    "140  (77 ÷ 0.55 = 140)",
    "2,000  (1260 ÷ 0.63 = 2000)",
]

# ── Plenary ───────────────────────────────────────────────────────────────────

PLENARY_SUMMARY = (
    "We have learned to find the whole when we are given a part and its percentage. "
    "The key step is to write the percentage as a decimal, then divide the part by that decimal. "
    "This is equivalent to the two-step unitary method: find 1% by dividing by the percentage, "
    "then multiply by 100. The ratio table keeps the working organised and easy to check. "
    "Always verify: if your answer is correct, the given % of it should equal the part."
)

PLENARY_Q = "24 is 32% of what number?"
PLENARY_A  = "24 ÷ 0.32 = 75  (check: 32% of 75 = 0.32 × 75 = 24 ✓)"


# ── Build deck ────────────────────────────────────────────────────────────────

def main():
    prs = Presentation()
    prs.slide_width  = T.SLIDE_WIDTH
    prs.slide_height = T.SLIDE_HEIGHT

    # 1 — Title
    slide_builder.make_title_slide(prs, TOPIC, BIG_QUESTION, 4)

    # 2 — Big Picture
    slide_builder.make_overview_slide(prs, TOPIC, PRIOR, [OBJECTIVE], FUTURE)

    # 3 — Prior Knowledge
    slide_builder.make_prior_knowledge(prs, TOPIC, PRIOR)

    # 4 — Vocabulary
    slide_builder.make_vocabulary(prs, TOPIC, VOCAB)

    # 5 — Starter
    slide_builder.make_starter_plus(prs, TOPIC, STARTER_Q)

    # 6 — Starter Answers
    slide_builder.make_starter_plus(prs, TOPIC, STARTER_Q, STARTER_A)

    # 7 — Learning Intro
    slide_builder.make_learning_intro(prs, TOPIC, OBJECTIVE, 1)

    # 8 — I Do  (ratio table: 30%/18 → ÷0.30 → 100%/60)
    ido_diagram = diagram_gen.ratio_table(
        "30%", "18",
        "100%", "60",
        "÷ 0.30",
        title="Find the whole",
    )
    slide_builder.make_ido_slide(
        prs, TOPIC,
        IDO_HEADING, IDO_EXAMPLE,
        method_text=METHODS_TEXT,
        notes=IDO_NOTES,
        diagram=ido_diagram,
    )

    # 9 — We Do
    slide_builder.make_wedo_slide(
        prs, TOPIC,
        WEDO_HEADING, WEDO_QUESTION,
        scaffold_steps=WEDO_STEPS,
    )

    # 10 — You Do
    slide_builder.make_youdo_slide(
        prs, TOPIC,
        YOUDO_HEADING, YOUDO_QUESTION,
        answer=YOUDO_ANSWER,
    )

    # 11–20 — Mini Whiteboard × 10
    for i, (q, _) in enumerate(zip(MWB_Q, MWB_A), start=1):
        slide_builder.make_mini_whiteboard(prs, TOPIC, q, i, 10)

    # 21 — Independent Practice
    slide_builder.make_independent_practice(prs, TOPIC, IP_Q)

    # 22 — Independent Practice Answers
    slide_builder.make_independent_answers(prs, TOPIC, IP_Q, IP_A)

    # 23 — Plenary
    slide_builder.make_plenary(
        prs, TOPIC, OBJECTIVE,
        PLENARY_SUMMARY, PLENARY_Q, PLENARY_A,
    )

    os.makedirs("Output", exist_ok=True)
    prs.save(OUTPUT)
    print(f"\n  Saved {len(prs.slides)} slides → {OUTPUT}\n")


if __name__ == "__main__":
    main()
