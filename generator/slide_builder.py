"""Build individual slides using python-pptx, applying the Outwood brand theme."""

import io
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import copy

from . import theme as T


def _new_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width  = T.SLIDE_WIDTH
    prs.slide_height = T.SLIDE_HEIGHT
    return prs


def _blank_slide(prs: Presentation):
    """Add a blank slide with the Outwood yellow background."""
    layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(layout)
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = T.YELLOW_BG
    return slide


def _add_logo(slide):
    """Add the Outwood logo to the top-left of a slide."""
    logo_path = T.LOGO_PATH
    if os.path.exists(logo_path):
        slide.shapes.add_picture(
            logo_path,
            T.LOGO_LEFT, T.LOGO_TOP,
            T.LOGO_WIDTH, T.LOGO_HEIGHT
        )


def _add_title_text(slide, topic_name: str):
    """Add the topic title (e.g. 'Algebra 1 Core Plus') centred at the top."""
    txBox = slide.shapes.add_textbox(T.TITLE_LEFT, T.TITLE_TOP,
                                     T.TITLE_WIDTH, T.TITLE_HEIGHT)
    tf = txBox.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = topic_name
    run.font.name = T.FONT_NAME
    run.font.size = T.TITLE_SIZE
    run.font.bold = False
    run.font.color.rgb = T.PURPLE


def _add_watermark(slide):
    """Add a subtle purple dot-pattern watermark to the top-right corner."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig, ax = plt.subplots(figsize=(3, 3), facecolor="white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    np.random.seed(42)
    for _ in range(30):
        x = np.random.uniform(0.05, 0.95)
        y = np.random.uniform(0.05, 0.95)
        r = np.random.uniform(0.02, 0.09)
        alpha = np.random.uniform(0.06, 0.14)
        circle = patches.Circle((x, y), r, color="#5B2C8D", alpha=alpha)
        ax.add_patch(circle)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=80, bbox_inches="tight",
                transparent=True)
    plt.close(fig)
    buf.seek(0)

    wm_w = Inches(3.5)
    wm_h = Inches(3.5)
    slide.shapes.add_picture(buf, T.SLIDE_WIDTH - wm_w,
                             Inches(0), wm_w, wm_h)


def _add_header(slide, topic_name: str):
    """Convenience: logo + title + watermark."""
    _add_watermark(slide)
    _add_logo(slide)
    _add_title_text(slide, topic_name)


def _textbox(slide, left, top, width, height,
             text="", font_size=None, bold=False,
             colour=None, alignment=PP_ALIGN.LEFT,
             underline=False, italic=False, word_wrap=True):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = word_wrap
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.name = T.FONT_NAME
    run.font.size = font_size or T.BODY_SIZE
    run.font.bold = bold
    run.font.italic = italic
    run.font.underline = underline
    if colour:
        run.font.color.rgb = colour
    return txBox


def _coloured_box(slide, left, top, width, height, fill_colour, text="",
                  text_colour=None, font_size=None, bold=False,
                  alignment=PP_ALIGN.CENTER, border_colour=None,
                  border_pt=1.5):
    """Add a filled rectangle with optional centred text and optional border."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_colour
    if border_colour:
        shape.line.color.rgb = border_colour
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()

    if text:
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = alignment
        run = p.add_run()
        run.text = text
        run.font.name = T.FONT_NAME
        run.font.size = font_size or T.BODY_SIZE
        run.font.bold = bold
        run.font.color.rgb = text_colour or T.WHITE
    return shape


def _embed_image(slide, img_bytes: io.BytesIO, left, top, width, height):
    slide.shapes.add_picture(img_bytes, left, top, width, height)


def _phase_badge(slide, phase: str):
    """Add a small coloured pill badge for I Do / We Do / You Do phases."""
    colours = {
        "I Do":   T.PURPLE,
        "We Do":  T.TEAL,
        "You Do": T.ORANGE,
    }
    colour = colours.get(phase, T.PURPLE)
    _coloured_box(slide,
                  Inches(0.3), Inches(0.88),
                  Inches(1.1), Inches(0.38),
                  colour,
                  text=phase, text_colour=T.WHITE,
                  font_size=Pt(13), bold=True,
                  alignment=PP_ALIGN.CENTER)


# ─────────────────────────────────────────────
#  Slide constructors
# ─────────────────────────────────────────────

