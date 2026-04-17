"""
NaijaEdu CBT - Question Palette Component
Grid of numbered buttons showing answer/flag status per question.
"""

from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QCursor

from config import PALETTE_COLUMNS, PALETTE_BUTTON_SZ


_STYLES = {
    "not_visited": {
        "bg": "#ffffff", "border": "#e0e0e0", "fg": "#2c3e50",
    },
    "current": {
        "bg": "#3498db", "border": "#2980b9", "fg": "#ffffff",
    },
    "answered": {
        "bg": "#27ae60", "border": "#219a52", "fg": "#ffffff",
    },
    "flagged": {
        "bg": "#f39c12", "border": "#d68910", "fg": "#ffffff",
    },
    "answered_flagged": {
        "bg": "#27ae60", "border": "#f39c12", "fg": "#ffffff",
    },
}


def _btn_stylesheet(state: str) -> str:
    s = _STYLES.get(state, _STYLES["not_visited"])
    extra_border = "3px" if state == "answered_flagged" else "1px"
    return (
        f"QPushButton {{"
        f"  background: {s['bg']};"
        f"  border: {extra_border} solid {s['border']};"
        f"  color: {s['fg']};"
        f"  border-radius: 4px;"
        f"  font-size: 12px;"
        f"  font-weight: bold;"
        f"}}"
        f"QPushButton:hover {{ border-color: #2c3e50; }}"
    )


class QuestionPalette(QWidget):
    """
    Emits:
        jump_to(int)  – 0-based question index
        flag_toggled(int) – right-click toggles flag
    """
    jump_to      = pyqtSignal(int)
    flag_toggled = pyqtSignal(int)

    def __init__(self, total: int = 50, parent=None):
        super().__init__(parent)
        self._total    = total
        self._current  = 0
        self._answered : set[int] = set()
        self._flagged  : set[int] = set()
        self._buttons  : list[QPushButton] = []
        self._build(total)

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build(self, total: int):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(6)

        # Scrollable grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)

        for i in range(total):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(PALETTE_BUTTON_SZ, PALETTE_BUTTON_SZ)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setToolTip(f"Question {i+1}")
            btn.setStyleSheet(_btn_stylesheet("not_visited"))
            btn.clicked.connect(lambda _, idx=i: self.jump_to.emit(idx))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda _, idx=i: self._right_click(idx)
            )
            row, col = divmod(i, PALETTE_COLUMNS)
            grid.addWidget(btn, row, col)
            self._buttons.append(btn)

        scroll.setWidget(grid_widget)
        outer.addWidget(scroll)
        outer.addWidget(self._make_legend())

    def _make_legend(self) -> QWidget:
        w = QFrame()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(3)

        items = [
            ("#ffffff", "#e0e0e0", "Not Visited"),
            ("#3498db", "#3498db", "Current"),
            ("#27ae60", "#27ae60", "Answered"),
            ("#f39c12", "#f39c12", "Flagged"),
        ]
        for bg, border, label in items:
            row = QHBoxLayout()
            dot = QLabel()
            dot.setFixedSize(14, 14)
            dot.setStyleSheet(
                f"background:{bg}; border:1px solid {border}; border-radius:3px;"
            )
            txt = QLabel(label)
            txt.setFont(QFont("Segoe UI", 10))
            txt.setStyleSheet("color: #7f8c8d;")
            row.addWidget(dot)
            row.addWidget(txt)
            row.addStretch()
            layout.addLayout(row)
        return w

    # ─── Public API ───────────────────────────────────────────────────────────

    def set_current(self, index: int):
        prev = self._current
        self._current = index
        self._refresh_button(prev)
        self._refresh_button(index)

    def mark_answered(self, index: int):
        self._answered.add(index)
        self._refresh_button(index)

    def unmark_answered(self, index: int):
        self._answered.discard(index)
        self._refresh_button(index)

    def toggle_flag(self, index: int):
        if index in self._flagged:
            self._flagged.discard(index)
        else:
            self._flagged.add(index)
        self._refresh_button(index)

    def is_flagged(self, index: int) -> bool:
        return index in self._flagged

    # ─── Private ──────────────────────────────────────────────────────────────

    def _right_click(self, index: int):
        self.toggle_flag(index)
        self.flag_toggled.emit(index)

    def _refresh_button(self, index: int):
        if index < 0 or index >= len(self._buttons):
            return
        answered = index in self._answered
        flagged  = index in self._flagged
        current  = index == self._current

        if current:
            state = "current"
        elif answered and flagged:
            state = "answered_flagged"
        elif answered:
            state = "answered"
        elif flagged:
            state = "flagged"
        else:
            state = "not_visited"

        self._buttons[index].setStyleSheet(_btn_stylesheet(state))
        tip_parts = [f"Question {index+1}"]
        if answered: tip_parts.append("Answered")
        if flagged:  tip_parts.append("Flagged ⚑")
        self._buttons[index].setToolTip(" · ".join(tip_parts))
