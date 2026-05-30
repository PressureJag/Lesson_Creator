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

1. Section divider (full purple banner)
2. Learning objective
3. Hook / real-world context (first 2 objectives only)
4. Worked example (teaching text)
5. Visual diagram (bar model / number line / area grid / angle — if relevant)
6. What's the Same? What's Different? (WSWT)
7. Practice questions (8 graded a–h)
8. Answers
9. Reasoning task (alternates ASN / open)
10. Misconception callout (red/green boxes)

Plus intro slides: Title → Prior Knowledge → Vocabulary → Retrieval Starter → Retrieval Answers

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

## GitHub remote

`git@github.com:PressureJag/Lesson_Creator.git`
