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
