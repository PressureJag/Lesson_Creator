# Lesson Creator

Generates PowerPoint lesson decks for **Outwood Grange Academies Trust** from Scheme of Work PDFs. Two PDFs in → 80–100 slide PPTX out, covering all objectives in the Outwood visual theme and pedagogical structure.

## Run

```bash
python3 generate_lesson.py \
  --summary "Examples/SOW/<Topic> - Core Plus Summary of Intent.pdf" \
  --methods "Examples/SOW/<Topic> - Common Methods.pdf" \
  --topic   "<Topic Name> Core Plus"
```

- Always `python3` (not `python` — not on PATH)
- `--output` defaults to `Output/<topic>.pptx`
- Demo mode (stub content, no API cost) activates automatically when `ANTHROPIC_API_KEY` is unset

## Key files

| File | Purpose |
|------|---------|
| `generate_lesson.py` | CLI entry point; orchestrates slide assembly per objective |
| `generator/content_gen.py` | Claude API calls + stub fallbacks |
| `generator/slide_builder.py` | All slide template functions (python-pptx) |
| `generator/sow_parser.py` | Parses Summary of Intent + Common Methods PDFs |
| `generator/theme.py` | Brand constants — colours, fonts, sizes |
| `generator/diagram_gen.py` | Matplotlib diagrams (bar models, number lines, grids) |
| `assets/outwood_logo.png` | Logo used on every slide |

## Brand snapshot

Background `#FFFFCC` · Purple `#5B2C8D` · Teal `#17A589` · Orange `#F5A623` · Font: Calibri · Slide: 10" × 7.5"  
Every slide: logo top-left, topic title top-centre (purple), dot watermark top-right.  
→ Full palette and layout constants: [`docs/brand-theme.md`](docs/brand-theme.md)

## Slide structure

**19 slides per objective**, fixed sequence: Starter → Starter Answers → Learning Intro → I Do → We Do → You Do → Mini Whiteboard ×10 → Independent Practice → Answers → Plenary.  
Intro slides before all objectives: Title → Prior Knowledge → Vocabulary.  
→ Full spec with builder function names: [`docs/slide-structure.md`](docs/slide-structure.md)

## Content generation

5 API calls per objective (retrieval, teaching sequence, whiteboards, independent practice, plenary). Opus for worked examples; Sonnet for everything else.  
→ Full table, demo mode, teaching sequence contract, SOW PDF format: [`docs/content-generation.md`](docs/content-generation.md)

## Project housekeeping

- **Task tracking**: `to_do.md` — update whenever tasks are identified or completed (🔴 Must Fix / 🟡 Before First Use / 🟢 Quality / 🔵 Polish / 📋 Done)
- **Git remote**: `git@github.com:PressureJag/Lesson_Creator.git`
- **Not in git**: `Examples/` (109 MB), `Output/`, `assets/image*.png` — only `assets/outwood_logo.png` is committed
