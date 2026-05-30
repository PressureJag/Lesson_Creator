# Content Generation

Source of truth: `generator/content_gen.py`

## API calls per objective

| Step | Function | Model | Max tokens |
|------|----------|-------|-----------|
| Retrieval starter (4 Qs) | `generate_retrieval_questions` | sonnet | 800 |
| I Do / We Do / You Do (1 call) | `generate_teaching_sequence` | opus | 2000 |
| Mini whiteboard ×10 | `generate_mini_whiteboard_questions` | sonnet | 1200 |
| Independent practice ×10 | `generate_independent_practice` | opus | 1800 |
| Plenary | `generate_plenary` | sonnet | 500 |

All calls use a cached system prompt (`cache_control: ephemeral`) so the Outwood teacher persona is not re-billed on every request.

## Demo mode

Activates automatically when `ANTHROPIC_API_KEY` is not set. Every public function has a `_stub_*` fallback that returns realistic placeholder content. Switch programmatically with `content_gen.set_demo_mode(True/False)`.

## Teaching sequence contract

`generate_teaching_sequence` returns one JSON object with three keys:

```
i_do  → { heading, worked_example, notes }
we_do → { heading, question, steps[4], answer }
you_do→ { heading, question, answer }
```

Near-variation rule: all three questions use the same method; only ONE numerical feature changes between them.

## SOW PDF format

Two PDFs per topic:

**Summary of Intent** (Medium Term Plan) — two-column layout:
- Left: objectives, prior knowledge, extend, future links
- Right: notes, misconceptions, vocabulary, personal development
- Parser: `sow_parser.parse_summary()` — auto-detects column split via word bounding boxes

**Common Methods** (Consistent Methodology) — one page per objective:
- Each page = one worked example / school teaching method
- Parser: `sow_parser.parse_methods()` — returns `{page_key: text}` dict; index N → objective N
