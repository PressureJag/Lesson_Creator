from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
import os

# ── Slide dimensions ─────────────────────────────────────────────────────────
# 16:9 widescreen (13.33" × 7.5")
SLIDE_WIDTH  = Emu(12192000)
SLIDE_HEIGHT = Inches(7.5)

# ── Brand colours ─────────────────────────────────────────────────────────────
PURPLE       = RGBColor(0x5B, 0x2C, 0x8D)   # I Do / You Do badge, plenary
PURPLE_LIGHT = RGBColor(0xD4, 0xC5, 0xE2)   # light fill (success-criteria chips etc.)
PURPLE_MID   = RGBColor(0x8E, 0x6B, 0xD0)
TEAL         = RGBColor(0x17, 0xA5, 0x89)   # We Do badge, Feedback badge
ORANGE       = RGBColor(0xF5, 0xA6, 0x23)   # Recap & Recall badge
PINK         = RGBColor(0xE5, 0x00, 0x7D)   # Clarity badge, Spot the Mistake footer
NAVY         = RGBColor(0x1B, 0x27, 0x66)   # OGAT text, header borders, body text
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
BLACK        = RGBColor(0x00, 0x00, 0x00)
DARK_GREY    = RGBColor(0x40, 0x40, 0x40)
YELLOW_BG    = RGBColor(0xFF, 0xFF, 0xCC)   # Slide background
RED          = RGBColor(0xCC, 0x00, 0x00)   # Retrieval badge
DARK_RED     = RGBColor(0x7B, 0x1F, 0x1F)   # Spot the Mistake badge

# ── 4-card question-card fills ────────────────────────────────────────────────
CARD_YELLOW  = RGBColor(0xFF, 0xF0, 0x80)   # Q1 top-left   (bright lemon)
CARD_PEACH   = RGBColor(0xFF, 0xCC, 0x99)   # Q2 top-right  (warm peach)
CARD_GREEN   = RGBColor(0xA8, 0xE0, 0xB8)   # Q3 bottom-left (mint green)
CARD_BLUE    = RGBColor(0xA8, 0xD8, 0xF5)   # Q4 bottom-right (powder blue)

# ── Typography ────────────────────────────────────────────────────────────────
FONT_NAME    = "Comic Sans MS"
TITLE_SIZE   = Pt(30)
HEADING_SIZE = Pt(22)
BODY_SIZE    = Pt(18)
SMALL_SIZE   = Pt(14)

# ── Logo path (retained for future use) ───────────────────────────────────────
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "outwood_logo.png")
