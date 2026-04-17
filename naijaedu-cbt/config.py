"""
NaijaEdu CBT - Configuration Module
All application-wide constants, paths, and settings.
"""

from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
import os, sys

BASE_DIR      = Path(__file__).parent
HOME_DIR      = Path.home()
RESOURCES_DIR = BASE_DIR / "resources"
STYLESHEET_PATH = RESOURCES_DIR / "styles" / "main.qss"

# Cross-platform data directory
if sys.platform == "win32":
    _appdata = os.environ.get("LOCALAPPDATA") or str(HOME_DIR / "AppData" / "Local")
    DATA_DIR = Path(_appdata) / "NaijaEdu" / "naijaedu-cbt"
elif sys.platform == "darwin":
    DATA_DIR = HOME_DIR / "Library" / "Application Support" / "naijaedu-cbt"
else:
    DATA_DIR = HOME_DIR / ".local" / "share" / "naijaedu-cbt"

DB_PATH = DATA_DIR / "naijaedu.db"

# ─── Application Info ─────────────────────────────────────────────────────────
APP_NAME        = "NaijaEdu CBT"
APP_VERSION     = "1.0.0"
APP_ORG         = "NaijaEdu"

# ─── Window Dimensions ────────────────────────────────────────────────────────
WINDOW_MIN_WIDTH  = 1200
WINDOW_MIN_HEIGHT = 800
WINDOW_DEF_WIDTH  = 1400
WINDOW_DEF_HEIGHT = 900

# ─── JAMB Configuration ───────────────────────────────────────────────────────
JAMB_CONFIG = {
    "total_questions"       : 180,
    "english_questions"     : 60,
    "other_subject_questions": 40,
    "time_limit_minutes"    : 120,
    "options"               : ["A", "B", "C", "D"],
    "pass_mark"             : 50,      # percentage
}

# ─── WAEC Configuration ───────────────────────────────────────────────────────
WAEC_CONFIG = {
    "total_questions"       : 50,
    "time_limit_minutes"    : 180,
    "options"               : ["A", "B", "C", "D", "E"],
    "pass_mark"             : 50,
}

# ─── Subjects ─────────────────────────────────────────────────────────────────
SUBJECTS = {
    "Sciences": [
        "Mathematics",
        "Physics",
        "Chemistry",
        "Biology",
        "Agricultural Science",
    ],
    "Arts": [
        "English Language",
        "Literature in English",
        "Government",
        "Christian Religious Studies",
        "History",
    ],
    "Commercial": [
        "Economics",
        "Commerce",
        "Accounting",
        "Business Studies",
    ],
    "General": [
        "Geography",
        "Civic Education",
    ],
}

# Flat subject list (used in dropdowns, validation, etc.)
ALL_SUBJECTS = [s for category in SUBJECTS.values() for s in category]

# ─── Category Colors ───────────────────────────────────────────────────────────
CATEGORY_COLORS = {
    "Sciences"   : "#3498db",
    "Arts"       : "#9b59b6",
    "Commercial" : "#f39c12",
    "General"    : "#27ae60",
}

# Subject → category lookup
SUBJECT_CATEGORY = {
    subject: category
    for category, subjects in SUBJECTS.items()
    for subject in subjects
}

# ─── Subject Icons (Unicode emoji fallbacks) ──────────────────────────────────
SUBJECT_ICONS = {
    "Mathematics"              : "∑",
    "Physics"                  : "⚛",
    "Chemistry"                : "⚗",
    "Biology"                  : "🧬",
    "Agricultural Science"     : "🌱",
    "English Language"         : "📖",
    "Literature in English"    : "📚",
    "Government"               : "🏛",
    "Christian Religious Studies": "✝",
    "History"                  : "📜",
    "Economics"                : "📈",
    "Commerce"                 : "🛒",
    "Accounting"               : "🧾",
    "Business Studies"         : "💼",
    "Geography"                : "🌍",
    "Civic Education"          : "🗳",
}

# ─── UI Color Palette ─────────────────────────────────────────────────────────
COLORS = {
    "primary"        : "#2c3e50",
    "secondary"      : "#27ae60",
    "accent"         : "#f39c12",
    "danger"         : "#e74c3c",
    "background"     : "#f8f9fa",
    "surface"        : "#ffffff",
    "text_primary"   : "#2c3e50",
    "text_secondary" : "#7f8c8d",
    "border"         : "#e0e0e0",
}

# ─── Timer Thresholds (seconds) ───────────────────────────────────────────────
TIMER_WARNING_THRESHOLD = 10 * 60   # 10 minutes  → orange
TIMER_DANGER_THRESHOLD  =  5 * 60   #  5 minutes  → red + pulse

# ─── Question Palette ─────────────────────────────────────────────────────────
PALETTE_COLUMNS   = 5
PALETTE_BUTTON_SZ = 36      # px

# ─── Auto-save interval ───────────────────────────────────────────────────────
AUTOSAVE_INTERVAL_MS = 30_000   # 30 seconds

# ─── History / Pagination ─────────────────────────────────────────────────────
HISTORY_PAGE_SIZE = 10

# ─── WAEC Grade Boundaries ────────────────────────────────────────────────────
WAEC_GRADES = [
    (75, "A1"),
    (70, "B2"),
    (65, "B3"),
    (60, "C4"),
    (55, "C5"),
    (50, "C6"),
    (45, "D7"),
    (40, "E8"),
    (0,  "F9"),
]


def get_waec_grade(percentage: float) -> str:
    for threshold, grade in WAEC_GRADES:
        if percentage >= threshold:
            return grade
    return "F9"


def get_exam_config(exam_type: str) -> dict:
    """Return config dict for the given exam type."""
    return JAMB_CONFIG if exam_type.upper() == "JAMB" else WAEC_CONFIG


def get_question_limit(exam_type: str, subject: str) -> int:
    """Return how many questions to load for a session."""
    cfg = get_exam_config(exam_type)
    if exam_type.upper() == "JAMB":
        return cfg["english_questions"] if subject == "English Language" else cfg["other_subject_questions"]
    return cfg["total_questions"]


def get_time_limit_seconds(exam_type: str) -> int:
    cfg = get_exam_config(exam_type)
    return cfg["time_limit_minutes"] * 60
