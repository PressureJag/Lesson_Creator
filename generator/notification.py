"""Terminal notification and interactive choice system for Lesson Creator."""

import select
import sys
import threading
import time

# ANSI codes
_P  = "\033[35m"    # purple
_T  = "\033[36m"    # teal
_O  = "\033[33m"    # orange
_G  = "\033[32m"    # green
_R  = "\033[31m"    # red
_B  = "\033[1m"     # bold
_D  = "\033[2m"     # dim
_X  = "\033[0m"     # reset
_CL = "\r\033[K"    # carriage return + erase to end of line

WIDTH = 62


def _line(char="─", color=_P):
    print(f"{color}{char * WIDTH}{_X}")


def header(title: str, subtitle: str = "", color=_P) -> None:
    print()
    _line("━", color=color)
    print(f"{color}{_B}  {title}{_X}")
    if subtitle:
        print(f"  {_D}{subtitle}{_X}")
    _line("━", color=color)


def notify(message: str, level: str = "info") -> None:
    """Print a formatted progress notification."""
    styles = {
        "info":     ("◆", _P),
        "progress": ("▶", _T),
        "success":  ("✓", _G),
        "warning":  ("⚠", _O),
        "error":    ("✗", _R),
        "section":  ("■", _P),
    }
    icon, color = styles.get(level, ("◆", _P))
    print(f"  {color}{icon}{_X}  {message}")


def prompt_choice(
    title: str,
    options: list,
    default: int = 0,
    timeout: int = 120,
) -> int:
    """
    Print title + numbered options. Return the 0-based index of the chosen option.
    Auto-selects `default` after `timeout` seconds.

    options: list of str  OR  list of (label: str, description: str) tuples.
    """
    print()
    _line(color=_P)
    print(f"{_P}{_B}  {title}{_X}")
    _line(color=_P)
    print()

    for i, opt in enumerate(options):
        if isinstance(opt, tuple):
            label, desc = opt[0], opt[1] if len(opt) > 1 else ""
        else:
            label, desc = opt, ""

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
            prompt_str = (
                f"{_CL}  {_D}Auto-selects {default + 1} in {remaining:3d}s{_X}"
                f"  Enter choice: "
            )
            sys.stdout.write(prompt_str)
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

        label = options[chosen]
        if isinstance(label, tuple):
            label = label[0]
        print(f"  {_G}✓{_X}  Selected: {_B}{label}{_X}")
    else:
        label = options[default]
        if isinstance(label, tuple):
            label = label[0]
        print(f"  {_D}(Timed out — auto-selected: {label}){_X}")

    return chosen