def make_title_slide(prs: Presentation, topic_name: str,
                     big_question: str, time_hours: int) -> None:
    """Opening title card for the whole deck."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    # Purple banner
    _coloured_box(slide,
                  Inches(0.3), Inches(1.1),
                  Inches(9.4), Inches(1.0),
                  T.PURPLE,
                  text=big_question,
                  font_size=Pt(22), bold=True, alignment=PP_ALIGN.CENTER)

    # Recommended time
    _textbox(slide, Inches(3), Inches(2.3), Inches(4), Inches(0.6),
             text=f"Recommended Time: {time_hours} hours",
             font_size=Pt(18), colour=T.DARK_GREY, alignment=PP_ALIGN.CENTER)


def make_retrieval_starter(prs: Presentation, topic_name: str,
                           questions: list[str], answers: bool = False,
                           answer_list: list[str] = None) -> None:
    """4-question retrieval starter in a 2×2 grid."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    label = "Retrieval Starter — Answers" if answers else "Retrieval Starter"
    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.4),
             text=label, font_size=T.HEADING_SIZE, bold=True,
             colour=T.PURPLE, underline=True)

    positions = [
        (Inches(0.3),  Inches(1.4)),
        (Inches(5.1),  Inches(1.4)),
        (Inches(0.3),  Inches(4.3)),
        (Inches(5.1),  Inches(4.3)),
    ]
    box_w = Inches(4.6)
    box_h = Inches(2.7)

    q_list = questions[:4]
    a_list = (answer_list or []) if answers else []

    colours = [T.PURPLE_LIGHT, T.PURPLE_LIGHT, T.PURPLE_LIGHT, T.PURPLE_LIGHT]

    for i, (q, (lft, top)) in enumerate(zip(q_list, positions)):
        # Box border
        _coloured_box(slide, lft, top, box_w, box_h, T.PURPLE_LIGHT)

        # Question text inside
        inner_text = q
        if answers and i < len(a_list):
            inner_text = f"{q}\n\nAnswer: {a_list[i]}"

        _textbox(slide, lft + Inches(0.1), top + Inches(0.1),
                 box_w - Inches(0.2), box_h - Inches(0.2),
                 text=inner_text,
                 font_size=T.BODY_SIZE, colour=T.BLACK, word_wrap=True)


def make_learning_objective(prs: Presentation, topic_name: str,
                            objective: str, objective_num: int) -> None:
    """Learning objective slide — 'How do I…?' framing."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.4),
             text=f"Learning Objective {objective_num}",
             font_size=T.HEADING_SIZE, bold=True,
             colour=T.PURPLE, underline=True)

    _coloured_box(slide,
                  Inches(0.6), Inches(1.6),
                  Inches(8.8), Inches(1.4),
                  T.PURPLE,
                  text=f"How do I {objective.lower().rstrip('.')}?",
                  font_size=Pt(20), bold=True, alignment=PP_ALIGN.CENTER)


def make_hook(prs: Presentation, topic_name: str,
              scenario: str, objective: str) -> None:
    """Real-world context hook slide."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.4),
             text="Why does this matter?",
             font_size=T.HEADING_SIZE, bold=True,
             colour=T.PURPLE, underline=True)

    _textbox(slide, Inches(0.4), Inches(1.4), Inches(9.2), Inches(5.5),
             text=scenario, font_size=Pt(18), colour=T.DARK_GREY, word_wrap=True)


