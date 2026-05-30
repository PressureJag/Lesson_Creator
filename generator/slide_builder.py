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
                  alignment=PP_ALIGN.CENTER):
    """Add a filled rectangle with optional centred text."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_colour
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
                       notes: str = "") -> None:
    """Teacher-led worked example — text only."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
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
                         right_text: str = "") -> None:
    """Worked example with a diagram on the left, text on the right."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
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
                  two_column: bool = False) -> None:
    """Practice questions slide — lettered list."""
    slide = _blank_slide(prs)
    _add_header(slide, topic_name)

    _textbox(slide, Inches(0.3), Inches(0.9), Inches(9.4), Inches(0.45),
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
