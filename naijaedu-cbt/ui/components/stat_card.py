"""
NaijaEdu CBT - Stat Card Component
"""

from typing import Optional
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class StatCard(QFrame):
    """
    Displays a single KPI stat with an icon, title, value and optional trend.
    """

    def __init__(
        self,
        title     : str,
        value     : str,
        icon      : str,
        icon_color: str = "#27ae60",
        trend     : Optional[str] = None,
        parent    = None,
    ):
        super().__init__(parent)
        self._icon_color = icon_color
        self.setObjectName("statCard")
        self.setMinimumSize(200, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QFrame#statCard {
                background: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        self._build(title, value, icon, trend)

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build(self, title, value, icon, trend):
        h = QHBoxLayout(self)
        h.setContentsMargins(15, 15, 15, 15)
        h.setSpacing(12)

        # Icon circle
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI", 18))
        icon_lbl.setStyleSheet(
            f"background: {self._icon_color}22; border-radius: 20px; color: {self._icon_color};"
        )

        # Text column
        col = QVBoxLayout()
        col.setSpacing(2)

        title_lbl = QLabel(title.upper())
        title_lbl.setFont(QFont("Segoe UI", 10))
        title_lbl.setStyleSheet("color: #7f8c8d;")

        self._value_lbl = QLabel(value)
        self._value_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self._value_lbl.setStyleSheet("color: #2c3e50;")

        col.addWidget(title_lbl)
        col.addWidget(self._value_lbl)

        if trend:
            trend_lbl = QLabel(trend)
            trend_lbl.setFont(QFont("Segoe UI", 10))
            color = "#27ae60" if trend.startswith("↑") else "#e74c3c"
            trend_lbl.setStyleSheet(f"color: {color};")
            col.addWidget(trend_lbl)

        h.addWidget(icon_lbl)
        h.addLayout(col)
        h.addStretch()

    # ─── Public API ───────────────────────────────────────────────────────────

    def set_value(self, value: str):
        self._value_lbl.setText(value)