def make_teaching_text(prs: Presentation, topic_name: str,
                       heading: str, worked_example: str,
                       notes: str = "", phase: str = "I Do") -> None:
    """Teacher-led worked example — text only. Phase badge: I Do / We Do / You Do."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _phase_badge(slide, phase)
    _textbox(slide, Inches(1.5), Inches(0.88), Inches(8.2), Inches(0.45),
             text=heading, font_size=T.HEADING_SIZE, bold=True,
             colour=T.BLACK, underline=True)

    split = Inches(5.8) if notes else Inches(9.4)

    _textbox(slide, Inches(0.3), Inches(1.45), split - Inches(0.3),
             Inches(5.8), text=worked_example,
             font_size=Pt(17), colour=T.BLACK, word_wrap=True)

    if notes:
        _coloured_box(slide,
                      split + Inches(0.1), Inches(1.45),
                      Inches(9.6) - split, Inches(5.8),
                      T.PURPLE_LIGHT,
                      text=notes,
                      text_colour=T.BLACK, font_size=Pt(14),
                      alignment=PP_ALIGN.LEFT)


def make_teaching_visual(prs: Presentation, topic_name: str,
                         heading: str, img_bytes: io.BytesIO,
                         right_text: str = "", phase: str = "I Do") -> None:
    """Worked example with a diagram on the left, text on the right."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _phase_badge(slide, phase)
    _textbox(slide, Inches(1.5), Inches(0.88), Inches(8.2), Inches(0.45),
             text=heading, font_size=T.HEADING_SIZE, bold=True,
             colour=T.BLACK, underline=True)

    if img_bytes:
        _embed_image(slide, img_bytes,
                     Inches(0.3), Inches(1.5),
                     Inches(5.0), Inches(5.5))

    if right_text:
        _textbox(slide, Inches(5.5), Inches(1.5), Inches(4.2), Inches(5.5),
                 text=right_text, font_size=Pt(16),
                 colour=T.BLACK, word_wrap=True)


def make_we_do(prs: Presentation, topic_name: str,
               we_do_data: dict, answers: bool = False) -> None:
    """
    We Do guided practice slide.
    Question version: shows the problem + 4 scaffold step boxes.
    Answer version (answers=True): shows the problem + full worked solution.
    """
    TEAL_LIGHT  = RGBColor(0xD1, 0xF2, 0xEB)
    GREEN_LIGHT = RGBColor(0xE8, 0xF8, 0xF5)

    slide = _blank_slide(prs)
    _add_header(slide, topic_name)
    _phase_badge(slide, "We Do")

    heading_text = ("We Do — Answers" if answers
                    else we_do_data.get("heading", "We Do — Guided Practice"))
    _textbox(slide, Inches(1.5), Inches(0.88), Inches(8.2), Inches(0.45),
             text=heading_text, font_size=T.HEADING_SIZE, bold=True,
             colour=T.BLACK, underline=True)

    # Problem statement box
    _coloured_box(slide,
                  Inches(0.3), Inches(1.45),
                  Inches(9.4), Inches(1.45),
                  TEAL_LIGHT,
                  text=we_do_data.get("problem", ""),
                  text_colour=T.BLACK, font_size=Pt(16),
                  alignment=PP_ALIGN.LEFT)

    if answers:
        _coloured_box(slide,
                      Inches(0.3), Inches(3.05),
                      Inches(9.4), Inches(4.2),
                      GREEN_LIGHT,
                      text=we_do_data.get("answer", ""),
                      text_colour=T.BLACK, font_size=Pt(15),
                      alignment=PP_ALIGN.LEFT)
    else:
        # 4 scaffold step boxes in a 2×2 grid
        steps = we_do_data.get("steps", [f"Step {i+1}" for i in range(4)])
        positions = [
            (Inches(0.3), Inches(3.05)),
            (Inches(5.1), Inches(3.05)),
            (Inches(0.3), Inches(5.15)),
            (Inches(5.1), Inches(5.15)),
        ]
        heights = [Inches(1.95), Inches(1.95), Inches(2.1), Inches(2.1)]
        for i, ((lft, top), h) in enumerate(zip(positions, heights)):
            step_text = steps[i] if i < len(steps) else f"Step {i + 1}"
            _coloured_box(slide, lft, top, Inches(4.6), h,
                          T.PURPLE_LIGHT,
                          text=step_text,
                          text_colour=T.BLACK, font_size=Pt(14),
                          alignment=PP_ALIGN.LEFT)


