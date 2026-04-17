"""
NaijaEdu CBT - Subject Selection Screen
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea, QFrame, QButtonGroup,
    QDialog, QDialogButtonBox, QSizePolicy, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import SUBJECTS, SUBJECT_CATEGORY, CATEGORY_COLORS, SUBJECT_ICONS
from config import get_question_limit, get_time_limit_seconds, get_exam_config


class _ConfirmDialog(QDialog):
    def __init__(self, subject: str, exam_type: str, n_questions: int,
                 time_secs: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Exam")
        self.setFixedSize(360, 260)
        self.setModal(True)

        v = QVBoxLayout(self)
        v.setContentsMargins(30, 30, 30, 30)
        v.setSpacing(12)

        title = QLabel("Ready to start?")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        def row(label, value):
            h = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #7f8c8d;")
            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 13, QFont.Bold))
            val.setStyleSheet("color: #2c3e50;")
            h.addWidget(lbl)
            h.addStretch()
            h.addWidget(val)
            return h

        v.addLayout(row("Subject:",     subject))
        v.addLayout(row("Exam Type:",   exam_type))
        v.addLayout(row("Questions:",   str(n_questions)))
        h, m = divmod(time_secs // 60, 60)
        time_str = f"{h}h {m:02d}m" if h else f"{m} minutes"
        v.addLayout(row("Time Limit:",  time_str))
        v.addStretch()

        btns = QDialogButtonBox()
        cancel = btns.addButton("Cancel",     QDialogButtonBox.RejectRole)
        start  = btns.addButton("Start Exam", QDialogButtonBox.AcceptRole)
        start.setStyleSheet(
            "background:#27ae60; color:white; border:none; border-radius:6px;"
            "padding: 8px 20px; font-weight:bold;"
        )
        cancel.setStyleSheet(
            "background:#e0e0e0; color:#2c3e50; border:none; border-radius:6px;"
            "padding: 8px 20px;"
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        v.addWidget(btns)


class SubjectSelection(QWidget):
    start_test = pyqtSignal(str, str)   # subject, exam_type

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db        = db
        self._exam_type = "JAMB"
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

        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        title = QLabel("Select Subject")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # Exam type toggle
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(0)
        self._jamb_btn = self._toggle_btn("JAMB", True)
        self._waec_btn = self._toggle_btn("WAEC", False)
        self._jamb_btn.clicked.connect(lambda: self._set_exam("JAMB"))
        self._waec_btn.clicked.connect(lambda: self._set_exam("WAEC"))
        toggle_row.addWidget(self._jamb_btn)
        toggle_row.addWidget(self._waec_btn)
        toggle_row.addStretch()
        layout.addLayout(toggle_row)

        # Subject grid per category
        for category, subjects in SUBJECTS.items():
            cat_lbl = QLabel(category)
            cat_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
            color = CATEGORY_COLORS.get(category, "#27ae60")
            cat_lbl.setStyleSheet(f"color: {color}; margin-top: 8px;")
            layout.addWidget(cat_lbl)

            grid = QGridLayout()
            grid.setSpacing(12)
            for i, subj in enumerate(subjects):
                card = self._make_card(subj, category)
                grid.addWidget(card, i // 3, i % 3)
            layout.addLayout(grid)

        layout.addStretch()

    def _toggle_btn(self, text: str, active: bool) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(100, 36)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setCheckable(True)
        btn.setChecked(active)
        self._style_toggle(btn, active)
        return btn

    def _style_toggle(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background: #27ae60; color: white;
                    border: 1px solid #27ae60; border-radius: 6px;
                    font-weight: bold; font-size: 13px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: white; color: #2c3e50;
                    border: 1px solid #e0e0e0; border-radius: 6px;
                    font-size: 13px;
                }
                QPushButton:hover { background: #f0f0f0; }
            """)

    def _make_card(self, subject: str, category: str) -> QFrame:
        color = CATEGORY_COLORS.get(category, "#27ae60")
        icon  = SUBJECT_ICONS.get(subject, "📚")

        card = QFrame()
        card.setObjectName("subCard")
        card.setStyleSheet(f"""
            QFrame#subCard {{
                background: white; border-radius: 10px;
                border: 1px solid #e0e0e0;
            }}
        """)
        card.setFixedHeight(160)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        v = QVBoxLayout(card)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 32))
        icon_lbl.setStyleSheet(f"color: {color};")

        name_lbl = QLabel(subject)
        name_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        name_lbl.setStyleSheet("color: #2c3e50;")
        name_lbl.setWordWrap(True)

        btn = QPushButton("Start Test")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 6px; font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{ background: #219a52; }}
        """)
        btn.clicked.connect(lambda _, s=subject: self._on_start(s))

        v.addWidget(icon_lbl)
        v.addWidget(name_lbl)
        v.addStretch()
        v.addWidget(btn)
        return card

    # ─── Logic ────────────────────────────────────────────────────────────────

    def _set_exam(self, exam_type: str):
        self._exam_type = exam_type
        is_jamb = exam_type == "JAMB"
        self._style_toggle(self._jamb_btn, is_jamb)
        self._style_toggle(self._waec_btn, not is_jamb)

    def _on_start(self, subject: str):
        n    = get_question_limit(self._exam_type, subject)
        secs = get_time_limit_seconds(self._exam_type)
        count = self._db.get_question_count(self._exam_type, subject)

        if count < 10:
            QMessageBox.warning(
                self, "Insufficient Questions",
                f"Not enough {self._exam_type} questions for {subject}.\n"
                f"Available: {count} (minimum 10 required).\n"
                "Please run generate_sample_data.py to add questions."
            )
            return

        dlg = _ConfirmDialog(subject, self._exam_type, min(n, count), secs, self)
        if dlg.exec_() == QDialog.Accepted:
            self.start_test.emit(subject, self._exam_type)
