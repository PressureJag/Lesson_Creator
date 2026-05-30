"""Multi-step startup wizard: year group → ability tier → class rating → scope."""

import select
import sys
import threading
import time

from .notification import header, notify, _P, _G, _B, _D, _X, _CL
from . import class_profile as cp

_WIZARD_STEPS = ["Year group", "Ability tier", "Rating", "Scope"]

_YEAR_GROUPS = ["Year 7", "Year 8", "Year 9", "Year 10", "Year 11"]

_ABILITY_TIERS = [
    ("Nurture",   "Heavy scaffolding, pictorial, one concept per slide"),
    ("Core",      "Balanced representations + notation"),
    ("Core Plus", "Faster pace, extension-style problems"),
    ("Extension", "Deep reasoning, algebraic notation default"),
]

_RATING_BANDS = [
    ("1–4  (lower within tier)", "More I-dos, smaller steps, heavy scaffolding"),
    ("5–7  (standard)",          "Balanced pacing — the typical class"),
    ("8–10 (upper within tier)", "Tighter pacing, more stretch problems, lighter scaffold"),
]

_RATING_GUIDANCE = {
    "1-4": (
        "This class is in the lower band of their tier (rating 1–4). "
        "Use additional step-by-step scaffolding, more worked examples, and simpler numbers. "
        "Break problems into smaller sub-steps and build confidence before extending."
    ),
    "5-7": (
        "This class is in the standard band of their tier (rating 5–7). "
        "Use balanced pacing and the typical difficulty for this pitch."
    ),
    "8-10": (
        "This class is in the upper band of their tier (rating 8–10). "
        "Reduce scaffolding, include more demanding questions, and introduce reasoning tasks early. "
        "Stretch beyond the standard pitch where possible."
    ),
}

_SCOPE_OPTIONS = [
    ("Single lesson  (~20 slides)",  "One objective — fast to build, focused lesson"),
    ("Full sequence  (100+ slides)", "All objectives for the module — complete end-to-end deck"),
]


def _breadcrumb(current_idx: int) -> None:
    parts = []
    for i, step in enumerate(_WIZARD_STEPS):
        if i < current_idx:
            parts.append(f"{_G}✓ {step}{_X}")
        elif i == current_idx:
            parts.append(f"{_P}{_B}▸ {step}{_X}")
        else:
            parts.append(f"{_D}{step}{_X}")
    print(f"\n  ←   {'   '.join(parts)}   →")


def _step(
    step_idx: int,
    question: str,
    options: list,
    default: int = 0,
    timeout: int = 120,
) -> int:
    """Show breadcrumb + question + options. Return 0-based chosen index."""
    _breadcrumb(step_idx)
    print()
    print(f"  {_B}{question}{_X}")
    print()

    for i, opt in enumerate(options):
        label, desc = opt if isinstance(opt, tuple) else (opt, "")
        rec = f"  {_D}← recommended{_X}" if i == default else ""
        print(f"  {_B}{i + 1}{_X}  {label}{rec}")
        if desc:
            print(f"      {_D}{desc}{_X}")

    print()

    deadline = time.time() + timeout
    stop = threading.Event()

    def _tick():
        while not stop.is_set():
            remaining = max(0, int(deadline - time.time()))
            sys.stdout.write(
                f"{_CL}  {_D}Auto-selects {default + 1} in {remaining:3d}s{_X}  Enter choice: "
            )
            sys.stdout.flush()
            if remaining == 0:
                break
            time.sleep(1)

    ticker = threading.Thread(target=_tick, daemon=True)
    ticker.start()

    chosen = default
    try:
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
    except (OSError, ValueError):
        ready = []
    finally:
        stop.set()
        ticker.join(timeout=0.3)
        sys.stdout.write(_CL)
        sys.stdout.flush()

    if ready:
        raw = sys.stdin.readline().strip()
        try:
            n = int(raw) - 1
            if 0 <= n < len(options):
                chosen = n
        except ValueError:
            pass

    label = options[chosen][0] if isinstance(options[chosen], tuple) else options[chosen]
    print(f"  {_G}✓{_X}  {label}")
    return chosen


def run_wizard() -> dict:
    """
    Run the 4-step lesson setup wizard.

    Returns:
      year_group, pitch, pitch_guidance, label,
      rating_band ("1-4" | "5-7" | "8-10"), rating_guidance,
      scope ("single" | "full")
    """
    header("LESSON SETUP", "Four questions to configure this build")

    # Step 0 — Year group
    yi = _step(
        0,
        "What year group are you creating a lesson for?",
        [(yg, "") for yg in _YEAR_GROUPS],
        default=2,  # Year 9
    )
    year_group = _YEAR_GROUPS[yi]

    # Step 1 — Ability tier
    ai = _step(
        1,
        "What ability is it for?",
        _ABILITY_TIERS,
        default=2,  # Core Plus
    )
    pitch = _ABILITY_TIERS[ai][0]
    pitch_guidance = cp._PITCH_GUIDANCE[pitch]

    # Step 2 — Class rating band
    ri = _step(
        2,
        "What level is the group within that tier?",
        _RATING_BANDS,
        default=1,  # 5-7 standard
    )
    band_key = ("1-4", "5-7", "8-10")[ri]
    rating_guidance = _RATING_GUIDANCE[band_key]

    # Step 3 — Scope
    si = _step(
        3,
        "What scope for this build?",
        _SCOPE_OPTIONS,
        default=1,  # Full sequence
    )
    scope = ("single", "full")[si]

    label = f"{year_group} — {pitch}"
    notify(
        f"Setup complete: {label}  |  Rating {band_key}  |  {'Single lesson' if scope == 'single' else 'Full sequence'}",
        "success",
    )

    return {
        "year_group":      year_group,
        "pitch":           pitch,
        "pitch_guidance":  pitch_guidance,
        "label":           label,
        "rating_band":     band_key,
        "rating_guidance": rating_guidance,
        "scope":           scope,
    }
