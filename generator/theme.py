from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor

# Slide dimensions (4:3 standard)
SLIDE_WIDTH = Inches(10)
SLIDE_HEIGHT = Inches(7.5)

# Brand colours
PURPLE      = RGBColor(0x5B, 0x2C, 0x8D)
PURPLE_LIGHT = RGBColor(0xD4, 0xC5, 0xE2)
PURPLE_MID  = RGBColor(0x8E, 0x6B, 0xD0)  # mid lavender accent
ORANGE      = RGBColor(0xF5, 0xA6, 0x23)
TEAL        = RGBColor(0x17, 0xA5, 0x89)
PINK        = RGBColor(0xE8, 0xA0, 0xBF)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
BLACK       = RGBColor(0x00, 0x00, 0x00)
DARK_GREY   = RGBColor(0x40, 0x40, 0x40)
YELLOW_BG   = RGBColor(0xFF, 0xFF, 0xCC)  # Outwood slide background

# Font sizes
TITLE_SIZE   = Pt(28)
HEADING_SIZE = Pt(20)
BODY_SIZE    = Pt(16)
SMALL_SIZE   = Pt(13)

# Font name
FONT_NAME = "Calibri"

# Logo path
import os
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "outwood_logo.png")

# Layout constants (in inches)
LOGO_LEFT   = Inches(0.15)
LOGO_TOP    = Inches(0.10)
LOGO_WIDTH  = Inches(0.85)
LOGO_HEIGHT = Inches(0.85)

TITLE_LEFT   = Inches(1.1)
TITLE_TOP    = Inches(0.10)
TITLE_WIDTH  = Inches(8.8)
TITLE_HEIGHT = Inches(0.75)

CONTENT_TOP  = Inches(1.0)
CONTENT_LEFT = Inches(0.3)
