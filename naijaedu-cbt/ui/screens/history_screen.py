"""
NaijaEdu CBT - History Screen
Test history with filters, pagination, and CSV export.
"""

import csv
import os
from pathlib import Path
from typing import List, Dict

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QScrollArea, QSizePolicy, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from config import ALL_SUBJECTS, HISTORY_PAGE_SIZE
from utils.helpers import format_date, format_duration, percentage_color


class HistoryScreen(QWidget):
    view_session = pyqtSignal(int)   # session_id → results screen

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db       = db
        self._user_id  = -1
        self._all_rows : List[Dict] = []
        self._filtered : List[Dict] = []
        self._page     = 0
        self._build_ui()

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("background: #f8f9fa;")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 30, 30, 30)
        outer.setSpacing(18)

        # Title row
        title_row = QHBoxLayout()
        title = QLabel("Test History")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title_row.addWidget(title)
        title_row.addStretch()

        export_btn = QPushButton("📥  Export CSV")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setFixedHeight(36)
        export_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #e0e0e0;
                border-radius: 6px; padding: 0 16px; color: #2c3e50; font-size: 13px;
            }
            QPushButton:hover { border-color: #27ae60; color: #27ae60; }
        """)
        export_btn.clicked.connect(self._export_csv)
        title_row.addWidget(export_btn)
        outer.addLayout(title_row)

        # Filters row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self._subj_filter = self._make_combo(
            ["All Subjects"] + ALL_SUBJECTS, width=200
        )
        self._type_filter = self._make_combo(["All Types", "JAMB", "WAEC"], width=130)
        self._date_filter = self._make_combo(
            ["All Time", "Last 7 Days", "Last 30 Days"], width=160
        )

        for combo in (self._subj_filter, self._type_filter, self._date_filter):
            combo.currentIndexChanged.connect(self._apply_filters)
            filter_row.addWidget(combo)

        filter_row.addStretch()
        outer.addLayout(filter_row)

        # Table
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["Date", "Subject", "Type", "Score", "Time", "Actions"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self._table.setColumnWidth(5, 110)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.setStyleSheet("""
            QTableWidget {
                background: white; border-radius: 10px;
                border: 1px solid #e0e0e0; gridline-color: transparent;
            }
            QTableWidget::item { padding: 10px; }
            QTableWidget::item:selected { background: #e8f5e9; color: #2c3e50; }
            QHeaderView::section {
                background: #f8f9fa; color: #7f8c8d;
                font-size: 12px; font-weight: 600; padding: 10px;
                border: none; border-bottom: 1px solid #e0e0e0;
            }
        """)
        self._table.setRowHeight(0, 52)
        outer.addWidget(self._table, 1)

        # Pagination row
        pag_row = QHBoxLayout()
        pag_row.setAlignment(Qt.AlignCenter)
        pag_row.setSpacing(8)

        self._prev_page_btn = QPushButton("← Prev")
        self._next_page_btn = QPushButton("Next →")
        self._page_lbl      = QLabel("Page 1")

        for btn in (self._prev_page_btn, self._next_page_btn):
            btn.setFixedSize(90, 34)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: white; border: 1px solid #e0e0e0;
                    border-radius: 6px; color: #2c3e50; font-size: 13px;
                }
                QPushButton:hover { border-color: #27ae60; color: #27ae60; }
                QPushButton:disabled { color: #bdc3c7; }
            """)

        self._prev_page_btn.clicked.connect(self._prev_page)
        self._next_page_btn.clicked.connect(self._next_page)
        self._page_lbl.setStyleSheet("color: #7f8c8d; font-size: 13px;")

        pag_row.addWidget(self._prev_page_btn)
        pag_row.addWidget(self._page_lbl)
        pag_row.addWidget(self._next_page_btn)
        outer.addLayout(pag_row)

    @staticmethod
    def _make_combo(items: list, width: int = 160) -> QComboBox:
        cb = QComboBox()
        cb.addItems(items)
        cb.setFixedSize(width, 36)
        cb.setStyleSheet("""
            QComboBox {
                background: white; border: 1px solid #e0e0e0;
                border-radius: 6px; padding: 0 10px; color: #2c3e50; font-size: 13px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox:hover { border-color: #27ae60; }
        """)
        return cb

    # ─── Public API ───────────────────────────────────────────────────────────

    def load_user(self, user_id: int):
        self._user_id = user_id
        self._all_rows = self._db.get_test_history(user_id, limit=200)
        self._page = 0
        self._apply_filters()

    # ─── Filtering ────────────────────────────────────────────────────────────

    def _apply_filters(self):
        from datetime import datetime, timedelta

        subj  = self._subj_filter.currentText()
        typ   = self._type_filter.currentText()
        days  = self._date_filter.currentText()

        rows = self._all_rows

        if subj != "All Subjects":
            rows = [r for r in rows if r.get("subject") == subj]
        if typ != "All Types":
            rows = [r for r in rows if r.get("exam_type") == typ]
        if days == "Last 7 Days":
            cutoff = datetime.now() - timedelta(days=7)
            rows = [r for r in rows if self._parse_dt(r.get("start_time","")) >= cutoff]
        elif days == "Last 30 Days":
            cutoff = datetime.now() - timedelta(days=30)
            rows = [r for r in rows if self._parse_dt(r.get("start_time","")) >= cutoff]

        self._filtered = rows
        self._page     = 0
        self._render_page()

    @staticmethod
    def _parse_dt(dt_str: str):
        from datetime import datetime
        try:
            return datetime.fromisoformat(dt_str)
        except Exception:
            return datetime.min

    # ─── Rendering ────────────────────────────────────────────────────────────

    def _render_page(self):
        page_rows = self._filtered[
            self._page * HISTORY_PAGE_SIZE :
            (self._page + 1) * HISTORY_PAGE_SIZE
        ]
        total_pages = max(1, -(-len(self._filtered) // HISTORY_PAGE_SIZE))
        self._page_lbl.setText(f"Page {self._page+1} of {total_pages}")
        self._prev_page_btn.setEnabled(self._page > 0)
        self._next_page_btn.setEnabled(self._page < total_pages - 1)

        self._table.setRowCount(0)

        if not page_rows:
            self._table.setRowCount(1)
            empty = QTableWidgetItem("No tests found. Start your first test!")
            empty.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(0, 0, empty)
            self._table.setSpan(0, 0, 1, 6)
            return

        for r, session in enumerate(page_rows):
            self._table.insertRow(r)
            self._table.setRowHeight(r, 52)
            pct = session.get("percentage_score", 0.0)

            cells = [
                format_date(session.get("start_time", "")),
                session.get("subject", ""),
                session.get("exam_type", ""),
                f"{pct:.1f}%",
                format_duration(session.get("time_spent_seconds", 0)),
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if c == 3:   # score → colour coded
                    item.setForeground(QColor(percentage_color(pct)))
                    item.setFont(QFont("Segoe UI", 13, QFont.Bold))
                self._table.setItem(r, c, item)

            # Action buttons cell
            action_widget = QWidget()
            ah = QHBoxLayout(action_widget)
            ah.setContentsMargins(4, 4, 4, 4)
            ah.setSpacing(4)

            view_btn = QPushButton("👁 View")
            view_btn.setFixedHeight(28)
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.setStyleSheet("""
                QPushButton {
                    background: #e8f5e9; color: #27ae60; border: none;
                    border-radius: 5px; font-size: 11px; font-weight: 600; padding: 0 6px;
                }
                QPushButton:hover { background: #27ae60; color: white; }
            """)
            sid = session.get("id", -1)
            view_btn.clicked.connect(lambda _, s=sid: self.view_session.emit(s))
            ah.addWidget(view_btn)
            self._table.setCellWidget(r, 5, action_widget)

    # ─── Pagination ───────────────────────────────────────────────────────────

    def _prev_page(self):
        if self._page > 0:
            self._page -= 1
            self._render_page()

    def _next_page(self):
        total_pages = max(1, -(-len(self._filtered) // HISTORY_PAGE_SIZE))
        if self._page < total_pages - 1:
            self._page += 1
            self._render_page()

    # ─── Export ───────────────────────────────────────────────────────────────

    def _export_csv(self):
        if not self._filtered:
            QMessageBox.information(self, "Export", "No records to export.")
            return
        docs = Path.home() / "Documents"
        docs.mkdir(parents=True, exist_ok=True)
        path = docs / "naijaedu-history.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Subject", "Type", "Score%", "Time (s)", "Status"])
                for row in self._filtered:
                    writer.writerow([
                        format_date(row.get("start_time", "")),
                        row.get("subject", ""),
                        row.get("exam_type", ""),
                        f"{row.get('percentage_score', 0):.1f}",
                        row.get("time_spent_seconds", 0),
                        row.get("status", ""),
                    ])
            QMessageBox.information(
                self, "Export Successful",
                f"History exported to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
