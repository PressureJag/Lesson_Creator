"""Parse Outwood SOW PDFs into structured data."""

import re
import pdfplumber


DEFAULT_COLUMN_SPLIT = 400  # x-coordinate dividing left and right columns


def _detect_column_split(words: list) -> float:
    """
    Detect the x-coordinate dividing two columns by finding the largest gap
    in word start positions in the content area (y > 70, excluding the title).
    """
    # Only look at content words, not the title row
    content_words = [w for w in words if w["top"] > 70]
    xs = sorted(set(round(w["x0"]) for w in content_words if 80 < w["x0"] < 650))
    if len(xs) < 4:
        return DEFAULT_COLUMN_SPLIT
    best_gap = 0
    best_split = DEFAULT_COLUMN_SPLIT
    for i in range(1, len(xs)):
        gap = xs[i] - xs[i - 1]
        mid = (xs[i - 1] + xs[i]) / 2
        if gap > best_gap and 200 < mid < 500:
            best_gap = gap
            best_split = mid
    return best_split if best_gap > 25 else DEFAULT_COLUMN_SPLIT


def _extract_columns(pdf_path: str) -> tuple[str, str]:
    """
    Extract text from the SOW PDF respecting its two-column layout.
    Returns (left_column_text, right_column_text).
    """
    left_lines = []
    right_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(keep_blank_chars=False)
            col_split = _detect_column_split(words)

            from collections import defaultdict
            left_by_y  = defaultdict(list)
            right_by_y = defaultdict(list)
            for w in words:
                y_key = round(w["top"] / 3) * 3
                if w["x0"] < col_split:
                    left_by_y[y_key].append(w)
                else:
                    right_by_y[y_key].append(w)

            for y in sorted(left_by_y):
                row_words = sorted(left_by_y[y], key=lambda w: w["x0"])
                left_lines.append(" ".join(w["text"] for w in row_words))

            for y in sorted(right_by_y):
                row_words = sorted(right_by_y[y], key=lambda w: w["x0"])
                right_lines.append(" ".join(w["text"] for w in row_words))

    return "\n".join(left_lines), "\n".join(right_lines)


def _full_text(pdf_path: str) -> str:
    """Full text of a PDF (for non-columnar docs like Common Methods)."""
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(keep_blank_chars=False)
            from collections import defaultdict
            by_y = defaultdict(list)
            for w in words:
                y_key = round(w["top"] / 3) * 3
                by_y[y_key].append(w)
            for y in sorted(by_y):
                row = sorted(by_y[y], key=lambda w: w["x0"])
                lines.append(" ".join(w["text"] for w in row))
    return "\n".join(lines)


def _section_from(text: str, header: str, next_headers: list[str]) -> str:
    """Extract a named section, stopping at the next header."""
    pattern = (re.escape(header) + r"\s*\n(.*?)(?="
               + "|".join(re.escape(h) for h in next_headers)
               + r"|\Z)")
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _bullet_list(section_text: str) -> list[str]:
    """Split section text into clean bullet items."""
    items = []
    current = ""
    for line in section_text.split("\n"):
        stripped = line.strip().lstrip("•·-– ").strip()
        if not stripped:
            if current:
                items.append(current)
                current = ""
            continue
        # A new bullet starts if the line begins with a bullet char
        if line.strip() and line.strip()[0] in "•·-–":
            if current:
                items.append(current)
            current = stripped
        else:
            # Continuation of previous item
            current = (current + " " + stripped).strip() if current else stripped

    if current:
        items.append(current)

    return [i for i in items if len(i) > 4]


