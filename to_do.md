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

---

## 🟡 Before First Real Use

- [ ] **"I Do, We Do, You Do" structure** — restructure the worked example section of each objective block into three phases:
  - *I Do*: teacher-led worked example (already exists as `make_teaching_text`)
  - *We Do*: guided practice slide — teacher and students work a problem together
  - *You Do*: independent practice questions (currently `make_practice`)
  Each phase should be clearly labelled on its own slide.

- [ ] **Answer slide for every practice slide** — ensure every slide that presents questions (We Do, You Do, retrieval starter) is immediately followed by a dedicated answers slide. Currently only the main practice and retrieval starters have answer pairs — We Do answers are missing.

- [ ] **Maths-specific enhancements** — review the tool against common secondary maths topics and consider adding:
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

- [ ] **Cleaner terminal output** — replace plain print statements with a progress indicator so it's obvious the tool hasn't hung during API calls (each API call takes 3–10 seconds)

- [ ] **Test all 4 diagram types** — confirm bar model, number line, area grid, and angle diagram all render correctly and appear on the right slide types

- [ ] **Test edge cases**:
  - Topic with no vocabulary section
  - Topic with no misconceptions
  - Topic with a very long objective text (check it doesn't overflow the section divider)

- [ ] **Test on a third topic** (e.g. Shape 6 or Algebra 12) to confirm the parser handles different SOW layouts

---

## 📋 Completed

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
- [x] `requirements.txt` added
- [x] `CLAUDE.md` written with full project context
- [x] Pushed to GitHub: `github.com/PressureJag/Lesson_Creator`
