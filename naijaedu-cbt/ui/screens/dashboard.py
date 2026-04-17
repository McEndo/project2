"""
NaijaEdu CBT - Dashboard Screen
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGridLayout,
    QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from ui.components.stat_card import StatCard
from config import SUBJECT_CATEGORY, CATEGORY_COLORS, ALL_SUBJECTS
from utils.helpers import format_date, format_duration, percentage_color


class Dashboard(QWidget):
    start_test = pyqtSignal()          # navigate to subject selection
    view_history = pyqtSignal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db      = db
        self._user_id : int  = -1
        self._user    : dict = {}
        self._build_ui()

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f8f9fa; }")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: #f8f9fa;")
        scroll.setWidget(content)

        self._main = QVBoxLayout(content)
        self._main.setContentsMargins(30, 30, 30, 30)
        self._main.setSpacing(24)

        # Header
        self._header_lbl  = QLabel("Welcome back!")
        self._header_lbl.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self._header_lbl.setStyleSheet("color: #2c3e50;")

        self._date_lbl = QLabel()
        self._date_lbl.setStyleSheet("color: #7f8c8d; font-size: 14px;")

        from datetime import datetime
        self._date_lbl.setText(datetime.now().strftime("%A, %B %d, %Y"))

        self._main.addWidget(self._header_lbl)
        self._main.addWidget(self._date_lbl)

        # Stats row
        self._stats_row = QHBoxLayout()
        self._stats_row.setSpacing(16)
        self._stat_tests  = StatCard("Tests Taken",    "0",  "📋", "#3498db")
        self._stat_avg    = StatCard("Average Score",  "0%", "📈", "#27ae60")
        self._stat_best   = StatCard("Best Subject",   "—",  "🏆", "#f39c12")
        self._stat_streak = StatCard("Study Streak",   "0 days", "🔥", "#e74c3c")
        for card in (self._stat_tests, self._stat_avg, self._stat_best, self._stat_streak):
            self._stats_row.addWidget(card)
        self._main.addLayout(self._stats_row)

        # Quick Start
        self._main.addWidget(self._section_header("Quick Start", self._on_view_all))
        self._subject_grid = QGridLayout()
        self._subject_grid.setSpacing(12)
        self._build_subject_grid()
        self._main.addLayout(self._subject_grid)

        # Recent activity
        self._main.addWidget(self._section_header("Recent Activity", self.view_history.emit))
        self._activity_table = self._build_activity_table()
        self._main.addWidget(self._activity_table)
        self._main.addStretch()

    def _section_header(self, title: str, link_action=None) -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        lbl.setStyleSheet("color: #2c3e50;")
        h.addWidget(lbl)
        h.addStretch()
        if link_action:
            btn = QPushButton("View All →")
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("color: #3498db; border: none; font-size: 13px;")
            btn.clicked.connect(link_action)
            h.addWidget(btn)
        return row

    def _build_subject_grid(self):
        # Show first 6 subjects
        from config import ALL_SUBJECTS, SUBJECT_CATEGORY, CATEGORY_COLORS, SUBJECT_ICONS
        sample = ALL_SUBJECTS[:6]
        for i, subj in enumerate(sample):
            row, col = divmod(i, 3)
            card = self._make_subject_card(subj)
            self._subject_grid.addWidget(card, row, col)

    def _make_subject_card(self, subject: str) -> QFrame:
        from config import SUBJECT_CATEGORY, CATEGORY_COLORS, SUBJECT_ICONS
        cat   = SUBJECT_CATEGORY.get(subject, "General")
        color = CATEGORY_COLORS.get(cat, "#27ae60")
        icon  = SUBJECT_ICONS.get(subject, "📚")

        card = QFrame()
        card.setObjectName("subjectCard")
        card.setStyleSheet(f"""
            QFrame#subjectCard {{
                background: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }}
            QFrame#subjectCard:hover {{
                border-color: {color};
            }}
        """)
        card.setFixedHeight(140)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        v = QVBoxLayout(card)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 28))
        icon_lbl.setStyleSheet(f"color: {color};")

        name_lbl = QLabel(subject)
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        name_lbl.setStyleSheet("color: #2c3e50;")
        name_lbl.setWordWrap(True)

        btn = QPushButton("Start Test")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(30)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 5px; font-size: 12px;
            }}
            QPushButton:hover {{ opacity: 0.85; }}
        """)
        btn.clicked.connect(self.start_test.emit)

        v.addWidget(icon_lbl)
        v.addWidget(name_lbl)
        v.addStretch()
        v.addWidget(btn)
        return card

    def _build_activity_table(self) -> QTableWidget:
        tbl = QTableWidget(0, 5)
        tbl.setHorizontalHeaderLabels(["Date", "Subject", "Type", "Score", "Status"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)
        tbl.setAlternatingRowColors(True)
        tbl.setStyleSheet("""
            QTableWidget {
                background: white; border-radius: 8px;
                border: 1px solid #e0e0e0; gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background: #f8f9fa; color: #7f8c8d;
                font-size: 12px; font-weight: 600;
                padding: 8px; border: none;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableWidget::item { padding: 8px; }
        """)
        return tbl

    def _on_view_all(self):
        self.start_test.emit()

    # ─── Public API ───────────────────────────────────────────────────────────

    def load_user(self, user_id: int):
        self._user_id = user_id
        user  = self._db.get_user_by_id(user_id)
        stats = self._db.get_user_stats(user_id)
        if not user:
            return
        self._user = user

        first = user["full_name"].split()[0]
        self._header_lbl.setText(f"Welcome back, {first}!")

        self._stat_tests.set_value(str(stats.get("total_tests", 0)))
        avg = stats.get("average_percentage", 0.0)
        self._stat_avg.set_value(f"{avg:.1f}%")
        self._stat_best.set_value(stats.get("best_subject") or "—")
        self._stat_streak.set_value(f"{stats.get('study_streak', 0)} days")

        self._load_recent_activity(user_id)

    def _load_recent_activity(self, user_id: int):
        rows = self._db.get_recent_activity(user_id, limit=5)
        self._activity_table.setRowCount(0)

        if not rows:
            self._activity_table.setRowCount(1)
            empty = QTableWidgetItem("No tests taken yet. Start your first test!")
            empty.setTextAlignment(Qt.AlignCenter)
            self._activity_table.setItem(0, 0, empty)
            self._activity_table.setSpan(0, 0, 1, 5)
            return

        for r, session in enumerate(rows):
            self._activity_table.insertRow(r)
            cells = [
                format_date(session.get("start_time", "")),
                session.get("subject", ""),
                session.get("exam_type", ""),
                f"{session.get('percentage_score', 0):.1f}%",
                session.get("status", ""),
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if c == 4:
                    color = "#27ae60" if text == "Completed" else "#f39c12"
                    item.setForeground(QColor(color))
                self._activity_table.setItem(r, c, item)