def _extract_vocab(pdf_path: str) -> list[str]:
    """
    Extract vocabulary terms, splitting the two sub-columns within the right column.
    Vocabulary sub-columns are at approximately x=443 and x=556.
    """
    vocab_terms = []
    in_vocab = False
    stop_headers = {"Personal Development", "Misconceptions", "Notes",
                    "Prior Knowledge", "Core Plus Objectives"}
    VOCAB_SUB_SPLIT = 530  # x boundary between vocab sub-columns

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(keep_blank_chars=False)
            from collections import defaultdict
            by_y = defaultdict(list)
            for w in words:
                by_y[round(w["top"] / 3) * 3].append(w)

            for y in sorted(by_y):
                row_words = sorted(by_y[y], key=lambda w: w["x0"])
                line = " ".join(w["text"] for w in row_words).strip()

                if "Key Vocabulary" in line:
                    in_vocab = True
                    continue
                if in_vocab and any(h in line for h in stop_headers):
                    in_vocab = False
                    continue

                if in_vocab:
                    # Collect words from right column (x > 420) split by sub-column
                    right_words = [w for w in row_words if w["x0"] > 420]
                    left_sub  = [w["text"] for w in right_words if w["x0"] < VOCAB_SUB_SPLIT]
                    right_sub = [w["text"] for w in right_words if w["x0"] >= VOCAB_SUB_SPLIT]
                    for group in [left_sub, right_sub]:
                        term = " ".join(group).strip().lstrip("•·-– ").strip()
                        if term and 1 < len(term) < 35:
                            vocab_terms.append(term)

    return vocab_terms


def parse_summary(pdf_path: str) -> dict:
    """
    Parse a 'Core Plus Summary of Intent' or 'Medium Term Plan' PDF.
    Returns a structured dict.
    """
    left, right = _extract_columns(pdf_path)

    # ── Header info (title, big question, hours) ──────────────
    # Read the top of the page (y < 80) to capture the centred header
    topic = ""
    big_question = ""
    time_hours = 0

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words(keep_blank_chars=False)
        from collections import defaultdict
        top_by_y = defaultdict(list)
        for w in words:
            if w["top"] < 80:
                top_by_y[round(w["top"] / 3) * 3].append(w)
        for y in sorted(top_by_y):
            row = sorted(top_by_y[y], key=lambda w: w["x0"])
            line = " ".join(w["text"] for w in row).strip()
            if re.search(r"Core Plus", line, re.IGNORECASE) and not topic:
                topic = line
            if "?" in line and len(line) > 15 and not big_question:
                big_question = line
            m = re.search(r"(\d+)\s*hours?", line, re.IGNORECASE)
            if m:
                time_hours = int(m.group(1))

    # ── Left column sections ─────────────────────────────────
    left_headers = [
        "Prior Knowledge", "Core Plus Objectives",
        "Opportunities to Extend", "Future Knowledge"
    ]
    right_headers = [
        "Notes", "Misconceptions", "Key Vocabulary", "Personal Development"
    ]

    def lsec(h):
        others = [x for x in left_headers + right_headers if x != h]
        return _section_from(left, h, others)

    def rsec(h):
        others = [x for x in left_headers + right_headers if x != h]
        return _section_from(right, h, others)

    prior       = _bullet_list(lsec("Prior Knowledge"))
    objectives  = _bullet_list(lsec("Core Plus Objectives"))
    extend      = _bullet_list(lsec("Opportunities to Extend"))
    future      = _bullet_list(lsec("Future Knowledge"))
    notes       = _bullet_list(rsec("Notes"))
    misconcs    = _bullet_list(rsec("Misconceptions"))
    vocab_raw   = rsec("Key Vocabulary")
    personal    = _bullet_list(rsec("Personal Development"))

    # Key vocabulary: extracted using bounding boxes to handle two sub-columns
    vocab = _extract_vocab(pdf_path)

    return {
        "topic":              topic or objectives[0][:60] if objectives else "Unknown Topic",
        "big_question":       big_question,
        "time_hours":         time_hours or 6,
        "prior_knowledge":    prior,
        "objectives":         objectives,
        "extend":             extend,
        "future_knowledge":   future,
        "misconceptions":     misconcs,
        "vocabulary":         vocab,
        "personal_development": personal,
        "notes":              notes,
    }


def parse_methods(pdf_path: str) -> dict:
    """
    Parse a 'Common Methods / Consistent Methodology' PDF.
    Returns {page_heading: body_text} for each page.
    """
    results = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(keep_blank_chars=False)
            from collections import defaultdict
            by_y = defaultdict(list)
            for w in words:
                y_key = round(w["top"] / 3) * 3
                by_y[y_key].append(w)

            page_lines = []
            for y in sorted(by_y):
                row = sorted(by_y[y], key=lambda w: w["x0"])
                page_lines.append(" ".join(w["text"] for w in row))

            if not page_lines:
                continue

            heading = page_lines[0].strip()
            body    = "\n".join(page_lines[1:])

            if heading in results:
                results[heading] += "\n" + body
            else:
                results[heading] = body

    return results
