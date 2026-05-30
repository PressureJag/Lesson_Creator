#!/usr/bin/env python3
"""
Lesson slide-deck generator for Outwood Grange Academies Trust.

Usage:
  python3 generate_lesson.py \\
    --summary  "Examples/SOW/Algebra 1 - Core Plus Summary of Intent.pdf" \\
    --methods  "Examples/SOW/Algebra 1 - Consistent Methodology.pdf" \\
    --topic    "Algebra 1 Core Plus" \\
    --output   "Output/Algebra_1.pptx"
"""

import argparse
import os
import sys

from pptx import Presentation

from generator import sow_parser, content_gen, slide_builder, diagram_gen, planner
from generator import theme as T
from generator.notification import header, notify, prompt_choice
from generator import gdrive


# ── Diagram builder ──────────────────────────────────────────────────────────

def build_diagram(obj_text: str, diagram_override=None):
    """Generate an appropriate diagram image, or return None."""
    from generator import content_gen as cg
    dtype = diagram_override or cg.select_diagram_type(obj_text)

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


# ── Slide deck assembly ──────────────────────────────────────────────────────

def build_deck(sow: dict, methods: dict, topic_name: str, output_path: str) -> None:
    prs = Presentation()
    prs.slide_width  = T.SLIDE_WIDTH
    prs.slide_height = T.SLIDE_HEIGHT

    objectives = sow["objectives"]
    prior      = sow["prior_knowledge"]
    misconcs   = sow["misconceptions"]
    vocab      = sow["vocabulary"]
    extend     = sow["extend"]
    pd_        = sow["personal_development"]
    hours      = sow["time_hours"]
    big_q      = sow["big_question"]

    total = len(objectives)
    methods_pages = list(methods.values())

    header(
        f"BUILDING DECK  —  {topic_name}",
        f"{total} objectives · {total * 15} slides estimated",
    )
    notify(f"Objectives parsed: {total}", "info")
    notify(f"Vocabulary terms:  {len(vocab)}", "info")
    notify(f"Misconceptions:    {len(misconcs)}", "info")

    # ── Intro slides ─────────────────────────────────────────
    notify("Building title slide …", "progress")
    slide_builder.make_title_slide(prs, topic_name, big_q, hours)

    notify("Building prior knowledge slide …", "progress")
    slide_builder.make_prior_knowledge(prs, topic_name, prior)

    if vocab:
        notify("Building vocabulary slide …", "progress")
        slide_builder.make_vocabulary(prs, topic_name, vocab)

    # ── Objective blocks ─────────────────────────────────────
    skip_next = False
    abort     = False
    idx       = 0

    for idx, obj in enumerate(objectives, start=1):

        if skip_next:
            notify(f"Skipping objective {idx}/{total} (user request)", "warning")
            skip_next = False
            continue

        # ── Planning choices ──────────────────────────────────
        obj_short = obj[:70] + ("…" if len(obj) > 70 else "")

        if idx - 1 < len(methods_pages):
            methods_text = methods_pages[idx - 1]
        else:
            methods_text = ""
            for key, val in methods.items():
                if any(w in key.lower() for w in obj.lower().split()[:4]):
                    methods_text = val
                    break

        plan_opts = planner.get_options(obj, topic_name, methods_text)
        plan_display = planner.to_prompt_list(plan_opts)

        choice_idx = prompt_choice(
            title=f"OBJECTIVE {idx}/{total}  —  {obj_short}",
            options=plan_display,
            default=0,
            timeout=120,
        )

        chosen = plan_opts[choice_idx]
        if chosen["skip"]:
            notify(f"Skipping objective {idx}/{total}", "warning")
            continue

        diagram_override = chosen.get("diagram")

        # ── Build slides for this objective ───────────────────
        notify(f"Objective {idx}/{total}: {obj[:55]} …", "section")

        notify("Generating retrieval starter …", "progress")
        retrieval = content_gen.generate_retrieval_questions(prior, obj, topic_name)
        slide_builder.make_retrieval_starter(prs, topic_name, retrieval["questions"])
        slide_builder.make_retrieval_starter(
            prs, topic_name, retrieval["questions"],
            answers=True, answer_list=retrieval["answers"]
        )

        slide_builder.make_section_divider(prs, topic_name, idx, obj)
        slide_builder.make_learning_objective(prs, topic_name, obj, idx)

        notify("Generating hook …", "progress")
        hook = content_gen.generate_hook(obj, topic_name, pd_)
        slide_builder.make_hook(prs, topic_name, hook, obj)

        # I Do
        notify("Generating worked example (I Do) …", "progress")
        worked = content_gen.generate_worked_example(obj, topic_name, methods_text)
        slide_builder.make_teaching_text(
            prs, topic_name,
            worked["heading"], worked["example"], worked.get("notes", ""),
            phase="I Do"
        )

        diag = build_diagram(obj, diagram_override)
        if diag:
            notify("Adding visual diagram (I Do) …", "progress")
            slide_builder.make_teaching_visual(
                prs, topic_name,
                worked["heading"], diag,
                right_text=worked["example"][:300],
                phase="I Do"
            )

        # We Do
        notify("Generating guided practice (We Do) …", "progress")
        we_do = content_gen.generate_we_do(obj, topic_name, methods_text)
        slide_builder.make_we_do(prs, topic_name, we_do, answers=False)
        slide_builder.make_we_do(prs, topic_name, we_do, answers=True)

        # WSWT
        notify("Generating What's the Same / What's Different …", "progress")
        wswt = content_gen.generate_wswt_pair(obj, topic_name)
        slide_builder.make_wswt(prs, topic_name, wswt["pair_a"], wswt["pair_b"])

        # You Do
        notify("Generating practice questions (You Do) …", "progress")
        practice = content_gen.generate_practice_questions(obj, topic_name)
        qs  = practice["questions"]
        ans = practice["answers"]
        slide_builder.make_practice(
            prs, topic_name,
            f"Practice — {obj[:50]}",
            qs[:6], two_column=True, phase="You Do"
        )
        slide_builder.make_answers(
            prs, topic_name,
            f"Practice — {obj[:50]}",
            list(zip(qs[:6], ans[:6]))
        )

        # Reasoning
        task_type = "asn" if idx % 2 == 1 else "open"
        notify(f"Generating reasoning task ({task_type}) …", "progress")
        reasoning = content_gen.generate_reasoning_task(obj, topic_name, task_type)
        slide_builder.make_reasoning(prs, topic_name, reasoning, task_type)

        # Misconception
        if idx <= len(misconcs):
            slide_builder.make_misconception(
                prs, topic_name,
                misconcs[idx - 1],
                f"Remember: {misconcs[idx - 1].split('.')[0]} — check your working carefully."
            )

        notify(f"Objective {idx}/{total} complete  ({len(prs.slides)} slides so far)", "success")

        # ── Between-objective checkpoint ──────────────────────
        if idx < total:
            next_short = objectives[idx][:55] + ("…" if len(objectives[idx]) > 55 else "")
            is_last_remaining = (idx + 1 == total)
            skip_desc = (
                f"Omit the final objective and finish the deck"
                if is_last_remaining
                else f"Jump past objective {idx + 1} and continue from {idx + 2}"
            )
            cont_choice = prompt_choice(
                title=f"CHECKPOINT — after objective {idx}/{total}",
                options=[
                    ("Continue to next objective",
                     f"Next: {next_short}"),
                    ("Skip next objective", skip_desc),
                    ("Abort — save deck as-is",
                     "Stop here and save the partial deck to output + Google Drive"),
                ],
                default=0,
                timeout=120,
            )
            if cont_choice == 1:
                skip_next = True
            elif cont_choice == 2:
                notify("Aborting — saving partial deck …", "warning")
                abort = True
                break

    if abort:
        notify(f"Generation aborted after {idx} objective(s) — saving partial deck", "warning")

    # ── Extension ─────────────────────────────────────────────
    if not abort and extend:
        notify("Building extension slide …", "progress")
        slide_builder.make_extension(prs, topic_name, "Going Further", extend)

    # ── Save ──────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    prs.save(output_path)

    slide_count = len(prs.slides)
    header("GENERATION COMPLETE", f"{slide_count} slides  →  {output_path}", color="\033[32m")
    notify(f"Saved: {output_path}", "success")

    # ── Google Drive upload ────────────────────────────────────
    notify("Uploading to Google Drive …", "progress")
    result = gdrive.upload(output_path)
    if result["success"]:
        notify(f"Google Drive: {result['uploaded'][0]}", "success")
    else:
        notify(f"Google Drive upload failed: {result['error']}", "warning")

    # ── Final options ─────────────────────────────────────────
    final_choice = prompt_choice(
        title="WHAT WOULD YOU LIKE TO DO NEXT?",
        options=[
            ("Done",
             "Exit the generator"),
            ("Open output folder in Finder",
             f"Open {os.path.dirname(os.path.abspath(output_path))}"),
            ("Open Google Drive folder in Finder",
             result["folder"] if result["success"] else "Google Drive not available"),
        ],
        default=0,
        timeout=120,
    )

    if final_choice == 1:
        folder = os.path.dirname(os.path.abspath(output_path))
        os.system(f'open "{folder}"')
    elif final_choice == 2 and result["success"]:
        os.system(f'open "{result["folder"]}"')


