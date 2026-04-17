"""
NaijaEdu CBT - Data Models
Typed dataclasses representing every database entity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id           : int
    username     : str
    full_name    : str
    password_hash: str          = field(repr=False)
    exam_number  : Optional[str] = None
    email        : Optional[str] = None
    created_at   : Optional[datetime] = None
    last_login   : Optional[datetime] = None

    @property
    def initials(self) -> str:
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        return self.full_name[:2].upper()


@dataclass
class Question:
    id            : int
    exam_type     : str          # 'JAMB' | 'WAEC'
    subject       : str
    question_text : str
    option_a      : str
    option_b      : str
    option_c      : str
    option_d      : str
    correct_option: str          # 'A' | 'B' | 'C' | 'D' | 'E'
    option_e      : Optional[str] = None
    explanation   : Optional[str] = None
    image_path    : Optional[str] = None
    topic         : Optional[str] = None
    difficulty    : Optional[str] = None   # 'Easy' | 'Medium' | 'Hard'
    year          : Optional[int] = None

    def get_options(self) -> dict[str, str]:
        """Return {letter: text} for all non-None options."""
        opts = {
            "A": self.option_a,
            "B": self.option_b,
            "C": self.option_c,
            "D": self.option_d,
        }
        if self.option_e:
            opts["E"] = self.option_e
        return opts


@dataclass
class TestSession:
    id                 : int
    user_id            : int
    exam_type          : str
    subject            : str
    status             : str               # 'In Progress' | 'Completed' | 'Abandoned'
    total_questions    : int   = 0
    correct_answers    : int   = 0
    wrong_answers      : int   = 0
    skipped_questions  : int   = 0
    percentage_score   : float = 0.0
    time_spent_seconds : int   = 0
    score              : Optional[int]      = None
    start_time         : Optional[datetime] = None
    end_time           : Optional[datetime] = None


@dataclass
class Answer:
    id                 : int
    session_id         : int
    question_id        : int
    is_correct         : bool
    selected_option    : Optional[str] = None
    time_spent_seconds : int           = 0
    answered_at        : Optional[datetime] = None


@dataclass
class UserStats:
    id                       : int
    user_id                  : int
    total_tests              : int   = 0
    total_questions_answered : int   = 0
    total_correct            : int   = 0
    total_wrong              : int   = 0
    average_percentage       : float = 0.0
    study_streak             : int   = 0
    best_subject             : Optional[str]      = None
    last_test_date           : Optional[datetime] = None
