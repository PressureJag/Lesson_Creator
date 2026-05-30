# Lesson Creator — Claude Code Context

## What this is
A local Python tool that generates PowerPoint lesson decks for **Outwood Grange Academies Trust** from Scheme of Work (SoW) PDFs. The teacher provides two PDFs per topic and the tool outputs an 80–100 slide PPTX covering all objectives in the school's visual theme and pedagogical structure.

## How to run

```bash
# Demo mode — no API key needed, uses stub content to check structure/layout
python3 generate_lesson.py \
  --summary "Examples/SOW/<Topic> - Core Plus Summary of Intent.pdf" \
  --methods "Examples/SOW/<Topic> - Common Methods.pdf" \
  --topic "<Topic Name> Core Plus" \
  --output "Output/<Topic>.pptx"

# Full generation — requires ANTHROPIC_API_KEY set in environment
export ANTHROPIC_API_KEY="sk-ant-..."
python3 generate_lesson.py --summary ... --methods ... --topic ...
```

- Use `python3`, not `python` (python is not on PATH on this machine)
- Output saves to `Output/` by default if `--output` is omitted
- Demo mode activates automatically when `ANTHROPIC_API_KEY` is not set — no flag needed

## Key files

| File | Purpose |
|------|---------|
| `generate_lesson.py` | CLI entry point and slide assembly orchestrator |
| `generator/sow_parser.py` | Parses two-column SOW PDFs using word-level bounding boxes |
| `generator/content_gen.py` | Claude API calls for questions, hooks, worked examples; stubs when no API key |
| `generator/slide_builder.py` | All slide template functions using python-pptx |
| `generator/diagram_gen.py` | Matplotlib diagrams (bar models, number lines, area grids, angle diagrams) |
| `generator/theme.py` | Brand constants — colours, fonts, logo path, layout sizes |
| `assets/outwood_logo.png` | Outwood circular purple spiral logo (extracted from example PPTX) |

## Outwood brand theme

- **Background**: `#FFFFCC` pale yellow — applied to every slide via `_blank_slide()` in `slide_builder.py`
- **Primary colour**: `#5B2C8D` Outwood purple — titles, section dividers, accents
- **Supporting colours**: Orange `#F5A623`, Teal `#17A589`, Pink `#E8A0BF`, Light purple `#D4C5E2`
- **Font**: Calibri
- **Slide size**: 10" × 7.5" (4:3)
- **Every slide has**: Outwood logo top-left, topic title top-centre in purple, purple dot watermark top-right

## Slide structure per objective block

Each objective block starts with a retrieval starter pair, then the teaching sequence:

1. Retrieval starter (questions based on prior knowledge for this objective)
2. Retrieval answers
3. Section divider (full purple banner)
4. Learning objective
5. Hook / real-world context (**all objectives**, not just first 2)
6. Worked example (teaching text)
7. Visual diagram (bar model / number line / area grid / angle — if relevant)
8. What's the Same? What's Different? (WSWT)
9. Practice questions (6 questions, two-column layout)
10. Answers
11. Reasoning task (alternates ASN / open by objective index)
12. Misconception callout (red/green boxes — one per objective, matched by index)

Intro slides (before objective blocks): Title → Prior Knowledge → Vocabulary

**Slide count**: ~13–14 slides per objective. A 5-objective topic → ~61 slides. An 11-objective topic → ~130 slides.

**Methods matching**: `methods_pages = list(methods.values())` — page N is matched to objective N by index first, keyword fallback only if N exceeds the page count.

## SOW PDF format

Each topic has two PDFs:
- **Summary of Intent** (also called "Medium Term Plan"): two-column layout. Left = objectives, prior knowledge, extend, future. Right = notes, misconceptions, vocabulary, personal development.
- **Common Methods** (also called "Consistent Methodology"): one column per page, each page is one worked example / teaching method.

The parser auto-detects the column split point using word bounding boxes — no manual config needed per topic.

## Dependencies

```
python-pptx   pdfplumber   matplotlib   pillow   anthropic
```

Install with: `pip3 install python-pptx pdfplumber matplotlib pillow anthropic`

## Git / what's excluded

- `Examples/` — local only (109MB of PPTX/PDF files), not in git
- `Output/` — generated decks, not in git
- `assets/image*.png` — extracted images from example lessons, not needed, not in git
- Only `assets/outwood_logo.png` is committed

## Live task tracking

`to_do.md` in the project root is a live document tracking outstanding work. Update it whenever new tasks are identified or completed. Sections: 🔴 Must Fix / 🟡 Before First Real Use / 🟢 Quality Improvements / 🔵 Polish / 📋 Completed.

## GitHub remote

`git@github.com:PressureJag/Lesson_Creator.git`

## Known completed fixes (do not re-implement)

- `lines` NameError in `sow_parser.py:222` — fixed; fallback now uses `objectives[0][:60]`
- Yellow `#FFFFCC` background — applied in `_blank_slide()` in `slide_builder.py` via `YELLOW_BG` constant in `theme.py`
- Hook limited to first 2 objectives — removed; hook now runs for every objective
- Retrieval starter shared at top — removed; now per-objective inside the loop
- Methods text matching by keyword — fixed; now index-based (page N → objective N) before keyword fallback
- `python` not on PATH — always use `python3` on this machine
