#!/usr/bin/env python3
"""
Lesson slide-deck generator for Outwood Grange Academies Trust.

Usage:
  python generate_lesson.py \\
    --summary  "Examples/SOW/Algebra 1 - Core Plus Summary of Intent.pdf" \\
    --methods  "Examples/SOW/Algebra 1 - Consistent Methodology.pdf" \\
    --topic    "Algebra 1 Core Plus" \\
    --hours    10 \\
    --output   "Output/Algebra_1.pptx"
"""

import argparse
import os
import sys
import io

from pptx import Presentation

from generator import sow_parser, content_gen, slide_builder, diagram_gen
from generator import theme as T


def build_diagram(obj_text: str):
    """Generate an appropriate diagram for the objective, or return None."""
    dtype = content_gen.select_diagram_type(obj_text)
    if dtype == "percentage_bar":
        return diagram_gen.percentage_bar(
            whole=240, part_pct=30,
            whole_label="100%", part_label="30%",
            title="Percentage model"
        )
    if dtype == "number_line":
        return diagram_gen.number_line(
            lo=-6, hi=8,
            intervals=[(-2, 5, True, False)],
            title="Number line"
        )
    if dtype == "area_grid":
        return diagram_gen.area_grid(
            rows=["x", "+3"],
            cols=["x", "+2"],
            cells=[["x²", "+2x"], ["+3x", "+6"]],
            title="Expansion grid: (x+3)(x+2)"
        )
    if dtype == "angle":
        return diagram_gen.angle_diagram("alternate")
    if dtype == "bar_model":
        return diagram_gen.bar_model(
            parts=[(1, "#D4C5E2", "a"), (2, "#5B2C8D", "2a")],
            total_label="3a"
        )
    return None


