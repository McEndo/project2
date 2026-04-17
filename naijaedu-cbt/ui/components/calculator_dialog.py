"""
NaijaEdu CBT - Scientific Calculator Dialog
"""

import math
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLineEdit, QPushButton,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeyEvent


class CalculatorDialog(QDialog):

    _BUTTONS = [
        # (label, role)   role: 'mem'|'func'|'op'|'num'|'eq'
        [("MC","mem"),  ("MR","mem"),   ("MS","mem"),  ("M+","mem"),   ("M-","mem")],
        [("←","func"),  ("CE","func"),  ("C","func"),  ("±","func"),   ("√","func")],
        [("7","num"),   ("8","num"),    ("9","num"),   ("/","op"),     ("%","op")  ],
        [("4","num"),   ("5","num"),    ("6","num"),   ("*","op"),     ("1/x","func")],
        [("1","num"),   ("2","num"),    ("3","num"),   ("-","op"),     ("x²","func")],
        [("0","num"),   (".","num"),    ("=","eq"),    ("+","op"),     ("","")     ],
    ]

    _ROLE_COLORS = {
        "mem" : "#e0e0e0",
        "func": "#e0e0e0",
        "op"  : "#f39c12",
        "num" : "#ffffff",
        "eq"  : "#27ae60",
        ""    : "transparent",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scientific Calculator")
        self.setFixedSize(320, 420)
        self.setModal(True)

        self._memory   : float = 0.0
        self._expr     : str   = ""
        self._new_num  : bool  = True
        self._pending_op: str  = ""
        self._pending_val: float = 0.0
        self._result   : float = 0.0

        self._build_ui()

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Display
        self._display = QLineEdit("0")
        self._display.setReadOnly(True)
        self._display.setAlignment(Qt.AlignRight)
        self._display.setFont(QFont("Courier New", 24, QFont.Bold))
        self._display.setStyleSheet("""
            QLineEdit {
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                color: #2c3e50;
            }
        """)
        self._display.setFixedHeight(55)
        layout.addWidget(self._display)

        # Button grid
        grid = QGridLayout()
        grid.setSpacing(5)

        for r, row in enumerate(self._BUTTONS):
            for c, (label, role) in enumerate(row):
                if not label:
                    continue
                btn = QPushButton(label)
                btn.setFixedSize(52, 52)
                btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
                bg = self._ROLE_COLORS.get(role, "#ffffff")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {bg};
                        border: 1px solid #e0e0e0;
                        border-radius: 6px;
                        color: #2c3e50;
                    }}
                    QPushButton:hover {{ background: {self._darken(bg)}; }}
                    QPushButton:pressed {{ background: #bdc3c7; }}
                """)
                btn.clicked.connect(lambda _, lbl=label, rl=role: self._on_btn(lbl, rl))
                grid.addWidget(btn, r, c)

        layout.addLayout(grid)

    # ─── Logic ────────────────────────────────────────────────────────────────

    def _current(self) -> float:
        try:
            return float(self._display.text())
        except ValueError:
            return 0.0

    def _show(self, value):
        text = str(value)
        if text.endswith(".0"):
            text = text[:-2]
        self._display.setText(text[:16])

    def _on_btn(self, label: str, role: str):
        val = self._current()

        if role == "num":
            if label == ".":
                cur = self._display.text()
                if self._new_num:
                    self._display.setText("0.")
                    self._new_num = False
                elif "." not in cur:
                    self._display.setText(cur + ".")
            else:
                if self._new_num:
                    self._display.setText(label)
                    self._new_num = False
                else:
                    cur = self._display.text()
                    if cur == "0":
                        self._display.setText(label)
                    else:
                        self._display.setText((cur + label)[:15])

        elif role == "op":
            self._apply_pending()
            self._pending_op  = label
            self._pending_val = self._current()
            self._new_num = True

        elif label == "=":
            self._apply_pending()
            self._pending_op = ""
            self._new_num = True

        elif label == "C":
            self._display.setText("0")
            self._pending_op  = ""
            self._pending_val = 0.0
            self._new_num = True

        elif label == "CE":
            self._display.setText("0")
            self._new_num = True

        elif label == "←":
            cur = self._display.text()
            self._display.setText(cur[:-1] if len(cur) > 1 else "0")

        elif label == "±":
            self._show(-val)

        elif label == "√":
            if val < 0:
                self._display.setText("Error")
            else:
                self._show(math.sqrt(val))
            self._new_num = True

        elif label == "x²":
            self._show(val ** 2)
            self._new_num = True

        elif label == "1/x":
            if val == 0:
                self._display.setText("Error")
            else:
                self._show(1 / val)
            self._new_num = True

        elif label == "%":
            self._show(val / 100)
            self._new_num = True

        elif role == "mem":
            self._handle_memory(label, val)

    def _apply_pending(self):
        if not self._pending_op:
            return
        b = self._current()
        a = self._pending_val
        try:
            if self._pending_op == "+":   result = a + b
            elif self._pending_op == "-": result = a - b
            elif self._pending_op == "*": result = a * b
            elif self._pending_op == "/":
                if b == 0:
                    self._display.setText("Error")
                    self._new_num = True
                    return
                result = a / b
            else:
                return
            self._show(result)
        except Exception:
            self._display.setText("Error")
        self._new_num = True

    def _handle_memory(self, label: str, val: float):
        if label == "MC":   self._memory = 0.0
        elif label == "MR": self._show(self._memory); self._new_num = True
        elif label == "MS": self._memory = val
        elif label == "M+": self._memory += val
        elif label == "M-": self._memory -= val

    def keyPressEvent(self, event: QKeyEvent):
        key = event.text()
        if key.isdigit() or key == ".":
            self._on_btn(key, "num")
        elif key in ("+", "-", "*", "/"):
            self._on_btn(key, "op")
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._on_btn("=", "eq")
        elif event.key() == Qt.Key_Backspace:
            self._on_btn("←", "func")
        elif event.key() == Qt.Key_Escape:
            self.close()

    @staticmethod
    def _darken(hex_color: str) -> str:
        """Very simple colour darkener for hover states."""
        _MAP = {
            "#e0e0e0"    : "#c8c8c8",
            "#f39c12"    : "#d68910",
            "#ffffff"    : "#f0f0f0",
            "#27ae60"    : "#219a52",
            "transparent": "#f0f0f0",
        }
        return _MAP.get(hex_color, hex_color)
