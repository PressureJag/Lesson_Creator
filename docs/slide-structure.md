# Slide Structure — Per-Objective Sequence

19 slides per objective, fixed order. Repeat for every objective in the SoW.

| # | Slide | Builder function | Notes |
|---|-------|-----------------|-------|
| 1 | Starter | `make_starter_plus` | 4 questions in cross/plus layout — PURPLE_LIGHT quadrants, purple divider lines, numbered badges |
| 2 | Starter — Answers | `make_starter_plus(..., answers=[...])` | Same layout; answers appended below each question |
| 3 | Learning Intro | `make_learning_intro` | Purple "Objective N" banner + objective text + success criteria bullets |
| 4 | I Do | `make_ido_slide` | Purple badge; teacher-led worked example with step annotations; optional teacher notes panel (right) |
| 5 | We Do | `make_wedo_slide` | Teal badge; TEAL_LIGHT question box + 4 PURPLE_LIGHT scaffold step boxes in 2×2 grid |
| 6 | You Do | `make_youdo_slide` | Orange badge; ORANGE_LIGHT question box + large white working space; answer in faint grey (teacher ref) |
| 7–16 | Mini Whiteboard 1/10 … 10/10 | `make_mini_whiteboard` | Teal header bar; white bordered whiteboard area; one question per slide; variation-theory order (fluency 1–4, reasoning 5–7, problem-solving 8–10) |
| 17 | Independent Practice | `make_independent_practice` | Orange header; up to 10 numbered questions, 2-column layout |
| 18 | Independent Practice — Answers | `make_independent_answers` | Matching numbered answers |
| 19 | Plenary | `make_plenary` | Purple header; lesson summary box; "Now show me on your whiteboard" + white question area + answer |

## Intro slides (before all objective blocks)

Title → Big Picture → Prior Knowledge → Vocabulary  (`make_title_slide`, `make_overview_slide`, `make_prior_knowledge`, `make_vocabulary`)

`make_overview_slide(prs, topic_name, prior_points, objectives, future_points)` — three-column map: Prior Knowledge (peach) → current module objectives (yellow) → Future Learning (green), with arrows between columns.

## Slide counts

- 5 objectives → 3 + (5 × 19) = **98 slides** ✓ target range 80–100
- 11 objectives → 3 + (11 × 19) = **212 slides**

## Methods matching

`methods_pages = list(methods.values())` — page N is matched to objective N by index. Keyword fallback only when N exceeds the page count.