def build_deck(sow: dict, methods: dict, topic_name: str,
               output_path: str) -> None:
    """Main slide assembly loop."""
    prs = Presentation()
    prs.slide_width  = T.SLIDE_WIDTH
    prs.slide_height = T.SLIDE_HEIGHT

    objectives  = sow["objectives"]
    prior       = sow["prior_knowledge"]
    misconcs    = sow["misconceptions"]
    vocab       = sow["vocabulary"]
    extend      = sow["extend"]
    pd          = sow["personal_development"]
    hours       = sow["time_hours"]
    big_q       = sow["big_question"]

    total = len(objectives)
    print(f"  Objectives: {total}")
    print(f"  Vocabulary: {len(vocab)} terms")
    print(f"  Misconceptions: {len(misconcs)}")
    print()

    # ── Title slide ─────────────────────────────────────────
    print("Building title slide…")
    slide_builder.make_title_slide(prs, topic_name, big_q, hours)

    # ── Prior knowledge recap ────────────────────────────────
    print("Building prior knowledge slide…")
    slide_builder.make_prior_knowledge(prs, topic_name, prior)

    # ── Vocabulary ──────────────────────────────────────────
    if vocab:
        print("Building vocabulary slide…")
        slide_builder.make_vocabulary(prs, topic_name, vocab)

    # ── Objective blocks ─────────────────────────────────────
    methods_pages = list(methods.values())  # ordered list of methods pages

    for idx, obj in enumerate(objectives, start=1):
        print(f"\nObjective {idx}/{total}: {obj[:60]}…")

        # Match methods text by index first, fall back to keyword search
        if idx - 1 < len(methods_pages):
            methods_text = methods_pages[idx - 1]
        else:
            methods_text = ""
            for key, val in methods.items():
                if any(word in key.lower() for word in obj.lower().split()[:4]):
                    methods_text = val
                    break

        # Per-objective retrieval starter
        print("  Generating retrieval starter…")
        retrieval = content_gen.generate_retrieval_questions(prior, obj, topic_name)
        slide_builder.make_retrieval_starter(prs, topic_name, retrieval["questions"])
        slide_builder.make_retrieval_starter(prs, topic_name, retrieval["questions"],
                                             answers=True,
                                             answer_list=retrieval["answers"])

        # Section divider
        slide_builder.make_section_divider(prs, topic_name, idx, obj)

        # Learning objective
        slide_builder.make_learning_objective(prs, topic_name, obj, idx)

        # Hook for every objective
        print("  Generating hook…")
        hook = content_gen.generate_hook(obj, topic_name, pd)
        slide_builder.make_hook(prs, topic_name, hook, obj)

        # ── I Do ────────────────────────────────────────────────
        print("  Generating worked example (I Do)…")
        worked = content_gen.generate_worked_example(obj, topic_name, methods_text)
        slide_builder.make_teaching_text(
            prs, topic_name,
            worked["heading"], worked["example"], worked.get("notes", ""),
            phase="I Do"
        )

        # Visual diagram (still part of I Do)
        diag = build_diagram(obj)
        if diag:
            print("  Adding diagram (I Do)…")
            slide_builder.make_teaching_visual(
                prs, topic_name,
                worked["heading"], diag,
                right_text=worked["example"][:300],
                phase="I Do"
            )

        # ── We Do ───────────────────────────────────────────────
        print("  Generating guided practice (We Do)…")
        we_do = content_gen.generate_we_do(obj, topic_name, methods_text)
        slide_builder.make_we_do(prs, topic_name, we_do, answers=False)
        slide_builder.make_we_do(prs, topic_name, we_do, answers=True)

        # What's the same / What's different
        print("  Generating WSWT task…")
        wswt = content_gen.generate_wswt_pair(obj, topic_name)
        slide_builder.make_wswt(prs, topic_name,
                                 wswt["pair_a"], wswt["pair_b"])

        # ── You Do ──────────────────────────────────────────────
        print("  Generating practice questions (You Do)…")
        practice = content_gen.generate_practice_questions(obj, topic_name)
        qs = practice["questions"]
        ans = practice["answers"]

        slide_builder.make_practice(prs, topic_name,
                                     f"Practice — {obj[:50]}",
                                     qs[:6], two_column=True,
                                     phase="You Do")
        slide_builder.make_answers(prs, topic_name,
                                    f"Practice — {obj[:50]}",
                                    list(zip(qs[:6], ans[:6])))

        # Reasoning task (alternate between ASN and open)
        task_type = "asn" if idx % 2 == 1 else "open"
        print(f"  Generating reasoning ({task_type})…")
        reasoning = content_gen.generate_reasoning_task(obj, topic_name, task_type)
        slide_builder.make_reasoning(prs, topic_name, reasoning, task_type)

        # Misconception (one per 2 objectives)
        if idx <= len(misconcs):
            slide_builder.make_misconception(
                prs, topic_name,
                misconcs[idx - 1],
                f"Remember: {misconcs[idx - 1].split('.')[0]} — check your working carefully."
            )

    # ── Extension tasks ──────────────────────────────────────
    if extend:
        print("\nBuilding extension slide…")
        slide_builder.make_extension(prs, topic_name,
                                      "Going Further", extend)

    # ── Save ─────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    prs.save(output_path)
    print(f"\n✓ Saved {len(prs.slides)} slides → {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate an Outwood lesson slide deck from a Scheme of Work."
    )
    parser.add_argument("--summary", required=True,
                        help="Path to 'Core Plus Summary of Intent' PDF")
    parser.add_argument("--methods", required=True,
                        help="Path to 'Common Methods / Consistent Methodology' PDF")
    parser.add_argument("--topic", default="",
                        help="Topic name override (e.g. 'Algebra 1 Core Plus')")
    parser.add_argument("--hours", type=int, default=0,
                        help="Override recommended teaching hours")
    parser.add_argument("--output", default="",
                        help="Output PPTX path (default: Output/<topic>.pptx)")
    args = parser.parse_args()

    print("Parsing Summary of Intent…")
    sow = sow_parser.parse_summary(args.summary)

    if args.topic:
        sow["topic"] = args.topic
    if args.hours:
        sow["time_hours"] = args.hours

    topic_name = sow["topic"]
    output_path = args.output or f"Output/{topic_name.replace(' ', '_')}.pptx"

    print("Parsing Common Methods…")
    methods = sow_parser.parse_methods(args.methods)

    print(f"\nGenerating lesson deck: {topic_name}")
    print(f"Output: {output_path}")
    print("─" * 50)

    build_deck(sow, methods, topic_name, output_path)


if __name__ == "__main__":
    main()
