# Outwood Brand Theme

Source of truth: `generator/theme.py`

## Colours

| Constant | Hex | Use |
|----------|-----|-----|
| `PURPLE` | `#5B2C8D` | Primary — titles, badges, banners, dividers |
| `PURPLE_LIGHT` | `#D4C5E2` | Box fills — starter, scaffold steps, intros |
| `TEAL` | `#17A589` | We Do badge, mini whiteboard header |
| `ORANGE` | `#F5A623` | You Do badge, independent practice header |
| `YELLOW_BG` | `#FFFFCC` | Slide background (every slide) |
| `WHITE` | `#FFFFFF` | Whiteboard areas, working space |
| `DARK_GREY` | `#404040` | Footer / teacher-note text |
| `BLACK` | `#000000` | Body text |

Supporting (available but less used): `PURPLE_MID #8E6BD0`, `PINK #E8A0BF`

## Typography & size

- **Font**: Calibri throughout
- **Slide**: 10" × 7.5" (4:3)
- `TITLE_SIZE` = 28pt · `HEADING_SIZE` = 20pt · `BODY_SIZE` = 16pt · `SMALL_SIZE` = 13pt

## Header anatomy (every slide)

Three elements added by `_add_header()`:
1. **Logo** — `assets/outwood_logo.png`, top-left (0.15", 0.10"), 0.85" × 0.85"
2. **Title** — topic name centred in purple, top-centre (1.1", 0.10"), 8.8" × 0.75"
3. **Watermark** — faint purple dot pattern, top-right corner, 3.5" × 3.5"

Content area starts at **y = 0.88"** (below the header zone).
