"""
NaijaEdu CBT - Sidebar Navigation Component
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush

from utils.helpers import initials_from_name


class _AvatarWidget(QLabel):
    """Circle with user initials."""

    def __init__(self, initials: str, parent=None):
        super().__init__(initials, parent)
        self.setFixedSize(40, 40)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.setStyleSheet(
            "color: white; background-color: #27ae60; border-radius: 20px;"
        )


class _NavButton(QPushButton):
    """Single sidebar nav item."""

    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(f"  {icon}  {label}", parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("navButton")
        self.setStyleSheet("""
            QPushButton#navButton {
                background: transparent;
                border: none;
                border-left: 4px solid transparent;
                text-align: left;
                padding-left: 15px;
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            QPushButton#navButton:hover {
                background: #f5f5f5;
            }
            QPushButton#navButton:checked {
                background: #e8f5e9;
                border-left: 4px solid #27ae60;
                color: #27ae60;
                font-weight: 600;
            }
        """)


class Sidebar(QWidget):
    navigate = pyqtSignal(str)   # screen name
    logout   = pyqtSignal()

    _NAV = [
        ("🏠", "Dashboard", "dashboard"),
        ("📝", "Take Test",  "subjects"),
        ("📊", "History",    "history"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setObjectName("sidebar")
        self.setStyleSheet("""
            QWidget#sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }
        """)
        self._buttons: dict[str, _NavButton] = {}
        self._build_ui()

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        layout.addWidget(self._make_logo())

        # Nav buttons
        for icon, label, screen in self._NAV:
            btn = _NavButton(icon, label)
            btn.clicked.connect(lambda _, s=screen, b=btn: self._on_nav(s, b))
            self._buttons[screen] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Logout
        logout_btn = _NavButton("🚪", "Logout")
        logout_btn.setObjectName("navButton")
        logout_btn.clicked.connect(self.logout.emit)
        layout.addWidget(logout_btn)

        # Profile card
        self._profile_card = self._make_profile_card()
        layout.addWidget(self._profile_card)

    def _make_logo(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(80)
        w.setStyleSheet("background: #27ae60;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.setAlignment(Qt.AlignCenter)

        top = QLabel("NAIJAEDU")
        top.setAlignment(Qt.AlignCenter)
        top.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top.setStyleSheet("color: white; background: transparent;")

        sub = QLabel("CBT")
        sub.setAlignment(Qt.AlignCenter)
        sub.setFont(QFont("Segoe UI", 16))
        sub.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")

        v.addWidget(top)
        v.addWidget(sub)
        return w

    def _make_profile_card(self) -> QWidget:
        card = QFrame()
        card.setFixedHeight(80)
        card.setStyleSheet("border-top: 1px solid #e0e0e0; background: white;")

        h = QHBoxLayout(card)
        h.setContentsMargins(15, 10, 15, 10)
        h.setSpacing(10)

        self._avatar   = _AvatarWidget("??")
        self._name_lbl = QLabel("Guest")
        self._name_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self._name_lbl.setStyleSheet("color: #2c3e50;")

        role = QLabel("Student")
        role.setStyleSheet(
            "background: #27ae60; color: white; border-radius: 4px;"
            "padding: 2px 8px; font-size: 11px;"
        )
        role.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        right = QVBoxLayout()
        right.setSpacing(2)
        right.addWidget(self._name_lbl)
        right.addWidget(role)

        h.addWidget(self._avatar)
        h.addLayout(right)
        return card

    # ─── Public API ───────────────────────────────────────────────────────────

    def set_active(self, screen: str):
        for key, btn in self._buttons.items():
            btn.setChecked(key == screen)

    def set_user(self, full_name: str):
        initials = initials_from_name(full_name)
        self._avatar.setText(initials)
        display = full_name.split()[0] if full_name else "Guest"
        self._name_lbl.setText(display)

    # ─── Private ──────────────────────────────────────────────────────────────

    def _on_nav(self, screen: str, btn: _NavButton):
        for b in self._buttons.values():
            b.setChecked(False)
        btn.setChecked(True)
        self.navigate.emit(screen)
