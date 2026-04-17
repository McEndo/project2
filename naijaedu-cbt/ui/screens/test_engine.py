"""
NaijaEdu CBT - Test Engine Screen
The core CBT interface: question display, navigation, palette, timer, auto-save.
"""

import random
from typing import Optional, Dict, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QRadioButton, QButtonGroup,
    QProgressBar, QDialog, QDialogButtonBox, QSizePolicy,
    QMessageBox, QSplitter,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QKeyEvent, QPixmap

from ui.components.timer_widget import TimerWidget
from ui.components.question_palette import QuestionPalette
from ui.components.calculator_dialog import CalculatorDialog
from config import get_question_limit, get_time_limit_seconds, AUTOSAVE_INTERVAL_MS


# ─── Submit Confirmation Dialog ───────────────────────────────────────────────

class _SubmitDialog(QDialog):
    def __init__(self, total, answered, unanswered, flagged, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Submit Exam")
        self.setFixedSize(380, 300)
        self.setModal(True)

        v = QVBoxLayout(self)
        v.setContentsMargins(30, 30, 30, 30)
        v.setSpacing(14)

        title = QLabel("Submit Exam?")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        v.addWidget(title)

        sub = QLabel("Here's a summary of your attempt:")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        v.addWidget(sub)

        def stat_row(icon, label, value, color="#2c3e50"):
            row = QHBoxLayout()
            lbl = QLabel(f"{icon}  {label}")
            lbl.setStyleSheet(f"color: #7f8c8d; font-size: 13px;")
            val = QLabel(str(value))
            val.setFont(QFont("Segoe UI", 13, QFont.Bold))
            val.setStyleSheet(f"color: {color};")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            return row

        v.addLayout(stat_row("📋", "Total Questions", total))
        v.addLayout(stat_row("✅", "Answered",        answered,   "#27ae60"))
        v.addLayout(stat_row("⬜", "Unanswered",      unanswered, "#e74c3c" if unanswered else "#2c3e50"))
        v.addLayout(stat_row("⚑",  "Flagged",         flagged,    "#f39c12" if flagged else "#2c3e50"))
        v.addStretch()

        btns = QDialogButtonBox()
        review = btns.addButton("Review",     QDialogButtonBox.RejectRole)
        submit = btns.addButton("Submit Now", QDialogButtonBox.AcceptRole)
        submit.setStyleSheet(
            "background:#e74c3c; color:white; border:none; border-radius:6px;"
            "padding:8px 20px; font-weight:bold;"
        )
        review.setStyleSheet(
            "background:#e0e0e0; color:#2c3e50; border:none; border-radius:6px;"
            "padding:8px 20px;"
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        v.addWidget(btns)


# ─── Test Engine ──────────────────────────────────────────────────────────────

class TestEngine(QWidget):
    test_completed  = pyqtSignal(int)   # session_id
    exit_to_dash    = pyqtSignal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db         = db
        self._session_id : int  = -1
        self._user_id    : int  = -1
        self._questions  : List[Dict] = []
        self._current_idx: int  = 0
        self._answers    : Dict[int, Optional[str]] = {}   # q_index → selected letter
        self._flagged    : set  = set()
        self._calc_dlg   : Optional[CalculatorDialog] = None

        self._build_ui()

        # Auto-save timer
        self._autosave = QTimer(self)
        self._autosave.timeout.connect(self._auto_save)
        self._autosave.setInterval(AUTOSAVE_INTERVAL_MS)

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Left panel ──
        self._left_panel = QFrame()
        self._left_panel.setFixedWidth(280)
        self._left_panel.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-right: 1px solid #e0e0e0;
            }
        """)
        self._left_layout = QVBoxLayout(self._left_panel)
        self._left_layout.setContentsMargins(12, 16, 12, 16)
        self._left_layout.setSpacing(12)

        # Timer
        timer_lbl = QLabel("Time Remaining")
        timer_lbl.setAlignment(Qt.AlignCenter)
        timer_lbl.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self._timer = TimerWidget()
        self._timer.time_up.connect(self._on_time_up)
        self._left_layout.addWidget(timer_lbl)
        self._left_layout.addWidget(self._timer)

        # Progress
        self._progress_lbl = QLabel("Question 1 of 0")
        self._progress_lbl.setAlignment(Qt.AlignCenter)
        self._progress_lbl.setStyleSheet("color: #2c3e50; font-size: 13px; font-weight: 600;")
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet("""
            QProgressBar { background: #e0e0e0; border-radius: 3px; border: none; }
            QProgressBar::chunk { background: #27ae60; border-radius: 3px; }
        """)
        self._left_layout.addWidget(self._progress_lbl)
        self._left_layout.addWidget(self._progress_bar)

        # Palette label
        pal_lbl = QLabel("Question Palette")
        pal_lbl.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-top: 4px;")
        self._left_layout.addWidget(pal_lbl)

        # Palette container — we swap the palette widget inside here
        self._palette_container = QWidget()
        self._palette_container.setStyleSheet("background: transparent;")
        self._palette_container_layout = QVBoxLayout(self._palette_container)
        self._palette_container_layout.setContentsMargins(0, 0, 0, 0)
        self._palette = QuestionPalette(0)
        self._palette_container_layout.addWidget(self._palette)
        self._left_layout.addWidget(self._palette_container, 1)

        # Flag button
        self._flag_btn = QPushButton("⚑  Flag for Review")
        self._flag_btn.setCheckable(True)
        self._flag_btn.setCursor(Qt.PointingHandCursor)
        self._flag_btn.setFixedHeight(38)
        self._flag_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #f39c12;
                color: #f39c12; border-radius: 6px; font-weight: 600;
            }
            QPushButton:checked {
                background: #f39c12; color: white;
            }
        """)
        self._flag_btn.toggled.connect(self._toggle_flag)
        self._left_layout.addWidget(self._flag_btn)

        # Calculator
        calc_btn = QPushButton("🧮  Calculator")
        calc_btn.setCursor(Qt.PointingHandCursor)
        calc_btn.setFixedHeight(38)
        calc_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #3498db;
                color: #3498db; border-radius: 6px; font-weight: 600;
            }
            QPushButton:hover { background: #ebf5fb; }
        """)
        calc_btn.clicked.connect(self._open_calc)
        self._left_layout.addWidget(calc_btn)

        # Submit
        submit_btn = QPushButton("Submit Exam")
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setFixedHeight(44)
        submit_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        submit_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c; color: white;
                border: none; border-radius: 6px;
            }
            QPushButton:hover { background: #c0392b; }
        """)
        submit_btn.clicked.connect(self._confirm_submit)
        self._left_layout.addWidget(submit_btn)

        main.addWidget(self._left_panel)

        # ── Right panel ──
        right = QWidget()
        right.setStyleSheet("background: #f8f9fa;")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header bar
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        hh = QHBoxLayout(header)
        hh.setContentsMargins(24, 0, 24, 0)
        self._subject_lbl = QLabel("Subject")
        self._subject_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self._subject_lbl.setStyleSheet("color: #2c3e50;")
        self._qnum_lbl = QLabel("Q 1 / 0")
        self._qnum_lbl.setAlignment(Qt.AlignCenter)
        self._qnum_lbl.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        hh.addWidget(self._subject_lbl)
        hh.addStretch()
        hh.addWidget(self._qnum_lbl)
        right_layout.addWidget(header)

        # Question scroll area
        q_scroll = QScrollArea()
        q_scroll.setWidgetResizable(True)
        q_scroll.setStyleSheet("QScrollArea { border: none; background: #f8f9fa; }")
        q_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        q_container = QWidget()
        q_container.setStyleSheet("background: #f8f9fa;")
        self._q_layout = QVBoxLayout(q_container)
        self._q_layout.setContentsMargins(32, 28, 32, 28)
        self._q_layout.setSpacing(16)

        # Question card
        q_card = QFrame()
        q_card.setObjectName("qCard")
        q_card.setStyleSheet("""
            QFrame#qCard {
                background: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        q_card_layout = QVBoxLayout(q_card)
        q_card_layout.setContentsMargins(28, 24, 28, 24)
        q_card_layout.setSpacing(20)

        # Question number badge
        self._q_badge = QLabel("Question 1")
        self._q_badge.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self._q_badge.setStyleSheet(
            "color: #27ae60; background: #e8f5e9; border-radius: 4px; padding: 4px 10px;"
        )
        self._q_badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Question text
        self._q_text = QLabel()
        self._q_text.setFont(QFont("Segoe UI", 16))
        self._q_text.setStyleSheet("color: #2c3e50; line-height: 1.6;")
        self._q_text.setWordWrap(True)
        self._q_text.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Options group
        self._option_group = QButtonGroup(self)
        self._option_group.buttonClicked.connect(self._on_option_selected)
        self._options_layout = QVBoxLayout()
        self._options_layout.setSpacing(10)
        self._option_radios: List[QRadioButton] = []

        # Create 5 radio buttons (WAEC has E)
        for i, letter in enumerate("ABCDE"):
            rb = QRadioButton()
            rb.setProperty("letter", letter)
            rb.setFont(QFont("Segoe UI", 15))
            rb.setStyleSheet(self._radio_style(False))
            rb.setCursor(Qt.PointingHandCursor)
            self._option_group.addButton(rb, i)
            self._options_layout.addWidget(rb)
            self._option_radios.append(rb)

        q_card_layout.addWidget(self._q_badge)
        q_card_layout.addWidget(self._q_text)
        q_card_layout.addLayout(self._options_layout)

        self._q_layout.addWidget(q_card)
        self._q_layout.addStretch()
        q_scroll.setWidget(q_container)
        right_layout.addWidget(q_scroll, 1)

        # Navigation bar
        nav = QFrame()
        nav.setFixedHeight(64)
        nav.setStyleSheet("background: white; border-top: 1px solid #e0e0e0;")
        nh = QHBoxLayout(nav)
        nh.setContentsMargins(32, 0, 32, 0)

        self._prev_btn = QPushButton("← Previous")
        self._prev_btn.setFixedSize(140, 40)
        self._prev_btn.setCursor(Qt.PointingHandCursor)
        self._prev_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 2px solid #e0e0e0;
                border-radius: 8px; color: #2c3e50; font-weight: 600;
            }
            QPushButton:hover { border-color: #27ae60; color: #27ae60; }
            QPushButton:disabled { color: #bdc3c7; border-color: #e0e0e0; }
        """)
        self._prev_btn.clicked.connect(self._prev)

        self._next_btn = QPushButton("Next →")
        self._next_btn.setFixedSize(140, 40)
        self._next_btn.setCursor(Qt.PointingHandCursor)
        self._next_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60; border: none;
                border-radius: 8px; color: white; font-weight: 600;
            }
            QPushButton:hover { background: #229954; }
            QPushButton:disabled { background: #bdc3c7; }
        """)
        self._next_btn.clicked.connect(self._next)

        hint = QLabel("1-5: Select option  |  ← →: Navigate  |  F: Flag  |  C: Calculator")
        hint.setStyleSheet("color: #bdc3c7; font-size: 11px;")

        nh.addWidget(self._prev_btn)
        nh.addStretch()
        nh.addWidget(hint)
        nh.addStretch()
        nh.addWidget(self._next_btn)
        right_layout.addWidget(nav)

        main.addWidget(right, 1)

    # ─── Public API ───────────────────────────────────────────────────────────

    def start_session(self, user_id: int, subject: str, exam_type: str):
        """Load questions and initialise a new test session."""
        self._user_id    = user_id
        self._questions  = []
        self._answers    = {}
        self._flagged    = set()
        self._current_idx = 0

        limit = get_question_limit(exam_type, subject)
        qs    = self._db.get_questions(exam_type, subject, limit)

        if not qs:
            QMessageBox.critical(self, "No Questions",
                "No questions found. Please run generate_sample_data.py first.")
            self.exit_to_dash.emit()
            return

        self._questions = qs
        n = len(qs)

        # Create DB session
        self._session_id = self._db.create_test_session(user_id, exam_type, subject, n)

        # Reset palette via container swap
        old_palette = self._palette
        self._palette = QuestionPalette(n)
        self._palette.jump_to.connect(self._go_to)
        self._palette_container_layout.replaceWidget(old_palette, self._palette)
        old_palette.deleteLater()

        # Update header
        self._subject_lbl.setText(subject)
        self._progress_bar.setRange(0, n)
        self._progress_bar.setValue(0)

        # Timer
        secs = get_time_limit_seconds(exam_type)
        self._timer.set_time(secs)
        self._timer.start()

        # Auto-save
        self._autosave.start()

        self._show_question(0)

    # ─── Navigation ───────────────────────────────────────────────────────────

    def _go_to(self, index: int):
        self._save_current_answer()
        self._current_idx = index
        self._show_question(index)

    def _prev(self):
        if self._current_idx > 0:
            self._go_to(self._current_idx - 1)

    def _next(self):
        if self._current_idx < len(self._questions) - 1:
            self._go_to(self._current_idx + 1)

    # ─── Display ──────────────────────────────────────────────────────────────

    def _show_question(self, index: int):
        if not self._questions:
            return
        q = self._questions[index]
        n = len(self._questions)

        # Badge & text
        self._q_badge.setText(f"Question {index + 1}")
        self._q_text.setText(q["question_text"])
        self._qnum_lbl.setText(f"Q {index+1} / {n}")
        self._progress_lbl.setText(f"Question {index+1} of {n}")
        self._progress_bar.setValue(index + 1)

        # Options
        options = {
            "A": q.get("option_a", ""),
            "B": q.get("option_b", ""),
            "C": q.get("option_c", ""),
            "D": q.get("option_d", ""),
            "E": q.get("option_e", ""),
        }
        saved = self._answers.get(index)

        for i, rb in enumerate(self._option_radios):
            letter = "ABCDE"[i]
            text   = options.get(letter, "")
            if text:
                rb.setText(f"  {letter}.  {text}")
                rb.setVisible(True)
                rb.setChecked(saved == letter)
                rb.setStyleSheet(self._radio_style(saved == letter))
            else:
                rb.setVisible(False)
                rb.setChecked(False)

        # Flag button state
        self._flag_btn.blockSignals(True)
        self._flag_btn.setChecked(index in self._flagged)
        self._flag_btn.blockSignals(False)

        # Palette
        self._palette.set_current(index)

        # Nav buttons
        self._prev_btn.setEnabled(index > 0)
        self._next_btn.setEnabled(index < n - 1)

    # ─── Answering ────────────────────────────────────────────────────────────

    def _on_option_selected(self, btn: QRadioButton):
        letter = btn.property("letter")
        idx    = self._current_idx
        self._answers[idx] = letter
        self._palette.mark_answered(idx)
        # Restyle all radios
        for rb in self._option_radios:
            rb.setStyleSheet(self._radio_style(rb.isChecked()))
        # Save immediately to DB
        q          = self._questions[idx]
        is_correct = (letter == q["correct_option"])
        self._db.save_answer(
            self._session_id, q["id"], letter, is_correct,
            self._timer.get_elapsed_seconds()
        )

    def _save_current_answer(self):
        """Persist whatever is currently selected (called on navigation)."""
        idx    = self._current_idx
        letter = self._answers.get(idx)
        if idx < len(self._questions) and letter:
            q = self._questions[idx]
            self._db.save_answer(
                self._session_id, q["id"], letter,
                letter == q["correct_option"],
                self._timer.get_elapsed_seconds()
            )

    # ─── Flagging ─────────────────────────────────────────────────────────────

    def _toggle_flag(self, checked: bool):
        idx = self._current_idx
        if checked:
            self._flagged.add(idx)
        else:
            self._flagged.discard(idx)
        self._palette.toggle_flag(idx)

    # ─── Calculator ───────────────────────────────────────────────────────────

    def _open_calc(self):
        if self._calc_dlg is None:
            self._calc_dlg = CalculatorDialog(self)
        self._calc_dlg.show()
        self._calc_dlg.raise_()

    # ─── Auto-save ────────────────────────────────────────────────────────────

    def _auto_save(self):
        self._save_current_answer()

    # ─── Submit ───────────────────────────────────────────────────────────────

    def _confirm_submit(self):
        n          = len(self._questions)
        answered   = len(self._answers)
        unanswered = n - answered
        flagged    = len(self._flagged)

        dlg = _SubmitDialog(n, answered, unanswered, flagged, self)
        if dlg.exec_() == QDialog.Accepted:
            self._submit()

    def _submit(self):
        self._timer.stop()
        self._autosave.stop()
        self._save_current_answer()

        n       = len(self._questions)
        correct = 0
        wrong   = 0
        skipped = 0

        for i, q in enumerate(self._questions):
            sel = self._answers.get(i)
            if sel is None:
                skipped += 1
            elif sel == q["correct_option"]:
                correct += 1
            else:
                wrong += 1

        pct = (correct / n * 100) if n else 0
        elapsed = self._timer.get_elapsed_seconds()

        self._db.complete_test_session(
            self._session_id, correct, correct, wrong, skipped, pct, elapsed
        )
        self._db.update_user_stats(self._user_id, {
            "total_questions"  : n,
            "correct_answers"  : correct,
            "wrong_answers"    : wrong,
            "percentage_score" : pct,
        })
        self.test_completed.emit(self._session_id)

    def _on_time_up(self):
        QMessageBox.information(
            self, "Time Up!",
            "Time is up! Your exam will be submitted automatically."
        )
        self._submit()

    # ─── Keyboard Shortcuts ───────────────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent):
        key  = event.key()
        text = event.text().upper()

        if text in "12345":
            idx = int(text) - 1
            if idx < len(self._option_radios) and self._option_radios[idx].isVisible():
                self._option_radios[idx].click()

        elif key in (Qt.Key_Right, Qt.Key_N):
            self._next()
        elif key in (Qt.Key_Left, Qt.Key_P):
            self._prev()
        elif key == Qt.Key_F:
            self._flag_btn.toggle()
        elif key == Qt.Key_C:
            self._open_calc()
        elif key == Qt.Key_S:
            self._confirm_submit()
        else:
            super().keyPressEvent(event)

    # ─── Style helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _radio_style(selected: bool) -> str:
        if selected:
            return """
                QRadioButton {
                    background: #e8f5e9; border: 2px solid #27ae60;
                    border-radius: 8px; padding: 14px 12px;
                    font-size: 15px; color: #2c3e50;
                }
                QRadioButton::indicator { width:18px; height:18px; border-radius:9px;
                    border:2px solid #27ae60; background:#27ae60; }
            """
        return """
            QRadioButton {
                background: white; border: 2px solid #e0e0e0;
                border-radius: 8px; padding: 14px 12px;
                font-size: 15px; color: #2c3e50;
            }
            QRadioButton:hover { border-color: #27ae60; background: #f8fdf9; }
            QRadioButton::indicator { width:18px; height:18px; border-radius:9px;
                border:2px solid #bdc3c7; background:white; }
            QRadioButton::indicator:checked { background:#27ae60; border-color:#27ae60; }
        """

    # ─── Window close guard ───────────────────────────────────────────────────

    def is_test_active(self) -> bool:
        return self._session_id != -1 and self._timer._running
