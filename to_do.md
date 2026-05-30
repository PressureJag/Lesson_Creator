# Lesson Creator — To Do

A live document tracking outstanding work. Updated as new tasks are identified.

---

## 🔴 Must Fix (will break the tool)

- [ ] Nothing currently blocking — all known crash bugs fixed

---

## 🟡 Before First Real Use

- [ ] **Set up Anthropic API key** — get from console.anthropic.com, then:
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  ```
  Once set, the tool automatically switches from stub content to real AI-generated maths

- [ ] **Run first full generation** on Proportion 4 with real API key and open the PPTX:
  ```bash
  python3 generate_lesson.py \
    --summary "Examples/SOW/Proportion 4 - Core Plus Summary of Intent.pdf" \
    --methods "Examples/SOW/Proportion 4 - Common Methods.pdf" \
    --topic "Proportion 4 Core Plus"
  ```

- [ ] **Verify maths quality** — spot-check 3 worked examples for correctness, check practice question answers are right

- [ ] **Test on Algebra 1** (11 objectives, larger topic) to confirm the tool is generic:
  ```bash
  python3 generate_lesson.py \
    --summary "Examples/SOW/Algebra 1 - Core Plus Medium Term Plan.pdf" \
    --methods "Examples/SOW/Algebra 1 - Consistent Methodology.pdf" \
    --topic "Algebra 1 Core Plus"
  ```

- [x] **Maths depth improvements** — content generation prompts updated with:
  - Variation theory in practice questions (a–c vary one feature at a time)
  - Fluency → Reasoning → Problem Solving arc (a–c / d–f / g–h tiers clearly defined)
  - Worked examples require concrete numbers, annotated steps, and generalised method
  - ASN reasoning tasks must have genuinely non-trivial statements (ALWAYS/SOMETIMES/NEVER rules enforced)
  - Open reasoning tasks must be genuine multi-step problem solving (not "explain how")
  - WSWT pairs require a named structural variation and "What changed?" prompt
  - We Do requires near-variation of I Do (same method, same steps, different values only)

- [x] **Content generation overhaul** — `content_gen.py` now uses:
  - Structured outputs (`output_config.format` + JSON schemas) — no more fragile regex parsing
  - `claude-opus-4-8` for accuracy-critical content (worked examples, We Do via teaching_sequence)
  - `claude-haiku-4-5` for formulaic content (retrieval, MWB, independent practice, plenary)
  - Vocabulary and misconceptions threaded into generation prompts for SoW alignment
  - Content JSON export saved alongside PPTX (`Output/<topic>_content.json`) for review

- [x] **Token reduction pass** — ~1,750 fewer input tokens per objective (~8,750 for a 5-obj deck):
  - System prompt compressed from ~150 to ~40 tokens (billed on every call)
  - JSON schema objects removed from the 5 live `_call_json` calls (~650 tokens saved)
  - All 5 active prompts tightened with inline key descriptions instead of verbose bullet blocks
  - `generate_independent_practice` downgraded Sonnet→Haiku (formulaic variation task)
  - Max-token budgets right-sized: retrieval 800→600, MWB 1200→1000, IP 1800→1200, plenary 500→400
  - Methodology diagrams now wired into `build_deck` I Do slides (`build_diagram` called per objective)

- [ ] **Maths-specific enhancements** — further improvements to consider:
  - Fraction / ratio bar models as a default diagram type for proportion topics
  - Algebraic notation rendering (e.g. proper superscript for powers)
  - Times tables / multiplication grid slide type for lower-attaining groups
  - Coordinate grid diagram type for geometry/algebra crossover topics
  - Sentence stems / stem sentences for reasoning slides (common in mastery maths)
  - "Odd one out" task type as an alternative to WSWT

---

## 🟡 Visual Rebuild — match `Examples/Example Slide deck/01_full_sequence_v5.pdf`

Steps 1–8 identified from full template analysis. Work one step at a time, verify in PowerPoint before moving on.

- [x] **Step 1 — Slide dimensions + header** — 16:9 (13.33"×7.5"), OGAT badge + header bar + phase circle badge; no logo, no watermark
- [ ] **Step 2 — 4-card layout** — correct fills (yellow/peach/green/blue), coloured border, "Working..." prompt in amber, 3 dashed lines, thematic icon top-right; answers version: red text + green ✓
- [ ] **Step 3 — Clarity of Learning** — "Topic Question" (pink border) + "Lesson Question" (teal border) + "What it'll look like" (dark border + diagram) + 4 success-criteria chips
- [ ] **Step 4 — I Do** — yellow question banner; left picture panel + right numbered steps (① ②) + green answer bar + dark navy key-idea bar
- [ ] **Step 5 — We Do / You Do difficulty levels** — Easy / Medium / Stretch variants; thin purple teacher-note bar between header and 4-card grid; Stretch badge (olive)
- [ ] **Step 6 — Spot the Mistake + Why** — Bobby (red border, wrong) vs Sara (green border, right) 2-card layout; pink "Turn to your partner" footer bar; Why slide: Bobby's mistake (red X) + Sara's method (green ✓) + dark navy RULE bar
- [ ] **Step 7 — Mixed Retrieval + Exam-style + Coming Next** — Mixed Retrieval (4-card, red Retrieval badge); Exam-style Synoptic (scenario card + 3-part a/b/c columns, Synoptic badge); Exam-style Worked Solutions; Coming Next (full purple background, 4 white topic-preview cards)
- [ ] **Step 8 — Title slide + "Where we're going"** — navy strip top/bottom, central white card, purple pill banner, objective icon row, footer; journey timeline slide with numbered circles

---

## 🟢 Quality Improvements

- [ ] **Visual check** — open generated PPTX alongside `Examples/Example Slide deck/01_full_sequence_v5.pdf` and compare slide-by-slide
- [ ] **Slide layout review** — check for text overflow, unbalanced spacing, or elements outside the slide boundary
- [ ] **Practice questions** — check that 8 questions fit comfortably in two-column layout without overflow

---

## 🔵 Polish (do last)

- [ ] **Add `run.sh` helper script** so the tool can be run with just the topic name:
  ```bash
  ./run.sh "Proportion 4"
  # instead of typing the full --summary / --methods / --topic flags each time
  ```

- [x] **Cleaner terminal output** — replaced plain print statements with a full notification system (`generator/notification.py`)

- [ ] **Test all 4 diagram types** — confirm bar model, number line, area grid, and angle diagram all render correctly and appear on the right slide types

- [ ] **Test edge cases**:
  - Topic with no vocabulary section
  - Topic with no misconceptions
  - Topic with a very long objective text (check it doesn't overflow the section divider)

- [ ] **Test on a third topic** (e.g. Shape 6 or Algebra 12) to confirm the parser handles different SOW layouts

---

## 📋 Completed

- [x] **Visual rebuild Step 1** — 16:9 slide dimensions, OGAT badge + header bar + phase circle badge, 4-card Starter with correct colours/dashed lines, updated all content coordinates; 10 unused legacy functions removed
- [x] **Real-time notification system** — `generator/notification.py` (terminal headers, progress icons, numbered choice prompts with 2-min countdown), `generator/planner.py` (per-objective teaching approach options), `generator/gdrive.py` (auto-upload to Google Drive `Lesson Creator/` folder after generation), startup API confirmation prompt, between-objective checkpoints (continue / skip next / abort)
- [x] Core project structure (`generate_lesson.py`, `generator/` modules)
- [x] SOW PDF parser — two-column auto-detection, handles vocabulary sub-columns
- [x] Outwood brand theme — yellow `#FFFFCC` background, purple `#5B2C8D`, Calibri font
- [x] Demo mode — works without API key, uses realistic stub content
- [x] Diagram generator — bar models, number lines, area grids, angle diagrams
- [x] Per-objective retrieval starter (previously one shared starter at the top)
- [x] Methods text matching fixed — now index-based before keyword fallback
- [x] Fixed `lines` NameError crash in `sow_parser.py`
- [x] Answer slides for all question types follow immediately after questions
- [x] Content generation overhaul — structured outputs, model tiering, caching, SoW alignment
- [x] `requirements.txt` added
- [x] `CLAUDE.md` written with full project context
- [x] Pushed to GitHub: `github.com/PressureJag/Lesson_Creator`
