"""
NaijaEdu CBT - Database Manager
Handles all SQLite3 operations with proper error handling and connection management.
"""

import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, List, Any

from config import DB_PATH, DATA_DIR


class DatabaseManager:
    """
    Centralised database access layer.
    All public methods return plain Python types (dict / list / int / bool)
    so UI code never imports sqlite3 directly.
    """

    def __init__(self, db_path: Optional[str] = None):
        self._db_path = Path(db_path) if db_path else DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_database()

    # ─── Connection ───────────────────────────────────────────────────────────

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self._db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False,
            )
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.execute("PRAGMA journal_mode = WAL")
        return self._conn

    def _init_database(self) -> None:
        schema_path = Path(__file__).parent / "schema.sql"
        conn = self._get_conn()
        with open(schema_path, "r") as f:
            conn.executescript(f.read())
        conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict:
        return dict(row) if row else {}

    # ─── User Management ──────────────────────────────────────────────────────

    def create_user(
        self,
        username    : str,
        password    : str,
        full_name   : str,
        exam_number : Optional[str] = None,
        email       : Optional[str] = None,
    ) -> int:
        """Hash password and insert user. Returns new user id."""
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn = self._get_conn()
        try:
            cur = conn.execute(
                """INSERT INTO users (username, password_hash, full_name, exam_number, email)
                   VALUES (?, ?, ?, ?, ?)""",
                (username, pw_hash, full_name, exam_number or None, email or None),
            )
            conn.commit()
            # Initialise stats row
            conn.execute(
                "INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)",
                (cur.lastrowid,),
            )
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"User creation failed: {e}") from e

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify credentials. Returns user dict or None."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not row:
            return None
        user = self._row_to_dict(row)
        if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            self.update_last_login(user["id"])
            return user
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        row = self._get_conn().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return self._row_to_dict(row) if row else None

    def update_last_login(self, user_id: int) -> bool:
        conn = self._get_conn()
        conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
        )
        conn.commit()
        return True

    def username_exists(self, username: str) -> bool:
        row = self._get_conn().execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        return row is not None

    def exam_number_exists(self, exam_number: str) -> bool:
        row = self._get_conn().execute(
            "SELECT 1 FROM users WHERE exam_number = ?", (exam_number,)
        ).fetchone()
        return row is not None

    # ─── Question Management ──────────────────────────────────────────────────

    def add_question(self, data: Dict) -> int:
        conn = self._get_conn()
        cur = conn.execute(
            """INSERT INTO questions
               (exam_type, subject, year, question_text,
                option_a, option_b, option_c, option_d, option_e,
                correct_option, explanation, image_path, topic, difficulty)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                data["exam_type"], data["subject"],
                data.get("year"), data["question_text"],
                data.get("option_a"), data.get("option_b"),
                data.get("option_c"), data.get("option_d"),
                data.get("option_e"),
                data["correct_option"], data.get("explanation"),
                data.get("image_path"), data.get("topic"),
                data.get("difficulty", "Medium"),
            ),
        )
        conn.commit()
        return cur.lastrowid

    def get_questions(
        self,
        exam_type : str,
        subject   : str,
        limit     : int = 50,
        year      : Optional[int] = None,
    ) -> List[Dict]:
        conn = self._get_conn()
        if year:
            rows = conn.execute(
                """SELECT * FROM questions
                   WHERE exam_type=? AND subject=? AND year=?
                   ORDER BY RANDOM() LIMIT ?""",
                (exam_type, subject, year, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM questions
                   WHERE exam_type=? AND subject=?
                   ORDER BY RANDOM() LIMIT ?""",
                (exam_type, subject, limit),
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_question_count(
        self,
        exam_type : str,
        subject   : str,
        year      : Optional[int] = None,
    ) -> int:
        conn = self._get_conn()
        if year:
            row = conn.execute(
                "SELECT COUNT(*) FROM questions WHERE exam_type=? AND subject=? AND year=?",
                (exam_type, subject, year),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) FROM questions WHERE exam_type=? AND subject=?",
                (exam_type, subject),
            ).fetchone()
        return row[0] if row else 0

    def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        row = self._get_conn().execute(
            "SELECT * FROM questions WHERE id = ?", (question_id,)
        ).fetchone()
        return self._row_to_dict(row) if row else None

    # ─── Test Session Management ───────────────────────────────────────────────

    def create_test_session(
        self,
        user_id         : int,
        exam_type       : str,
        subject         : str,
        total_questions : int,
    ) -> int:
        conn = self._get_conn()
        cur = conn.execute(
            """INSERT INTO test_sessions (user_id, exam_type, subject, total_questions, status)
               VALUES (?, ?, ?, ?, 'In Progress')""",
            (user_id, exam_type, subject, total_questions),
        )
        conn.commit()
        return cur.lastrowid

    def save_answer(
        self,
        session_id      : int,
        question_id     : int,
        selected_option : Optional[str],
        is_correct      : bool,
        time_spent      : int,
    ) -> bool:
        conn = self._get_conn()
        try:
            # Upsert: remove old answer for this (session, question) then insert
            conn.execute(
                "DELETE FROM answers WHERE session_id=? AND question_id=?",
                (session_id, question_id),
            )
            conn.execute(
                """INSERT INTO answers
                   (session_id, question_id, selected_option, is_correct, time_spent_seconds)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, question_id, selected_option, int(is_correct), time_spent),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    def complete_test_session(
        self,
        session_id  : int,
        score       : int,
        correct     : int,
        wrong       : int,
        skipped     : int,
        percentage  : float,
        time_spent  : int,
    ) -> bool:
        conn = self._get_conn()
        try:
            conn.execute(
                """UPDATE test_sessions SET
                   status='Completed', end_time=CURRENT_TIMESTAMP,
                   score=?, correct_answers=?, wrong_answers=?,
                   skipped_questions=?, percentage_score=?, time_spent_seconds=?
                   WHERE id=?""",
                (score, correct, wrong, skipped, percentage, time_spent, session_id),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    def abandon_test_session(self, session_id: int) -> bool:
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE test_sessions SET status='Abandoned', end_time=CURRENT_TIMESTAMP WHERE id=?",
                (session_id,),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    def get_session_by_id(self, session_id: int) -> Optional[Dict]:
        row = self._get_conn().execute(
            "SELECT * FROM test_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        return self._row_to_dict(row) if row else None

    def get_session_answers(self, session_id: int) -> List[Dict]:
        rows = self._get_conn().execute(
            """SELECT a.*, q.question_text, q.option_a, q.option_b,
                      q.option_c, q.option_d, q.option_e,
                      q.correct_option, q.explanation
               FROM answers a
               JOIN questions q ON a.question_id = q.id
               WHERE a.session_id = ?
               ORDER BY a.id""",
            (session_id,),
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    # ─── History & Stats ──────────────────────────────────────────────────────

    def get_test_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        rows = self._get_conn().execute(
            """SELECT * FROM test_sessions
               WHERE user_id = ? AND status != 'In Progress'
               ORDER BY start_time DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_user_stats(self, user_id: int) -> Dict:
        row = self._get_conn().execute(
            "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not row:
            return {
                "user_id": user_id, "total_tests": 0,
                "total_questions_answered": 0, "total_correct": 0,
                "total_wrong": 0, "average_percentage": 0.0,
                "best_subject": None, "last_test_date": None,
                "study_streak": 0,
            }
        return self._row_to_dict(row)

    def update_user_stats(self, user_id: int, test_data: Dict) -> bool:
        conn = self._get_conn()
        try:
            stats = self.get_user_stats(user_id)
            total_tests    = stats["total_tests"] + 1
            total_q        = stats["total_questions_answered"] + test_data.get("total_questions", 0)
            total_correct  = stats["total_correct"] + test_data.get("correct_answers", 0)
            total_wrong    = stats["total_wrong"] + test_data.get("wrong_answers", 0)
            avg_pct        = (stats["average_percentage"] * stats["total_tests"] +
                              test_data.get("percentage_score", 0)) / total_tests

            # Best subject: find subject with highest avg score across sessions
            best = self._get_best_subject(user_id)

            # Study streak: increment if last test was yesterday, reset if gap > 1 day
            streak = self._calc_streak(stats)

            conn.execute(
                """INSERT INTO user_stats
                   (user_id, total_tests, total_questions_answered, total_correct,
                    total_wrong, average_percentage, best_subject, last_test_date, study_streak)
                   VALUES (?,?,?,?,?,?,?,CURRENT_TIMESTAMP,?)
                   ON CONFLICT(user_id) DO UPDATE SET
                   total_tests=excluded.total_tests,
                   total_questions_answered=excluded.total_questions_answered,
                   total_correct=excluded.total_correct,
                   total_wrong=excluded.total_wrong,
                   average_percentage=excluded.average_percentage,
                   best_subject=excluded.best_subject,
                   last_test_date=excluded.last_test_date,
                   study_streak=excluded.study_streak""",
                (user_id, total_tests, total_q, total_correct,
                 total_wrong, avg_pct, best, streak),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False

    def _get_best_subject(self, user_id: int) -> Optional[str]:
        row = self._get_conn().execute(
            """SELECT subject, AVG(percentage_score) as avg_score
               FROM test_sessions
               WHERE user_id=? AND status='Completed'
               GROUP BY subject ORDER BY avg_score DESC LIMIT 1""",
            (user_id,),
        ).fetchone()
        return row["subject"] if row else None

    def _calc_streak(self, stats: Dict) -> int:
        last = stats.get("last_test_date")
        if not last:
            return 1
        try:
            if isinstance(last, str):
                last_date = datetime.fromisoformat(last).date()
            else:
                last_date = last.date() if hasattr(last, "date") else date.today()
            delta = (date.today() - last_date).days
            if delta == 0:
                return stats.get("study_streak", 1)
            elif delta == 1:
                return stats.get("study_streak", 0) + 1
            else:
                return 1
        except Exception:
            return 1

    def get_subject_performance(self, user_id: int) -> List[Dict]:
        rows = self._get_conn().execute(
            """SELECT subject, exam_type,
                      COUNT(*) as tests_taken,
                      AVG(percentage_score) as avg_score,
                      MAX(percentage_score) as best_score
               FROM test_sessions
               WHERE user_id=? AND status='Completed'
               GROUP BY subject, exam_type
               ORDER BY avg_score DESC""",
            (user_id,),
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_recent_activity(self, user_id: int, limit: int = 5) -> List[Dict]:
        rows = self._get_conn().execute(
            """SELECT * FROM test_sessions
               WHERE user_id=? AND status != 'In Progress'
               ORDER BY start_time DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]
