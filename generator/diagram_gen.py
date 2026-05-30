"""Generate matplotlib diagrams as PNG bytes for embedding in slides."""

import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def _fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf


def bar_model(parts: list[tuple[float, str, str]], total_label: str = "",
              title: str = "") -> io.BytesIO:
    """
    Horizontal segmented bar model.
    parts: list of (proportion, fill_colour_hex, label) e.g. [(0.5,'#F5A623','50%')]
    """
    fig, ax = plt.subplots(figsize=(6, 1.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    x = 0
    total = sum(p[0] for p in parts)
    for (val, colour, label) in parts:
        w = val / total
        rect = patches.FancyBboxPatch((x, 0.25), w, 0.5,
                                      boxstyle="square,pad=0",
                                      linewidth=1.2, edgecolor="#333333",
                                      facecolor=colour)
        ax.add_patch(rect)
        ax.text(x + w / 2, 0.5, label, ha="center", va="center",
                fontsize=11, fontweight="bold", color="white" if colour not in ("#FFFFFF","#F5F5F5") else "black")
        x += w

    if total_label:
        ax.annotate("", xy=(1, 0.85), xytext=(0, 0.85),
                    arrowprops=dict(arrowstyle="<->", color="#5B2C8D", lw=1.5))
        ax.text(0.5, 0.95, total_label, ha="center", va="bottom",
                fontsize=11, color="#5B2C8D", fontweight="bold")

    if title:
        ax.set_title(title, fontsize=12, color="#5B2C8D", fontweight="bold", pad=4)

    fig.tight_layout(pad=0.3)
    return _fig_to_bytes(fig)


def number_line(lo: float, hi: float,
                intervals: list[tuple[float, float, bool, bool]] = None,
                points: list[tuple[float, bool]] = None,
                title: str = "") -> io.BytesIO:
    """
    Number line diagram.
    intervals: list of (start, end, open_left, open_right)
    points:    list of (value, filled)
    """
    fig, ax = plt.subplots(figsize=(6, 1.4))
    ax.set_xlim(lo - 0.5, hi + 0.5)
    ax.set_ylim(-0.5, 1.0)
    ax.axis("off")

    # Draw line with arrows
    ax.annotate("", xy=(hi + 0.4, 0), xytext=(lo - 0.4, 0),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
    ax.annotate("", xy=(lo - 0.4, 0), xytext=(lo + 0.1, 0),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5))

    # Tick marks and labels
    ticks = range(int(lo), int(hi) + 1)
    for t in ticks:
        ax.plot([t, t], [-0.15, 0.15], color="black", lw=1)
        ax.text(t, -0.38, str(t), ha="center", va="top", fontsize=9)

    # Shaded intervals
    if intervals:
        for (s, e, open_l, open_r) in intervals:
            ax.hlines(0, s, e, colors="#5B2C8D", linewidth=4, alpha=0.7)
            lfc = "white" if open_l else "#5B2C8D"
            rfc = "white" if open_r else "#5B2C8D"
            ax.plot(s, 0, "o", ms=9, color="#5B2C8D", mfc=lfc, mew=2)
            ax.plot(e, 0, "o", ms=9, color="#5B2C8D", mfc=rfc, mew=2)

    if points:
        for (v, filled) in points:
            fc = "#5B2C8D" if filled else "white"
            ax.plot(v, 0, "o", ms=9, color="#5B2C8D", mfc=fc, mew=2)

    if title:
        ax.set_title(title, fontsize=11, color="#5B2C8D", fontweight="bold")

    fig.tight_layout(pad=0.2)
    return _fig_to_bytes(fig)


def area_grid(rows: list[str], cols: list[str],
              cells: list[list[str]], title: str = "") -> io.BytesIO:
    """
    Expansion / multiplication grid.
    rows/cols: header labels.  cells: 2-D list of cell strings.
    """
    nr, nc = len(rows), len(cols)
    fig, ax = plt.subplots(figsize=(max(3, nc * 1.4), max(2, nr * 1.2)))
    ax.set_xlim(-1, nc)
    ax.set_ylim(-1, nr)
    ax.axis("off")
    ax.invert_yaxis()

    colours = ["#D4C5E2", "#E8D5F5", "#F0EAF9", "#EDE3F7"]

    for r in range(nr):
        for c in range(nc):
            colour = colours[(r + c) % len(colours)]
            rect = patches.FancyBboxPatch((c - 0.45, r - 0.45), 0.9, 0.9,
                                          boxstyle="square,pad=0.05",
                                          linewidth=1, edgecolor="#5B2C8D",
                                          facecolor=colour)
            ax.add_patch(rect)
            ax.text(c, r, cells[r][c], ha="center", va="center",
                    fontsize=12, color="#1A1A1A")

    # Column headers
    for c, label in enumerate(cols):
        ax.text(c, -0.65, label, ha="center", va="center",
                fontsize=12, color="#5B2C8D", fontweight="bold")

    # Row headers
    for r, label in enumerate(rows):
        ax.text(-0.65, r, label, ha="center", va="center",
                fontsize=12, color="#5B2C8D", fontweight="bold")

    if title:
        ax.set_title(title, fontsize=12, color="#5B2C8D", fontweight="bold", pad=6)

    fig.tight_layout(pad=0.3)
    return _fig_to_bytes(fig)


def percentage_bar(whole: float, part_pct: float,
                   whole_label: str = "100%", part_label: str = "",
                   title: str = "") -> io.BytesIO:
    """Simple percentage double-bar model (whole on top, part below)."""
    fig, ax = plt.subplots(figsize=(5.5, 1.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    frac = part_pct / 100

    # Whole bar
    rect_w = patches.FancyBboxPatch((0, 0.6), 1.0, 0.3,
                                    boxstyle="square,pad=0", linewidth=1.2,
                                    edgecolor="#5B2C8D", facecolor="#D4C5E2")
    ax.add_patch(rect_w)
    ax.text(0.5, 0.75, f"{whole_label}  →  {whole}", ha="center", va="center",
            fontsize=11, color="#5B2C8D", fontweight="bold")

    # Part bar
    rect_p = patches.FancyBboxPatch((0, 0.15), frac, 0.3,
                                    boxstyle="square,pad=0", linewidth=1.2,
                                    edgecolor="#5B2C8D", facecolor="#F5A623")
    ax.add_patch(rect_p)
    rect_rem = patches.FancyBboxPatch((frac, 0.15), 1 - frac, 0.3,
                                      boxstyle="square,pad=0", linewidth=1.2,
                                      edgecolor="#5B2C8D", facecolor="#EEEEEE")
    ax.add_patch(rect_rem)
    ax.text(frac / 2, 0.3, part_label or f"{part_pct}%", ha="center", va="center",
            fontsize=11, color="white", fontweight="bold")

    if title:
        ax.set_title(title, fontsize=11, color="#5B2C8D", fontweight="bold", pad=4)

    fig.tight_layout(pad=0.3)
    return _fig_to_bytes(fig)


def ratio_table(row1_left, row1_right, row2_left, row2_right,
                multiplier_label: str, title: str = "") -> io.BytesIO:
    """
    2×2 ratio table with flanking curved multiplier arrows (Outwood methodology).
    e.g. ratio_table("100%", "240", "135%", "324", "× 1.35")

    Layout (xlim = -0.6 → 5.0, 5.6 units wide on 5.0" figure = 1.12 u/in):
      Table x: [1.10, 3.80]   arrows at x=1.00 (left) and x=3.90 (right)
      rad=0.35 → left arc bows to x≈0.86; label centred at x=0.45 (right edge ≈0.70) ✓
               → right arc bows to x≈4.04; label centred at x=4.65 (left edge ≈4.40) ✓
    """
    fig, ax = plt.subplots(figsize=(5.0, 2.6))
    ax.set_xlim(-0.6, 5.0)
    ax.set_ylim(0, 2.6)
    ax.axis("off")

    # Cell geometry — table centred, larger cells for readability
    tl_x, tl_y, cw, ch = 1.10, 1.20, 1.35, 0.82
    cells = [
        (tl_x,        tl_y,      cw, ch, str(row1_left),  "#E8D5F5"),
        (tl_x + cw,   tl_y,      cw, ch, str(row1_right), "#D4C5E2"),
        (tl_x,        tl_y - ch, cw, ch, str(row2_left),  "#F0EAF9"),
        (tl_x + cw,   tl_y - ch, cw, ch, str(row2_right), "#EDE3F7"),
    ]
    for (x, y, w, h, val, col) in cells:
        rect = patches.FancyBboxPatch((x, y), w, h,
                                      boxstyle="square,pad=0",
                                      linewidth=1.5, edgecolor="#5B2C8D",
                                      facecolor=col)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, val, ha="center", va="center",
                fontsize=14, fontweight="bold", color="#1B2766")

    # Arrows sit just outside the table edges; rad=0.35 (reduced from 0.45)
    # so the arc bows less and stays well clear of the labels
    top_mid = tl_y + ch / 2        # mid-height of top row
    bot_mid = tl_y - ch + ch / 2   # mid-height of bottom row
    mid_y   = (top_mid + bot_mid) / 2

    ax.annotate("", xy=(1.00, bot_mid), xytext=(1.00, top_mid),
                arrowprops=dict(arrowstyle="-|>", color="#5B2C8D",
                               connectionstyle="arc3,rad=0.35",
                               lw=1.8, mutation_scale=12))
    ax.annotate("", xy=(3.90, bot_mid), xytext=(3.90, top_mid),
                arrowprops=dict(arrowstyle="-|>", color="#5B2C8D",
                               connectionstyle="arc3,rad=-0.35",
                               lw=1.8, mutation_scale=12))

    # Labels with solid white background so they always read clearly
    # Left label centred at x=0.45 — right edge ≈0.70 is left of arc bow ≈0.86 ✓
    # Right label centred at x=4.55 — left edge ≈4.30 is right of arc bow ≈4.04 ✓
    _lkw = dict(ha="center", va="center", fontsize=11, fontweight="bold",
                color="#5B2C8D",
                bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                          edgecolor="#5B2C8D", linewidth=0.8, alpha=1.0))
    ax.text(0.45,  mid_y, multiplier_label, **_lkw)
    ax.text(4.55,  mid_y, multiplier_label, **_lkw)

    if title:
        ax.set_title(title, fontsize=11, color="#5B2C8D", fontweight="bold", pad=3)
    fig.tight_layout(pad=0.25)
    return _fig_to_bytes(fig)


def arrow_flow(original, multiplier_str: str, result,
               orig_label: str = "Original\namount",
               result_label: str = "New\namount",
               title: str = "") -> io.BytesIO:
    """
    Three-shape flow diagram: [original] → [×multiplier] → [result].
    Middle shape is a right-pointing arrow/chevron.
    """
    fig, ax = plt.subplots(figsize=(5.6, 2.0))
    ax.set_xlim(0, 5.6)
    ax.set_ylim(0, 2.0)
    ax.axis("off")

    box_y, box_h = 0.32, 0.80
    mid_y = box_y + box_h / 2

    # Original amount box
    ax.add_patch(patches.FancyBboxPatch(
        (0.10, box_y), 1.45, box_h,
        boxstyle="round,pad=0.04", linewidth=1.5,
        edgecolor="#5B2C8D", facecolor="#D4C5E2"))
    ax.text(0.83, mid_y, str(original),
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#1B2766")
    ax.text(0.83, 1.35, orig_label,
            ha="center", va="center", fontsize=8.5,
            color="#5B2C8D", style="italic")

    # Connecting arrow
    ax.annotate("", xy=(1.80, mid_y), xytext=(1.60, mid_y),
                arrowprops=dict(arrowstyle="-|>", color="#5B2C8D",
                               lw=1.5, mutation_scale=12))

    # Chevron/arrow shape for multiplier
    arr_l, arr_r, arr_pt = 1.82, 3.30, 3.65
    chev_xs = [arr_l, arr_r, arr_pt, arr_r, arr_l]
    chev_ys = [box_y + box_h, box_y + box_h, mid_y, box_y, box_y]
    ax.add_patch(plt.Polygon(list(zip(chev_xs, chev_ys)),
                              facecolor="#F5A623", edgecolor="#5B2C8D",
                              linewidth=1.5))
    ax.text((arr_l + arr_r) / 2, mid_y, multiplier_str,
            ha="center", va="center", fontsize=13, fontweight="bold",
            color="white")
    ax.text((arr_l + arr_r) / 2, 1.35, "Multiplier",
            ha="center", va="center", fontsize=8.5,
            color="#5B2C8D", style="italic")

    # Connecting arrow
    ax.annotate("", xy=(3.90, mid_y), xytext=(3.68, mid_y),
                arrowprops=dict(arrowstyle="-|>", color="#5B2C8D",
                               lw=1.5, mutation_scale=12))

    # New amount box
    ax.add_patch(patches.FancyBboxPatch(
        (3.92, box_y), 1.45, box_h,
        boxstyle="round,pad=0.04", linewidth=1.5,
        edgecolor="#5B2C8D", facecolor="#A8E0B8"))
    ax.text(4.65, mid_y, str(result),
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#1B2766")
    ax.text(4.65, 1.35, result_label,
            ha="center", va="center", fontsize=8.5,
            color="#5B2C8D", style="italic")

    if title:
        ax.set_title(title, fontsize=11, color="#5B2C8D", fontweight="bold", pad=3)
    fig.tight_layout(pad=0.2)
    return _fig_to_bytes(fig)


def percentage_number_line(amount, pct_change: float,
                           increase: bool = True, title: str = "") -> io.BytesIO:
    """
    Percentage number line (Outwood methodology style).
    Shows original amount at 100%, with green bar and coloured extension/reduction.
    """
    fig, ax = plt.subplots(figsize=(5.6, 1.9))
    ax.set_xlim(0, 5.6)
    ax.set_ylim(0, 1.9)
    ax.axis("off")

    bx, bw, by, bh = 0.35, 4.90, 0.70, 0.52

    if increase:
        total = 100 + pct_change
        f100 = 100 / total

        # Green bar to 100%
        ax.add_patch(patches.FancyBboxPatch(
            (bx, by), bw * f100, bh,
            boxstyle="square,pad=0", linewidth=1, edgecolor="#2D6A2D",
            facecolor="#4A8C4A"))
        # Orange extension
        ax.add_patch(patches.FancyBboxPatch(
            (bx + bw * f100, by), bw * (1 - f100), bh,
            boxstyle="square,pad=0", linewidth=1, edgecolor="#C67A00",
            facecolor="#F5A623"))
        ax.text(bx + bw * f100 + bw * (1 - f100) / 2, by + bh / 2,
                f"+{pct_change:.4g}%", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

        dot_x = bx + bw * f100
        ax.text(dot_x, by + bh + 0.22, str(amount),
                ha="center", va="bottom", fontsize=12, fontweight="bold",
                color="#1B2766")
        ax.plot(dot_x, by + bh, "o", color="#333333", ms=6, zorder=5)

        ax.text(bx,          by - 0.12, "0%",              ha="center", va="top", fontsize=9, color="#555555")
        ax.text(dot_x,       by - 0.12, "100%",            ha="center", va="top", fontsize=9, color="#2D6A2D", fontweight="bold")
        ax.text(bx + bw,     by - 0.12, f"{total:.4g}%",  ha="center", va="top", fontsize=9, color="#C67A00", fontweight="bold")
    else:
        remain_pct = 100 - pct_change
        f_rem = remain_pct / 100

        # Green bar for remaining portion
        ax.add_patch(patches.FancyBboxPatch(
            (bx, by), bw * f_rem, bh,
            boxstyle="square,pad=0", linewidth=1, edgecolor="#2D6A2D",
            facecolor="#4A8C4A"))
        # Red section for the decrease
        ax.add_patch(patches.FancyBboxPatch(
            (bx + bw * f_rem, by), bw * (1 - f_rem), bh,
            boxstyle="square,pad=0", linewidth=1, edgecolor="#900000",
            facecolor="#CC3333"))
        ax.text(bx + bw * f_rem + bw * (1 - f_rem) / 2, by + bh / 2,
                f"-{pct_change:.4g}%", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

        dot_x = bx + bw * f_rem
        ax.text(bx + bw, by + bh + 0.22, str(amount),
                ha="center", va="bottom", fontsize=12, fontweight="bold",
                color="#1B2766")
        ax.plot(dot_x, by + bh, "o", color="#333333", ms=6, zorder=5)

        ax.text(bx,          by - 0.12, "0%",                    ha="center", va="top", fontsize=9, color="#555555")
        ax.text(dot_x,       by - 0.12, f"{remain_pct:.4g}%",   ha="center", va="top", fontsize=9, color="#CC3333", fontweight="bold")
        ax.text(bx + bw,     by - 0.12, "100%",                  ha="center", va="top", fontsize=9, color="#2D6A2D", fontweight="bold")

    if title:
        ax.set_title(title, fontsize=11, color="#5B2C8D", fontweight="bold", pad=3)
    fig.tight_layout(pad=0.25)
    return _fig_to_bytes(fig)


def part_whole_bar(whole_label, n_parts: int,
                   part_label: str = "", highlight_n: int = 1,
                   title: str = "") -> io.BytesIO:
    """
    Part-whole bar (Outwood methodology style).
    Bar divided into n_parts equal segments; a double-headed brace labels the
    whole above and optionally a highlighted subset below.
    """
    fig, ax = plt.subplots(figsize=(5.6, 2.4))
    ax.set_xlim(0, 5.6)
    ax.set_ylim(0, 2.4)
    ax.axis("off")

    bx, bw, by, bh = 0.35, 4.90, 0.80, 0.58
    seg_w = bw / n_parts
    font_sz = max(7, 12 - n_parts // 3)

    colours = ["#5B2C8D", "#A87BC8"]  # highlighted vs remaining

    for i in range(n_parts):
        x = bx + i * seg_w
        col = colours[0] if i < highlight_n else colours[1]
        ax.add_patch(patches.FancyBboxPatch(
            (x, by), seg_w, bh,
            boxstyle="square,pad=0",
            linewidth=1.5, edgecolor="#333333", facecolor=col))
        pct = 100 // n_parts
        ax.text(x + seg_w / 2, by + bh / 2, f"{pct}%",
                ha="center", va="center",
                fontsize=font_sz, fontweight="bold", color="white")

    # Double-headed arrow above — whole label
    brace_y_top = by + bh + 0.14
    ax.annotate("", xy=(bx + bw, brace_y_top), xytext=(bx, brace_y_top),
                arrowprops=dict(arrowstyle="<->", color="#1B2766", lw=1.5))
    ax.text(bx + bw / 2, brace_y_top + 0.17, str(whole_label),
            ha="center", va="bottom", fontsize=13, fontweight="bold",
            color="#1B2766")

    # Double-headed arrow below — part label
    if part_label:
        brace_y_bot = by - 0.14
        hi_right = bx + highlight_n * seg_w
        ax.annotate("", xy=(hi_right, brace_y_bot), xytext=(bx, brace_y_bot),
                    arrowprops=dict(arrowstyle="<->", color="#5B2C8D", lw=1.5))
        ax.text((bx + hi_right) / 2, brace_y_bot - 0.14, str(part_label),
                ha="center", va="top", fontsize=11, fontweight="bold",
                color="#5B2C8D")

    if title:
        ax.set_title(title, fontsize=11, color="#5B2C8D", fontweight="bold", pad=3)
    fig.tight_layout(pad=0.25)
    return _fig_to_bytes(fig)


def angle_diagram(angle_type: str = "alternate") -> io.BytesIO:
    """Simple parallel lines angle diagram."""
    fig, ax = plt.subplots(figsize=(4, 3.5))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.axis("off")

    # Two parallel horizontal lines
    ax.hlines([1, 3], 0.2, 3.8, colors="#333333", linewidth=2)
    # Transversal
    ax.plot([0.8, 3.2], [0.2, 3.8], color="#333333", linewidth=2)

    if angle_type == "alternate":
        # Mark alternate angles
        from matplotlib.patches import Arc
        ax.add_patch(Arc((1.4, 1), 0.5, 0.5, angle=0, theta1=50, theta2=110,
                         color="#5B2C8D", lw=2))
        ax.add_patch(Arc((2.6, 3), 0.5, 0.5, angle=0, theta1=230, theta2=290,
                         color="#5B2C8D", lw=2))
        ax.text(1.05, 1.25, "a", fontsize=13, color="#5B2C8D", fontweight="bold")
        ax.text(2.9, 2.75, "a", fontsize=13, color="#5B2C8D", fontweight="bold")
        ax.text(2, 0.3, "Alternate angles are equal", ha="center",
                fontsize=10, color="#333333", style="italic")
    elif angle_type == "corresponding":
        from matplotlib.patches import Arc
        ax.add_patch(Arc((1.4, 1), 0.5, 0.5, angle=0, theta1=50, theta2=110,
                         color="#F5A623", lw=2))
        ax.add_patch(Arc((2.2, 3), 0.5, 0.5, angle=0, theta1=50, theta2=110,
                         color="#F5A623", lw=2))
        ax.text(1.05, 1.25, "b", fontsize=13, color="#F5A623", fontweight="bold")
        ax.text(1.85, 3.25, "b", fontsize=13, color="#F5A623", fontweight="bold")
        ax.text(2, 0.3, "Corresponding angles are equal", ha="center",
                fontsize=10, color="#333333", style="italic")

    fig.tight_layout(pad=0.3)
    return _fig_to_bytes(fig)
