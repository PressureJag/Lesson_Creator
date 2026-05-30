"""Interactive module browser for the Outwood mathematics curriculum."""

import json
import re
import sys
from pathlib import Path
from typing import Optional

from .notification import prompt_choice, notify, header

_MODULES_FILE  = Path(__file__).parent.parent / "Examples/Other Generator scripts/_modules.json"
_MANIFEST_FILE = Path(__file__).parent.parent / "Examples/Other Generator scripts/_manifest_known.json"
_PDF_CACHE     = Path(__file__).parent.parent / "Output" / "pdf_cache"

_STRAND_LABELS = {
    "algebra":    "Algebra",
    "data":       "Data",
    "number":     "Number",
    "proportion": "Proportion",
    "shape":      "Shape",
    "ks4-nurture": "KS4 Nurture",
}

_TIER_LABELS = {
    "core-plus":              "Core Plus",
    "core":                   "Core",
    "extension":              "Extension",
    "nurture":                "Nurture",
    "algebra-nurture-ks4":   "Algebra",
    "data-nurture-ks4":      "Data",
    "number-nurture-ks4":    "Number",
    "proportion-nurture-ks4": "Proportion",
    "shape-nurture-ks4":     "Shape",
}

_TIER_CODES = {
    "cp": "Core Plus",
    "c":  "Core",
    "e":  "Extension",
    "n":  "Nurture",
}

_STRAND_ORDER = ["algebra", "data", "number", "proportion", "shape", "ks4-nurture"]
_TIER_ORDER   = ["nurture", "core", "core-plus", "extension"]


def _load_modules() -> list:
    if not _MODULES_FILE.exists():
        return []
    data = json.loads(_MODULES_FILE.read_text())
    return data.get("modules", [])


def _load_manifest() -> dict:
    if not _MANIFEST_FILE.exists():
        return {}
    data = json.loads(_MANIFEST_FILE.read_text())
    if isinstance(data, list):
        return {}
    return data.get("captured_drive_ids", {})


def _parse_module_url(url: str) -> Optional[dict]:
    m = re.search(r'/modules/([^/]+)/([^/]+)/([^/]+)$', url)
    if not m:
        return None
    strand, tier, module_id = m.group(1), m.group(2), m.group(3)

    # Standard pattern: {strand}-{num}{code}  e.g. algebra-1cp, number-1an, shape-10n
    sm = re.match(r'[a-z]+-(\d+[ab]?)([a-z]+)$', module_id)
    if sm:
        num = sm.group(1)
        code = sm.group(2)
        tier_name = _TIER_CODES.get(code, code.upper())
    else:
        # KS4 Nurture: {strand}-{letter}  e.g. algebra-a, data-b
        km = re.match(r'[a-z-]+-([a-z])$', module_id)
        num = km.group(1).upper() if km else module_id
        tier_name = "Nurture"

    strand_label = _STRAND_LABELS.get(strand, strand.title())
    tier_label   = _TIER_LABELS.get(tier, tier.title())
    display      = f"{strand_label} {num}  ({tier_label})"

    return {
        "url":          url,
        "strand":       strand,
        "tier":         tier,
        "module_id":    module_id,
        "num":          num,
        "tier_name":    tier_name,
        "display":      display,
        "strand_label": strand_label,
        "tier_label":   tier_label,
    }


def _sort_key(p: dict) -> tuple:
    raw = p["num"]
    letter = 0
    if raw and not raw[-1].isdigit() and len(raw) > 1:
        letter = ord(raw[-1])
        raw = raw[:-1]
    try:
        return (int(raw), letter)
    except ValueError:
        return (0, ord(raw[0]) if raw else 0)


def _get_drive_ids(module_url: str, manifest: dict) -> dict:
    module_id = module_url.rstrip('/').split('/')[-1]
    ids = {}
    for suffix, key in [("-mtp", "mtp"), ("-cm", "cm"), ("-i", "interleaving")]:
        sub_url = f"{module_url}/{module_id}{suffix}"
        if sub_url in manifest:
            ids[key] = manifest[sub_url]
    return ids


def _download_pdf(drive_id: str, dest: Path) -> bool:
    try:
        import requests
    except ImportError:
        return False

    if dest.exists() and dest.stat().st_size > 0:
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    base_url = "https://drive.usercontent.google.com/download"
    params = {"id": drive_id, "export": "download"}

    try:
        r = session.get(base_url, params=params, stream=True, allow_redirects=True, timeout=30)
        ctype = r.headers.get("content-type", "")

        if "text/html" in ctype:
            html = r.text
            form_m = re.search(
                r'<form[^>]*action="(https://drive\.usercontent\.google\.com/download)"[^>]*>(.*?)</form>',
                html, re.DOTALL
            )
            if form_m:
                inputs = dict(re.findall(r'<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"', form_m.group(2)))
                if inputs:
                    r = session.get(base_url, params=inputs, stream=True, allow_redirects=True, timeout=30)
                    ctype = r.headers.get("content-type", "")

        if "text/html" in ctype:
            return False

        total = 0
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 15):
                if chunk:
                    fh.write(chunk)
                    total += len(chunk)
        return total > 0
    except Exception:
        return False