# ── Startup prompt ───────────────────────────────────────────────────────────

def _confirm_mode() -> bool:
    """
    Ask the user whether to run in demo mode or full API mode.
    Returns True if demo mode, False if full mode.
    Defaults to demo mode after 2 minutes.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    has_key = bool(api_key)

    if not has_key:
        header(
            "LESSON CREATOR  —  Outwood Grange Academies Trust",
            "Demo mode  (no ANTHROPIC_API_KEY found)",
        )
        notify("Running in demo mode — stub content will be used", "info")
        notify("Set ANTHROPIC_API_KEY to generate real AI content", "info")
        return True  # no choice needed

    header(
        "LESSON CREATOR  —  Outwood Grange Academies Trust",
        "API key detected — choose generation mode",
    )

    choice = prompt_choice(
        title="SELECT GENERATION MODE",
        options=[
            ("Demo mode",
             "Fast — uses realistic stub content, no API calls, no cost"),
            ("Full generation (uses API)",
             "Slow — real AI-generated maths content via Claude API (~£0.05–£0.50 per deck)"),
            ("Cancel",
             "Exit without generating"),
        ],
        default=0,
        timeout=120,
    )

    if choice == 2:
        notify("Cancelled.", "warning")
        sys.exit(0)

    return choice == 0  # 0 = demo, 1 = full


# ── CLI entry point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate an Outwood lesson slide deck from a Scheme of Work."
    )
    parser.add_argument("--summary",  required=True,
                        help="Path to 'Core Plus Summary of Intent' PDF")
    parser.add_argument("--methods",  required=True,
                        help="Path to 'Common Methods / Consistent Methodology' PDF")
    parser.add_argument("--topic",    default="",
                        help="Topic name override (e.g. 'Algebra 1 Core Plus')")
    parser.add_argument("--hours",    type=int, default=0,
                        help="Override recommended teaching hours")
    parser.add_argument("--output",   default="",
                        help="Output PPTX path (default: Output/<topic>.pptx)")
    args = parser.parse_args()

    # ── Mode selection ────────────────────────────────────────
    demo = _confirm_mode()
    content_gen.set_demo_mode(demo)

    mode_label = "DEMO" if demo else "FULL (API)"
    notify(f"Mode: {mode_label}", "info")

    # ── Parse PDFs ────────────────────────────────────────────
    notify("Parsing Summary of Intent …", "progress")
    sow = sow_parser.parse_summary(args.summary)

    if args.topic:
        sow["topic"] = args.topic
    if args.hours:
        sow["time_hours"] = args.hours

    topic_name  = sow["topic"]
    output_path = args.output or f"Output/{topic_name.replace(' ', '_')}.pptx"

    notify("Parsing Common Methods …", "progress")
    methods = sow_parser.parse_methods(args.methods)

    notify(f"Topic:  {topic_name}", "info")
    notify(f"Output: {output_path}", "info")

    build_deck(sow, methods, topic_name, output_path)


if __name__ == "__main__":
    main()