def make_wswt(prs: Presentation, topic_name: str,
              pair_a: str, pair_b: str,
              question: str = "What's the same? What's different?") -> None:
    """Comparison task slide."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
             text=question, font_size=T.HEADING_SIZE, bold=True,
             colour=T.PURPLE, underline=True)

    for lft, text, col in [(Inches(0.3),  pair_a, T.PURPLE_LIGHT),
                           (Inches(5.2),  pair_b, RGBColor(0xF0, 0xE0, 0xFF))]:
        _coloured_box(slide, lft, Inches(1.5), Inches(4.6), Inches(5.5),
                      col, text=text, text_colour=T.BLACK,
                      font_size=Pt(16), alignment=PP_ALIGN.LEFT)


def make_practice(prs: Presentation, topic_name: str,
                  heading: str, questions: list[str],
                  two_column: bool = False, phase: str = "You Do") -> None:
    """Practice questions slide — lettered list."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _phase_badge(slide, phase)
    _textbox(slide, Inches(1.5), Inches(0.88), Inches(8.2), Inches(0.45),
             text=heading, font_size=T.HEADING_SIZE, bold=True,
             colour=T.BLACK, underline=True)

    letters = "abcdefghijklmnopqrstuvwxyz"

    if two_column and len(questions) > 4:
        mid = len(questions) // 2
        cols = [questions[:mid], questions[mid:]]
        lefts = [Inches(0.3), Inches(5.1)]
        for qs, lft in zip(cols, lefts):
            text = "\n".join(f"{letters[i]})  {q}" for i, q in enumerate(qs))
            _textbox(slide, lft, Inches(1.5), Inches(4.6), Inches(5.7),
                     text=text, font_size=Pt(15), colour=T.BLACK, word_wrap=True)
    else:
        text = "\n".join(f"{letters[i]})  {q}" for i, q in enumerate(questions))
        _textbox(slide, Inches(0.3), Inches(1.5), Inches(9.4), Inches(5.7),
                 text=text, font_size=Pt(15), colour=T.BLACK, word_wrap=True)


def make_reasoning(prs: Presentation, topic_name: str,
                   task: str, prompt_type: str = "asn") -> None:
    """
    Reasoning task slide.
    prompt_type: 'asn' = Always/Sometimes/Never, 'wswt' = WSWT, 'open' = open
    """
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    headings = {
        "asn":  "Always, Sometimes or Never True?",
        "wswt": "What's the Same? What's Different?",
        "open": "Mathematical Reasoning",
    }
    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
             text=headings.get(prompt_type, "Reasoning"),
             font_size=T.HEADING_SIZE, bold=True,
             colour=T.PURPLE, underline=True)

    _coloured_box(slide,
                  Inches(0.5), Inches(1.5),
                  Inches(9.0), Inches(4.5),
                  T.PURPLE_LIGHT, text=task,
                  text_colour=T.BLACK, font_size=Pt(17),
                  alignment=PP_ALIGN.LEFT)

    if prompt_type == "asn":
        _textbox(slide, Inches(0.5), Inches(6.1), Inches(9.0), Inches(0.6),
                 text="Explain why — and for 'sometimes', state when it is true.",
                 font_size=Pt(13), colour=T.DARK_GREY, italic=True)


def make_answers(prs: Presentation, topic_name: str,
                 heading: str, qa_pairs: list[tuple[str, str]]) -> None:
    """Question + answer pairs in two columns."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
             text=f"{heading} — Answers",
             font_size=T.HEADING_SIZE, bold=True,
             colour=T.BLACK, underline=True)

    letters = "abcdefghijklmnopqrstuvwxyz"
    mid = (len(qa_pairs) + 1) // 2
    cols = [qa_pairs[:mid], qa_pairs[mid:]]
    lefts = [Inches(0.3), Inches(5.1)]

    for pairs, lft in zip(cols, lefts):
        text = "\n".join(
            f"{letters[i]})  {q}  =  {a}" for i, (q, a) in enumerate(pairs)
        )
        _textbox(slide, lft, Inches(1.5), Inches(4.6), Inches(5.7),
                 text=text, font_size=Pt(14), colour=T.BLACK, word_wrap=True)


def make_misconception(prs: Presentation, topic_name: str,
                       misconception: str, correction: str) -> None:
    """Misconception callout slide."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
             text="Common Misconception", font_size=T.HEADING_SIZE, bold=True,
             colour=RGBColor(0xC0, 0x39, 0x2B), underline=True)

    _coloured_box(slide,
                  Inches(0.4), Inches(1.5),
                  Inches(9.2), Inches(2.0),
                  RGBColor(0xFD, 0xED, 0xEC),
                  text=f"✗  {misconception}",
                  text_colour=RGBColor(0xC0, 0x39, 0x2B),
                  font_size=Pt(17), alignment=PP_ALIGN.LEFT)

    _coloured_box(slide,
                  Inches(0.4), Inches(3.7),
                  Inches(9.2), Inches(2.0),
                  RGBColor(0xE9, 0xF7, 0xEF),
                  text=f"✓  {correction}",
                  text_colour=RGBColor(0x1E, 0x8B, 0x4C),
                  font_size=Pt(17), alignment=PP_ALIGN.LEFT)


