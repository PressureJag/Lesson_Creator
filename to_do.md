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

- [ ] **Maths-specific enhancements** — further improvements to consider:
  - Fraction / ratio bar models as a default diagram type for proportion topics
  - Algebraic notation rendering (e.g. proper superscript for powers)
  - Times tables / multiplication grid slide type for lower-attaining groups
  - Coordinate grid diagram type for geometry/algebra crossover topics
  - Sentence stems / stem sentences for reasoning slides (common in mastery maths)
  - "Odd one out" task type as an alternative to WSWT

---

## 🟢 Quality Improvements

- [ ] **Visual check** — compare generated PPTX slide-by-side with `Examples/Lessons/Algebra 1 (1).pptx`:
  - Yellow background on all slides
  - Logo top-left, purple title, dot watermark top-right
  - Section dividers match Outwood style
  - Text not overflowing on any slide

- [ ] **Slide layout review** — after opening demo PPTX, note any slides where:
  - Text is too small or too large
  - Content overflows the slide
  - Layout looks unbalanced

- [ ] **Practice questions** — check that 8 questions (a–h) fit comfortably in two-column layout without overflow

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

- [x] **Real-time notification system** — `generator/notification.py` (terminal headers, progress icons, numbered choice prompts with 2-min countdown), `generator/planner.py` (per-objective teaching approach options), `generator/gdrive.py` (auto-upload to Google Drive `Lesson Creator/` folder after generation), startup API confirmation prompt, between-objective checkpoints (continue / skip next / abort)

- [x] Core project structure (`generate_lesson.py`, `generator/` modules)
- [x] SOW PDF parser — two-column auto-detection, handles vocabulary sub-columns
- [x] All 15 slide template functions built and working
- [x] Outwood brand theme — yellow `#FFFFCC` background, purple `#5B2C8D`, Calibri font
- [x] Outwood circular logo on every slide (`assets/outwood_logo.png`)
- [x] Purple dot watermark top-right on every slide
- [x] Demo mode — works without API key, uses realistic stub content
- [x] Diagram generator — bar models, number lines, area grids, angle diagrams
- [x] Per-objective retrieval starter (previously one shared starter at the top)
- [x] Hook slide on every objective (previously first 2 only)
- [x] Methods text matching fixed — now index-based before keyword fallback
- [x] Fixed `lines` NameError crash in `sow_parser.py`
- [x] I Do / We Do / You Do structure — phase badges (purple/teal/orange), We Do scaffold + answers slides
- [x] Answer slides for all question types — retrieval answers, We Do answers, You Do answers all follow immediately
- [x] `requirements.txt` added
- [x] `CLAUDE.md` written with full project context
- [x] Pushed to GitHub: `github.com/PressureJag/Lesson_Creator`
