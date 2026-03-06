"""
syllabus_parser.py (improved)
─────────────────────────────
Handles multiple syllabus heading formats:
  - Module 1 [8 hrs]           (original format)
  - Module I                   (roman numerals, no hours)
  - MODULE 1:                  (uppercase with colon)
  - Unit 1                     (unit-based syllabi)
  - UNIT I                     (uppercase roman)
"""

import re


def extract_modules_from_syllabus(text: str) -> dict[str, str]:
    """
    Extract topic blocks from a syllabus PDF.

    Returns:
        {
            "Module 1 [8 hrs]": "Introduction to data structures...",
            "Module 2 [10 hrs]": "Stacks, queues...",
            ...
        }
    """

    # ── Strategy 1: Module N [X hrs] or Module N (X hrs) ─────────────────────
    pattern_with_hours = r"(Module\s+\d+\s*[\[\(].*?[\]\)])(.*?)(?=Module\s+\d+\s*[\[\(]|$)"
    matches = re.findall(pattern_with_hours, text, re.DOTALL | re.IGNORECASE)

    if matches:
        return _build_dict(matches)

    # ── Strategy 2: Module N or MODULE N (no hours annotation) ───────────────
    pattern_numbered = r"(MODULE?\s*\d+[:\-]?)(.*?)(?=MODULE?\s*\d+[:\-]?|$)"
    matches = re.findall(pattern_numbered, text, re.DOTALL | re.IGNORECASE)

    if _has_content(matches):
        return _build_dict(matches)

    # ── Strategy 3: Module I / Module II (Roman numerals) ────────────────────
    roman = r"(Module\s+(?:I{1,3}|IV|VI{0,3}|IX|XI{0,2}|XII)[:\-]?)(.*?)(?=Module\s+(?:I{1,3}|IV|VI{0,3}|IX|XI{0,2}|XII)[:\-]?|$)"
    matches = re.findall(roman, text, re.DOTALL | re.IGNORECASE)

    if _has_content(matches):
        return _build_dict(matches)

    # ── Strategy 4: Unit N / UNIT I ──────────────────────────────────────────
    unit_pattern = r"(UNIT\s+(?:\d+|I{1,3}|IV|VI{0,3}|IX)[:\-]?)(.*?)(?=UNIT\s+(?:\d+|I{1,3}|IV|VI{0,3}|IX)[:\-]?|$)"
    matches = re.findall(unit_pattern, text, re.DOTALL | re.IGNORECASE)

    if _has_content(matches):
        return _build_dict(matches)

    # ── Fallback: treat entire text as one block ──────────────────────────────
    return {"Syllabus Content": text.strip()}


def _has_content(matches: list) -> bool:
    """Returns True if at least one match has non-trivial content."""
    return any(content.strip() for _, content in matches)


def _build_dict(matches: list) -> dict[str, str]:
    """Convert regex matches to {header: content} dict, cleaning whitespace."""
    result = {}
    for header, content in matches:
        key = header.strip()
        val = content.strip().replace("\n", " ")
        val = re.sub(r"\s{2,}", " ", val)
        if val:  # skip empty blocks
            result[key] = val
    return result