def make_vocabulary(prs: Presentation, topic_name: str,
                    vocab_list: list[str]) -> None:
    """Key vocabulary slide."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
             text="Key Vocabulary", font_size=T.HEADING_SIZE, bold=True,
             colour=T.PURPLE, underline=True)

    cols = 3
    per_col = (len(vocab_list) + cols - 1) // cols
    col_w = Inches(3.0)
    for ci in range(cols):
        chunk = vocab_list[ci * per_col: (ci + 1) * per_col]
        text = "\n".join(f"•  {v}" for v in chunk)
        _textbox(slide,
                 Inches(0.3) + ci * col_w,
                 Inches(1.5),
                 col_w - Inches(0.1),
                 Inches(5.5),
                 text=text, font_size=Pt(16),
                 colour=T.BLACK, word_wrap=True)


def make_section_divider(prs: Presentation, topic_name: str,
                         objective_num: int, objective_text: str) -> None:
    """Purple banner slide to mark a new objective block."""
    slide = _blank_slide(prs)
    _add_watermark(slide)
    _add_logo(slide)

    _coloured_box(slide,
                  Inches(0), Inches(2.5),
                  T.SLIDE_WIDTH, Inches(2.5),
                  T.PURPLE,
                  text=f"Objective {objective_num}\n{objective_text}",
                  font_size=Pt(22), bold=True, alignment=PP_ALIGN.CENTER)

    _textbox(slide, Inches(0.3), Inches(0.05), Inches(9.4), Inches(0.6),
             text=topic_name, font_size=T.TITLE_SIZE, bold=False,
             colour=T.PURPLE, alignment=PP_ALIGN.CENTER)


def make_prior_knowledge(prs: Presentation, topic_name: str,
                         prior: list[str]) -> None:
    """Prior knowledge recap slide."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
             text="Prior Knowledge — What do you already know?",
             font_size=T.HEADING_SIZE, bold=True,
             colour=T.PURPLE, underline=True)

    text = "\n".join(f"•  {p}" for p in prior)
    _textbox(slide, Inches(0.4), Inches(1.5), Inches(9.2), Inches(5.5),
             text=text, font_size=Pt(17), colour=T.BLACK, word_wrap=True)


