#!/usr/bin/env python3
"""
Single-slide font demo.
Shows the I Do slide so we can judge Comic Sans sizing before
applying it to a full deck.
Run with:
    python3 generate_font_demo.py
"""

import os
from pptx import Presentation
from generator import slide_builder, diagram_gen, theme as T

OUTPUT = "Output/Font_Demo.pptx"

TOPIC   = "Proportion 7 Core Plus"
HEADING = "18 is 30% of what number?"

EXAMPLE = """\
Find the whole when 18 is 30% of the whole.

Step 1:  Set up the ratio table
         We know: 30% of the whole = 18
         We want: 100% of the whole = ?

Step 2:  Find the multiplier
         Divide by the decimal: ÷ 0.30

Step 3:  Apply to the known value
         18 ÷ 0.30 = 60

Answer:  The whole is 60.

In general: whole = part ÷ (percentage ÷ 100)
"""

METHODS = """\
UNITARY METHOD

Find 1%:
  part ÷ percentage

Find 100%:
  answer × 100

One-step:
  whole = part ÷ decimal

e.g.  18 is 30%:
  18 ÷ 0.30 = 60\
"""

NOTES = (
    "Common error: students multiply instead of divide. "
    "Verify: 30% of 60 = 18 ✓"
)

def main():
    prs = Presentation()
    prs.slide_width  = T.SLIDE_WIDTH
    prs.slide_height = T.SLIDE_HEIGHT

    diagram = diagram_gen.ratio_table(
        "30%", "18",
        "100%", "60",
        "÷ 0.30",
        title="Find the whole",
    )

    slide_builder.make_ido_slide(
        prs, TOPIC,
        HEADING, EXAMPLE,
        method_text=METHODS,
        notes=NOTES,
        diagram=diagram,
    )

    os.makedirs("Output", exist_ok=True)
    prs.save(OUTPUT)
    print(f"  Saved 1 slide → {OUTPUT}")

if __name__ == "__main__":
    main()