def _prompt_pdf_path(label: str, suggestion: str = "") -> Optional[str]:
    print()
    if suggestion:
        print(f"    Hint: try  {suggestion}")
    print(f"  Enter path to {label} PDF (or leave blank to cancel):")
    print("  > ", end="", flush=True)
    path = sys.stdin.readline().strip().strip('"').strip("'")
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        notify(f"File not found: {path}", "warning")
        return None
    return str(p)


def _resolve_pdf(module: dict, drive_ids: dict, pdf_type: str, label: str) -> Optional[str]:
    module_id = module["module_id"]

    if pdf_type in drive_ids:
        cache_path = (
            _PDF_CACHE
            / module["strand"]
            / module["tier"]
            / module_id
            / f"{pdf_type}.pdf"
        )
        if cache_path.exists() and cache_path.stat().st_size > 0:
            notify(f"{label}: using cached PDF", "info")
            return str(cache_path)

        notify(f"Downloading {label} from Google Drive …", "progress")
        if _download_pdf(drive_ids[pdf_type], cache_path):
            notify(f"{label}: downloaded OK", "success")
            return str(cache_path)
        notify("Download failed — please enter the PDF path manually", "warning")

    sow_dir = Path(__file__).parent.parent / "Examples" / "SOW"
    suggestion = f"{sow_dir}/" if sow_dir.exists() else ""
    return _prompt_pdf_path(label, suggestion)


def select_module() -> Optional[dict]:
    """
    Interactive 3-step module browser: Strand → Tier → Module.
    Returns dict with keys: summary_pdf, methods_pdf, topic_name, module
    Returns None if cancelled.
    """
    modules = _load_modules()
    manifest = _load_manifest()

    if not modules:
        notify("Module list not found — use --summary and --methods to specify PDFs", "warning")
        return None

    parsed = [p for p in (_parse_module_url(url) for url in modules) if p]

    strands = [s for s in _STRAND_ORDER if any(p["strand"] == s for p in parsed)]

    while True:
        # ── Step 1: Strand ──────────────────────────────────────
        strand_opts = [
            (
                _STRAND_LABELS.get(s, s.title()),
                f"{sum(1 for p in parsed if p['strand'] == s)} modules",
            )
            for s in strands
        ]
        strand_opts.append(("Cancel", "Return without selecting a module"))

        header("SELECT MODULE", "Browse the Outwood Mathematics curriculum")
        si = prompt_choice("STRAND", strand_opts, default=0, timeout=120)
        if si == len(strands):
            return None
        selected_strand = strands[si]
        strand_mods = [p for p in parsed if p["strand"] == selected_strand]

        tiers = [t for t in _TIER_ORDER if any(p["tier"] == t for p in strand_mods)]

        while True:
            # ── Step 2: Tier ────────────────────────────────────
            tier_opts = [
                (
                    _TIER_LABELS.get(t, t.title()),
                    f"{sum(1 for p in strand_mods if p['tier'] == t)} modules",
                )
                for t in tiers
            ]
            tier_opts.append(("Back", "Choose a different strand"))

            ti = prompt_choice(
                f"TIER  —  {_STRAND_LABELS.get(selected_strand, selected_strand.title())}",
                tier_opts, default=0, timeout=120,
            )
            if ti == len(tiers):
                break  # back to strand selection
            selected_tier = tiers[ti]
            tier_mods = sorted(
                [p for p in strand_mods if p["tier"] == selected_tier],
                key=_sort_key
            )

            while True:
                # ── Step 3: Module number ───────────────────────
                mod_opts = [(p["display"], f"Module {p['num']}") for p in tier_mods]
                mod_opts.append(("Back", "Choose a different tier"))

                mi = prompt_choice(
                    f"MODULE  —  {_STRAND_LABELS.get(selected_strand, selected_strand.title())} "
                    f"({_TIER_LABELS.get(selected_tier, selected_tier)})",
                    mod_opts, default=0, timeout=120,
                )
                if mi == len(tier_mods):
                    break  # back to tier selection

                selected = tier_mods[mi]
                drive_ids = _get_drive_ids(selected["url"], manifest)
                topic_name = (
                    f"{selected['strand_label']} {selected['num']} "
                    f"{selected['tier_label']}"
                )
                notify(f"Module: {selected['display']}", "info")

                summary_pdf = _resolve_pdf(selected, drive_ids, "mtp", "Medium Term Plan (Summary)")
                if not summary_pdf:
                    notify("Summary PDF is required — try again", "warning")
                    continue

                methods_pdf = _resolve_pdf(selected, drive_ids, "cm", "Common Methods")
                if not methods_pdf:
                    notify("Common Methods PDF is required — try again", "warning")
                    continue

                return {
                    "summary_pdf": summary_pdf,
                    "methods_pdf": methods_pdf,
                    "topic_name":  topic_name,
                    "module":      selected,
                }