def make_extension(prs: Presentation, topic_name: str,
                   heading: str, tasks: list[str]) -> None:
    """Extension task slide."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
             text=f"Extension: {heading}",
             font_size=T.HEADING_SIZE, bold=True,
             colour=T.ORANGE, underline=True)

    text = "\n\n".join(f"•  {t}" for t in tasks)
    _coloured_box(slide,
                  Inches(0.4), Inches(1.5),
                  Inches(9.2), Inches(5.5),
                  RGBColor(0xFF, 0xF8, 0xE7),
                  text=text, text_colour=T.BLACK,
                  font_size=Pt(16), alignment=PP_ALIGN.LEFT)


# ─────────────────────────────────────────────
#  New structured slide sequence (2025 overhaul)
# ─────────────────────────────────────────────

def make_starter_plus(prs: Presentation, topic_name: str,
                      questions: list[str], answers: list[str] = None) -> None:
    """4-question starter in cross/plus quadrant layout.
    Pass answers to render the answers version of the slide.
    """
    TEAL_LIGHT = RGBColor(0xD1, 0xF2, 0xEB)

    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    heading = "Starter — Answers" if answers else "Starter"
    _textbox(slide, Inches(0.2), Inches(0.9), Inches(9.6), Inches(0.32),
             text=heading, font_size=T.HEADING_SIZE, bold=True,
             colour=T.PURPLE, underline=True, word_wrap=False)

    # Cross dividers
    _coloured_box(slide, Inches(4.88), Inches(1.28), Inches(0.12), Inches(6.1), T.PURPLE)
    _coloured_box(slide, Inches(0.15), Inches(4.3), Inches(9.73), Inches(0.12), T.PURPLE)

    positions = [
        (Inches(0.18), Inches(1.3)),   # Q1 top-left
        (Inches(5.08), Inches(1.3)),   # Q2 top-right
        (Inches(0.18), Inches(4.5)),   # Q3 bottom-left
        (Inches(5.08), Inches(4.5)),   # Q4 bottom-right
    ]
    box_w = Inches(4.6)
    heights = [Inches(2.88), Inches(2.88), Inches(2.88), Inches(2.88)]

    q_list = (list(questions) + [""] * 4)[:4]
    a_list = (list(answers) if answers else []) + [""] * 4

    for i, ((lft, top), h) in enumerate(zip(positions, heights)):
        _coloured_box(slide, lft, top, box_w, h, T.PURPLE_LIGHT)

        # Number badge
        _coloured_box(slide,
                      lft + Inches(0.08), top + Inches(0.07),
                      Inches(0.38), Inches(0.34),
                      T.PURPLE,
                      text=str(i + 1), text_colour=T.WHITE,
                      font_size=Pt(14), bold=True)

        body = q_list[i]
        if answers and i < len(answers) and a_list[i]:
            body = f"{q_list[i]}\n\nAnswer: {a_list[i]}"

        _textbox(slide,
                 lft + Inches(0.55), top + Inches(0.1),
                 box_w - Inches(0.65), h - Inches(0.2),
                 text=body, font_size=Pt(15), colour=T.BLACK, word_wrap=True)


def make_learning_intro(prs: Presentation, topic_name: str,
                        objective: str, objective_num: int) -> None:
    """Objective introduction slide — what we're learning and why."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    # Purple objective banner
    _coloured_box(slide,
                  Inches(0.2), Inches(0.95),
                  Inches(9.6), Inches(0.75),
                  T.PURPLE,
                  text=f"Objective {objective_num}",
                  font_size=Pt(22), bold=True, alignment=PP_ALIGN.CENTER)

    # Objective text box
    _coloured_box(slide,
                  Inches(0.2), Inches(1.8),
                  Inches(9.6), Inches(1.5),
                  T.PURPLE_LIGHT,
                  text=objective,
                  text_colour=T.BLACK, font_size=Pt(18),
                  alignment=PP_ALIGN.LEFT)

    # Success criteria heading
    _textbox(slide, Inches(0.25), Inches(3.45), Inches(9.5), Inches(0.42),
             text="By the end of this lesson you will be able to:",
             font_size=Pt(16), bold=True, colour=T.PURPLE)

    # Success criteria box
    criteria = (
        f"• {objective}\n\n"
        "• Show all working clearly, step by step\n\n"
        "• Apply this skill with increasing confidence across a range of question types"
    )
    _coloured_box(slide,
                  Inches(0.25), Inches(3.95),
                  Inches(9.5), Inches(3.35),
                  RGBColor(0xF5, 0xF0, 0xFF),
                  text=criteria,
                  text_colour=T.BLACK, font_size=Pt(16),
                  alignment=PP_ALIGN.LEFT)


