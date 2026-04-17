"""
NaijaEdu CBT - Utility Helpers
"""

from datetime import datetime, timedelta
from typing import Optional


def format_duration(seconds: int) -> str:
    """Convert seconds → 'Xh Ym' or 'Ym Zs'."""
    h, rem = divmod(int(seconds), 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def format_time_hms(seconds: int) -> str:
    """Convert seconds → 'HH:MM:SS'."""
    h, rem = divmod(max(0, int(seconds)), 3600)
    m, s   = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_date(dt_str: Optional[str], fmt: str = "%b %d, %Y") -> str:
    """Parse ISO datetime string and return human-readable date."""
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime(fmt)
    except Exception:
        return str(dt_str)


def percentage_color(pct: float) -> str:
    """Return hex color based on score percentage."""
    if pct >= 70:
        return "#27ae60"
    if pct >= 50:
        return "#f39c12"
    return "#e74c3c"


def score_to_grade(pct: float, exam_type: str) -> str:
    """Return grade string for the given percentage and exam type."""
    from config import get_waec_grade
    if exam_type.upper() == "WAEC":
        return get_waec_grade(pct)
    # JAMB: just return percentage band
    if pct >= 70:
        return "Excellent"
    if pct >= 50:
        return "Pass"
    return "Fail"


def truncate(text: str, max_len: int = 60) -> str:
    """Truncate long text with ellipsis."""
    return text if len(text) <= max_len else text[:max_len - 1] + "…"


def initials_from_name(full_name: str) -> str:
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return full_name[:2].upper() if full_name else "??"
