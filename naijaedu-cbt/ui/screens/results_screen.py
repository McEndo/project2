"""
NaijaEdu CBT - Results Screen
Score display with circular indicator, stats grid, and answer review mode.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPalette

from utils.helpers import format_duration, score_to_grade, percentage_color


# ─── Circular Score Widget ─────────────────────────────────────────────────────

class _CircleScore(QWidget):
    def __init__(self, percentage: float, parent=None):
        super().__init__(parent)
        self._pct   = percentage
        self._color = percentage_color(percentage)
        self.setFixedSize(180, 180)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(14, 14, 152, 152)

        # Background arc
        p.setPen(QPen(QColor("#e0e0e0"), 12))
        p.drawArc(rect, 0, 360 * 16)

        # Score arc
        span = int(-self._pct / 100 * 360 * 16)
        p.setPen(QPen(QColor(self._color), 12, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, 90 * 16, span)

        # Percentage text
        p.setPen(QPen(QColor("#2c3e50")))
        p.setFont(QFont("Segoe UI", 30, QFont.Bold))
        p.drawText(rect, Qt.AlignCenter, f"{self._pct:.0f}%")


# ─── Results Screen ───────────────────────────────────────────────────────────

class ResultsScreen(QWidget):
    retake_test   = pyqtSignal()
    back_to_dash  = pyqtSignal()
    review_answers = pyqtSignal(int)   # session_id

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db         = db
        self._session_id = -1
        self._build_ui()

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("background: #f8f9fa;")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f8f9fa; }")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: #f8f9fa;")
        scroll.setWidget(content)

        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignTop)

        # Placeholder – filled by load_session()
        self._content_frame = QFrame()
        self._layout.addWidget(self._content_frame)

    def _rebuild(self, session: dict, answers: list):
        # Clear old content
        old = self._content_frame
        self._content_frame = QFrame()
        self._content_frame.setStyleSheet("background: #f8f9fa;")
        self._layout.replaceWidget(old, self._content_frame)
        old.deleteLater()

        v = QVBoxLayout(self._content_frame)
        v.setContentsMargins(0, 0, 0, 40)
        v.setSpacing(0)
        v.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        pct     = session.get("percentage_score", 0.0)
        correct = session.get("correct_answers", 0)
        wrong   = session.get("wrong_answers", 0)
        skipped = session.get("skipped_questions", 0)
        total   = session.get("total_questions", 0)
        elapsed = session.get("time_spent_seconds", 0)
        exam    = session.get("exam_type", "JAMB")
        subj    = session.get("subject", "")
        passed  = pct >= 50

        # ── Hero banner ──
        banner = QFrame()
        banner.setFixedHeight(90)
        banner_color = "#e8f5e9" if passed else "#fdecea"
        banner.setStyleSheet(f"background: {banner_color};")
        bh = QHBoxLayout(banner)
        bh.setAlignment(Qt.AlignCenter)
        icon = "🎉" if passed else "📚"
        msg  = "Excellent work! Keep it up!" if passed else "Keep practicing! Review the topics below."
        banner_lbl = QLabel(f"{icon}  {msg}")
        banner_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        banner_lbl.setStyleSheet(f"color: {'#27ae60' if passed else '#e74c3c'};")
        bh.addWidget(banner_lbl)
        v.addWidget(banner)

        # ── Main content (max 800px) ──
        inner = QWidget()
        inner.setMaximumWidth(800)
        inner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        iv = QVBoxLayout(inner)
        iv.setContentsMargins(30, 30, 30, 30)
        iv.setSpacing(28)

        # Subject / exam info
        info_lbl = QLabel(f"{subj} — {exam}")
        info_lbl.setAlignment(Qt.AlignCenter)
        info_lbl.setFont(QFont("Segoe UI", 14))
        info_lbl.setStyleSheet("color: #7f8c8d;")
        iv.addWidget(info_lbl)

        # Circle + grade
        score_row = QHBoxLayout()
        score_row.setAlignment(Qt.AlignCenter)
        score_row.setSpacing(30)

        circle = _CircleScore(pct)
        grade_col = QVBoxLayout()
        grade_col.setAlignment(Qt.AlignCenter)
        grade_lbl = QLabel(score_to_grade(pct, exam))
        grade_lbl.setFont(QFont("Segoe UI", 36, QFont.Bold))
        grade_lbl.setStyleSheet(f"color: {percentage_color(pct)};")
        grade_lbl.setAlignment(Qt.AlignCenter)
        result_lbl = QLabel("PASSED" if passed else "FAILED")
        result_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        result_lbl.setStyleSheet(
            f"color: white; background: {'#27ae60' if passed else '#e74c3c'};"
            "border-radius: 6px; padding: 4px 18px;"
        )
        result_lbl.setAlignment(Qt.AlignCenter)
        grade_col.addWidget(grade_lbl)
        grade_col.addWidget(result_lbl)
        score_row.addWidget(circle)
        score_row.addLayout(grade_col)
        iv.addLayout(score_row)

        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(14)
        stats = [
            ("📋", "Total Questions", str(total),   "#3498db"),
            ("✅", "Correct",         str(correct),  "#27ae60"),
            ("❌", "Wrong",           str(wrong),    "#e74c3c"),
            ("⏱", "Time Spent",      format_duration(elapsed), "#f39c12"),
        ]
        for i, (icon, label, value, color) in enumerate(stats):
            card = self._stat_card(icon, label, value, color)
            stats_grid.addWidget(card, 0, i)
        iv.addLayout(stats_grid)

        # Action buttons
        btns_row = QHBoxLayout()
        btns_row.setSpacing(12)
        btns_row.setAlignment(Qt.AlignCenter)

        review_btn = QPushButton("📖  Review Answers")
        review_btn.setFixedHeight(46)
        review_btn.setFixedWidth(200)
        review_btn.setCursor(Qt.PointingHandCursor)
        review_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        review_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60; color: white;
                border: none; border-radius: 8px;
            }
            QPushButton:hover { background: #229954; }
        """)
        review_btn.clicked.connect(lambda: self.review_answers.emit(self._session_id))

        retake_btn = QPushButton("🔄  Retake Test")
        retake_btn.setFixedHeight(46)
        retake_btn.setFixedWidth(160)
        retake_btn.setCursor(Qt.PointingHandCursor)
        retake_btn.setFont(QFont("Segoe UI", 13))
        retake_btn.setStyleSheet("""
            QPushButton {
                background: white; color: #2c3e50;
                border: 2px solid #e0e0e0; border-radius: 8px;
            }
            QPushButton:hover { border-color: #27ae60; color: #27ae60; }
        """)
        retake_btn.clicked.connect(self.retake_test.emit)

        dash_btn = QPushButton("← Back to Dashboard")
        dash_btn.setFlat(True)
        dash_btn.setCursor(Qt.PointingHandCursor)
        dash_btn.setStyleSheet("color: #3498db; border: none; font-size: 13px;")
        dash_btn.clicked.connect(self.back_to_dash.emit)

        btns_row.addWidget(review_btn)
        btns_row.addWidget(retake_btn)
        iv.addLayout(btns_row)

        center_row = QHBoxLayout()
        center_row.setAlignment(Qt.AlignCenter)
        center_row.addWidget(dash_btn)
        iv.addLayout(center_row)

        # Answer review section
        if answers:
            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet("color: #e0e0e0;")
            iv.addWidget(sep)

            rev_title = QLabel("Answer Review")
            rev_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
            rev_title.setStyleSheet("color: #2c3e50;")
            iv.addWidget(rev_title)

            for j, ans in enumerate(answers):
                iv.addWidget(self._answer_card(j + 1, ans))

        wrapper = QHBoxLayout()
        wrapper.setAlignment(Qt.AlignHCenter)
        wrapper.addWidget(inner)
        v.addLayout(wrapper)

    # ─── Public API ───────────────────────────────────────────────────────────

    def load_session(self, session_id: int):
        self._session_id = session_id
        session = self._db.get_session_by_id(session_id)
        answers = self._db.get_session_answers(session_id)
        if session:
            self._rebuild(session, answers)

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _stat_card(icon, label, value, color) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white; border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        card.setFixedHeight(90)
        v = QVBoxLayout(card)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(4)
        v.setAlignment(Qt.AlignCenter)

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 18))
        icon_lbl.setStyleSheet(f"color: {color};")
        val_lbl = QLabel(value)
        val_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        val_lbl.setStyleSheet(f"color: {color};")
        row.addWidget(icon_lbl)
        row.addWidget(val_lbl)

        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #7f8c8d; font-size: 12px;")

        v.addLayout(row)
        v.addWidget(lbl)
        return card

    @staticmethod
    def _answer_card(number: int, ans: dict) -> QFrame:
        selected = ans.get("selected_option")
        correct  = ans.get("correct_option")
        is_right = ans.get("is_correct", False)

        card = QFrame()
        bg = "#f0faf0" if is_right else ("#fef0f0" if selected else "#fff8e1")
        card.setStyleSheet(f"""
            QFrame {{
                background: {bg}; border-radius: 8px;
                border: 1px solid {'#27ae60' if is_right else '#e74c3c' if selected else '#f39c12'};
                padding: 4px;
            }}
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(6)

        # Question
        q_lbl = QLabel(f"Q{number}. {ans.get('question_text','')}")
        q_lbl.setFont(QFont("Segoe UI", 13))
        q_lbl.setStyleSheet("color: #2c3e50;")
        q_lbl.setWordWrap(True)
        v.addWidget(q_lbl)

        # Options row
        opts_row = QHBoxLayout()
        opts_row.setSpacing(8)
        for letter in "ABCDE":
            key  = f"option_{letter.lower()}"
            text = ans.get(key, "")
            if not text:
                continue
            is_correct_opt  = letter == correct
            is_selected_opt = letter == selected
            color = "#27ae60" if is_correct_opt else ("#e74c3c" if is_selected_opt else "#e0e0e0")
            opt_lbl = QLabel(f"{letter}. {text[:40]}")
            opt_lbl.setStyleSheet(
                f"background: {color}22; border: 1px solid {color};"
                f"border-radius: 4px; padding: 4px 8px; font-size: 12px;"
                f"color: {'#2c3e50' if not is_correct_opt else '#27ae60'};"
            )
            opt_lbl.setWordWrap(False)
            opts_row.addWidget(opt_lbl)
        opts_row.addStretch()
        v.addLayout(opts_row)

        # Explanation
        explanation = ans.get("explanation", "")
        if explanation:
            exp_lbl = QLabel(f"💡 {explanation}")
            exp_lbl.setStyleSheet("color: #7f8c8d; font-size: 12px; font-style: italic;")
            exp_lbl.setWordWrap(True)
            v.addWidget(exp_lbl)

        return card