def make_ido_slide(prs: Presentation, topic_name: str,
                   heading: str, worked_example: str,
                   notes: str = "") -> None:
    """I Do — teacher-led worked example."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)
    _phase_badge(slide, "I Do")

    _textbox(slide, Inches(1.5), Inches(0.88), Inches(8.2), Inches(0.45),
             text=heading, font_size=T.HEADING_SIZE, bold=True,
             colour=T.BLACK, underline=True)

    if notes:
        _textbox(slide, Inches(0.3), Inches(1.45), Inches(5.7), Inches(5.85),
                 text=worked_example, font_size=Pt(16),
                 colour=T.BLACK, word_wrap=True)
        _coloured_box(slide,
                      Inches(6.15), Inches(1.45),
                      Inches(3.55), Inches(5.85),
                      T.PURPLE_LIGHT,
                      text=notes, text_colour=T.BLACK,
                      font_size=Pt(13), alignment=PP_ALIGN.LEFT)
    else:
        _textbox(slide, Inches(0.3), Inches(1.45), Inches(9.4), Inches(5.85),
                 text=worked_example, font_size=Pt(17),
                 colour=T.BLACK, word_wrap=True)


def make_wedo_slide(prs: Presentation, topic_name: str,
                    heading: str, question: str,
                    scaffold_steps: list[str] = None) -> None:
    """We Do — guided practice with scaffold step boxes."""
    TEAL_LIGHT = RGBColor(0xD1, 0xF2, 0xEB)

    slide = _blank_slide(prs)
    _add_header(slide, topic_name)
    _phase_badge(slide, "We Do")

    _textbox(slide, Inches(1.5), Inches(0.88), Inches(8.2), Inches(0.45),
             text=heading, font_size=T.HEADING_SIZE, bold=True,
             colour=T.BLACK, underline=True)

    _coloured_box(slide,
                  Inches(0.3), Inches(1.45),
                  Inches(9.4), Inches(1.5),
                  TEAL_LIGHT,
                  text=question, text_colour=T.BLACK,
                  font_size=Pt(17), alignment=PP_ALIGN.LEFT)

    steps = (scaffold_steps or [
        "Step 1: What are we finding? Identify the key information.",
        "Step 2: Write the method / rule before substituting.",
        "Step 3: Substitute and calculate — show every line.",
        "Step 4: Check — does the answer make sense?",
    ])[:4]

    step_positions = [
        (Inches(0.3),  Inches(3.1)),
        (Inches(5.05), Inches(3.1)),
        (Inches(0.3),  Inches(5.2)),
        (Inches(5.05), Inches(5.2)),
    ]
    for step_text, (lft, top) in zip(steps, step_positions):
        _coloured_box(slide, lft, top, Inches(4.6), Inches(2.0),
                      T.PURPLE_LIGHT,
                      text=step_text, text_colour=T.BLACK,
                      font_size=Pt(14), alignment=PP_ALIGN.LEFT)


def make_youdo_slide(prs: Presentation, topic_name: str,
                     heading: str, question: str,
                     answer: str = "") -> None:
    """You Do — student solo attempt with large working space."""
    ORANGE_LIGHT = RGBColor(0xFF, 0xF3, 0xCD)

    slide = _blank_slide(prs)
    _add_header(slide, topic_name)
    _phase_badge(slide, "You Do")

    _textbox(slide, Inches(1.5), Inches(0.88), Inches(8.2), Inches(0.45),
             text=heading, font_size=T.HEADING_SIZE, bold=True,
             colour=T.BLACK, underline=True)

    _coloured_box(slide,
                  Inches(0.3), Inches(1.45),
                  Inches(9.4), Inches(1.45),
                  ORANGE_LIGHT,
                  text=question, text_colour=T.BLACK,
                  font_size=Pt(17), alignment=PP_ALIGN.LEFT)

    # Working space
    _coloured_box(slide,
                  Inches(0.3), Inches(3.05),
                  Inches(9.4), Inches(3.9),
                  T.WHITE,
                  border_colour=T.ORANGE, border_pt=1.5)

    _textbox(slide, Inches(0.3), Inches(7.05), Inches(9.4), Inches(0.38),
             text="Show all of your working in your book.",
             font_size=Pt(13), colour=T.DARK_GREY, italic=True)

    if answer:
        _textbox(slide, Inches(0.3), Inches(7.1), Inches(9.4), Inches(0.35),
                 text=f"Answer: {answer}",
                 font_size=Pt(11), colour=RGBColor(0xBB, 0xBB, 0xBB),
                 alignment=PP_ALIGN.RIGHT)


def make_mini_whiteboard(prs: Presentation, topic_name: str,
                         question: str, question_num: int = None,
                         total: int = 10) -> None:
    """Mini whiteboard question slide — one question, large display area."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    counter = f"  ({question_num}/{total})" if question_num else ""
    _coloured_box(slide,
                  Inches(0.2), Inches(0.88),
                  Inches(9.6), Inches(0.55),
                  T.TEAL,
                  text=f"Mini Whiteboard{counter}",
                  text_colour=T.WHITE, font_size=Pt(20), bold=True)

    # White whiteboard area
    _coloured_box(slide,
                  Inches(0.5), Inches(1.6),
                  Inches(9.0), Inches(5.15),
                  T.WHITE,
                  text=question, text_colour=T.BLACK,
                  font_size=Pt(26), alignment=PP_ALIGN.CENTER,
                  border_colour=T.TEAL, border_pt=2.0)

    _textbox(slide, Inches(0.5), Inches(6.85), Inches(9.0), Inches(0.42),
             text="Show me your answer on your mini whiteboard.",
             font_size=Pt(13), colour=T.DARK_GREY, italic=True,
             alignment=PP_ALIGN.CENTER)


def make_independent_practice(prs: Presentation, topic_name: str,
                               questions: list[str]) -> None:
    """Independent practice slide with up to 10 numbered questions in two columns."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _coloured_box(slide,
                  Inches(0.2), Inches(0.88),
                  Inches(9.6), Inches(0.55),
                  T.ORANGE,
                  text="Independent Practice",
                  text_colour=T.WHITE, font_size=Pt(20), bold=True)

    qs = list(questions)[:10]
    mid = (len(qs) + 1) // 2
    left_qs  = qs[:mid]
    right_qs = qs[mid:]

    left_text = "\n\n".join(f"{i + 1}.  {q}" for i, q in enumerate(left_qs))
    _textbox(slide, Inches(0.25), Inches(1.6), Inches(4.65), Inches(5.65),
             text=left_text, font_size=Pt(14), colour=T.BLACK, word_wrap=True)

    if right_qs:
        right_text = "\n\n".join(
            f"{i + mid + 1}.  {q}" for i, q in enumerate(right_qs)
        )
        _textbox(slide, Inches(5.1), Inches(1.6), Inches(4.65), Inches(5.65),
                 text=right_text, font_size=Pt(14), colour=T.BLACK, word_wrap=True)

    # Vertical divider between columns
    if right_qs:
        _coloured_box(slide, Inches(5.0), Inches(1.6), Inches(0.05), Inches(5.65),
                      T.PURPLE_LIGHT)


def make_independent_answers(prs: Presentation, topic_name: str,
                              questions: list[str],
                              answers: list[str]) -> None:
    """Answers slide for independent practice."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _coloured_box(slide,
                  Inches(0.2), Inches(0.88),
                  Inches(9.6), Inches(0.55),
                  T.ORANGE,
                  text="Independent Practice — Answers",
                  text_colour=T.WHITE, font_size=Pt(20), bold=True)

    qs  = list(questions)[:10]
    ans = (list(answers) + ["?"] * 10)[:len(qs)]
    mid = (len(qs) + 1) // 2

    left_text = "\n\n".join(
        f"{i + 1}.  {ans[i]}" for i in range(min(mid, len(ans)))
    )
    _textbox(slide, Inches(0.25), Inches(1.6), Inches(4.65), Inches(5.65),
             text=left_text, font_size=Pt(14), colour=T.BLACK, word_wrap=True)

    if mid < len(qs):
        right_text = "\n\n".join(
            f"{i + mid + 1}.  {ans[i + mid]}"
            for i in range(len(qs) - mid)
        )
        _textbox(slide, Inches(5.1), Inches(1.6), Inches(4.65), Inches(5.65),
                 text=right_text, font_size=Pt(14), colour=T.BLACK, word_wrap=True)

    if mid < len(qs):
        _coloured_box(slide, Inches(5.0), Inches(1.6), Inches(0.05), Inches(5.65),
                      T.PURPLE_LIGHT)


def make_plenary(prs: Presentation, topic_name: str,
                 objective: str, summary: str,
                 question: str, answer: str = "") -> None:
    """Plenary slide — lesson summary and final mini whiteboard check."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _coloured_box(slide,
                  Inches(0.2), Inches(0.88),
                  Inches(9.6), Inches(0.55),
                  T.PURPLE,
                  text="Plenary",
                  text_colour=T.WHITE, font_size=Pt(20), bold=True)

    _coloured_box(slide,
                  Inches(0.2), Inches(1.55),
                  Inches(9.6), Inches(2.0),
                  T.PURPLE_LIGHT,
                  text=summary, text_colour=T.BLACK,
                  font_size=Pt(15), alignment=PP_ALIGN.LEFT)

    _textbox(slide, Inches(0.25), Inches(3.65), Inches(9.5), Inches(0.42),
             text="Now show me on your whiteboard:",
             font_size=Pt(16), bold=True, colour=T.PURPLE)

    _coloured_box(slide,
                  Inches(0.25), Inches(4.15),
                  Inches(9.5), Inches(2.5),
                  T.WHITE,
                  text=question, text_colour=T.BLACK,
                  font_size=Pt(22), alignment=PP_ALIGN.CENTER,
                  border_colour=T.PURPLE, border_pt=2.0)

    if answer:
        _textbox(slide, Inches(0.25), Inches(6.75), Inches(9.5), Inches(0.55),
                 text=f"Answer: {answer}",
                 font_size=Pt(12), colour=T.DARK_GREY, italic=True)
