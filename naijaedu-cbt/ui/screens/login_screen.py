"""
NaijaEdu CBT - Login Screen
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QFrame, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont

from utils.validators import validate_login_password


class LoginScreen(QWidget):
    login_success    = pyqtSignal(int)   # user_id
    navigate_register = pyqtSignal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db = db
        self._build_ui()

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Full-page background
        self.setStyleSheet("background-color: #f8f9fa;")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card.setObjectName("loginCard")
        card.setStyleSheet("""
            QFrame#loginCard {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        # Logo
        logo = QLabel("NAIJAEDU CBT")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        logo.setStyleSheet("color: #27ae60;")
        layout.addWidget(logo)

        # Title
        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        subtitle = QLabel("Sign in to continue your preparation")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # Username
        self._username = self._make_input("👤  Username")
        layout.addWidget(self._username)
        self._username_err = self._make_err()
        layout.addWidget(self._username_err)

        # Password
        pw_row = QHBoxLayout()
        self._password = self._make_input("🔒  Password", password=True)
        pw_row.addWidget(self._password)
        self._eye_btn = QPushButton("👁")
        self._eye_btn.setFixedSize(40, 45)
        self._eye_btn.setCheckable(True)
        self._eye_btn.setCursor(Qt.PointingHandCursor)
        self._eye_btn.setStyleSheet(
            "border: 1px solid #e0e0e0; border-radius: 6px; background: #f8f9fa;"
        )
        self._eye_btn.toggled.connect(self._toggle_pw)
        pw_row.addWidget(self._eye_btn)
        layout.addLayout(pw_row)
        self._pw_err = self._make_err()
        layout.addWidget(self._pw_err)

        # Remember me
        self._remember = QCheckBox("Remember me")
        self._remember.setStyleSheet("color: #2c3e50; font-size: 13px;")
        layout.addWidget(self._remember)

        # Login button
        self._login_btn = QPushButton("Sign In")
        self._login_btn.setFixedHeight(50)
        self._login_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self._login_btn.setCursor(Qt.PointingHandCursor)
        self._login_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60; color: white;
                border: none; border-radius: 6px;
            }
            QPushButton:hover  { background: #229954; }
            QPushButton:pressed{ background: #1e8449; }
        """)
        self._login_btn.clicked.connect(self._attempt_login)
        layout.addWidget(self._login_btn)

        # General error
        self._general_err = self._make_err()
        self._general_err.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._general_err)

        # Register link
        reg_row = QHBoxLayout()
        reg_row.setAlignment(Qt.AlignCenter)
        reg_lbl = QLabel("Don't have an account?")
        reg_lbl.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        reg_btn = QPushButton("Register")
        reg_btn.setFlat(True)
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.setStyleSheet(
            "color: #3498db; font-size: 13px; border: none; background: transparent;"
        )
        reg_btn.clicked.connect(self.navigate_register.emit)
        reg_row.addWidget(reg_lbl)
        reg_row.addWidget(reg_btn)
        layout.addLayout(reg_row)

        outer.addWidget(card)

        # Enter key
        self._username.returnPressed.connect(self._password.setFocus)
        self._password.returnPressed.connect(self._attempt_login)

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _make_input(placeholder: str, password: bool = False) -> QLineEdit:
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        w.setFixedHeight(45)
        w.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0; border-radius: 6px;
                padding: 0 12px; font-size: 14px; color: #2c3e50;
                background: white;
            }
            QLineEdit:focus { border-color: #27ae60; }
        """)
        if password:
            w.setEchoMode(QLineEdit.Password)
        return w

    @staticmethod
    def _make_err() -> QLabel:
        lbl = QLabel()
        lbl.setStyleSheet("color: #e74c3c; font-size: 12px;")
        lbl.setVisible(False)
        return lbl

    def _toggle_pw(self, checked: bool):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self._password.setEchoMode(mode)

    def _clear_errors(self):
        for lbl in (self._username_err, self._pw_err, self._general_err):
            lbl.setVisible(False)

    # ─── Logic ────────────────────────────────────────────────────────────────

    def _attempt_login(self):
        self._clear_errors()
        username = self._username.text().strip()
        password = self._password.text()

        valid = True
        if not username or len(username) < 3:
            self._username_err.setText("Username must be at least 3 characters.")
            self._username_err.setVisible(True)
            valid = False

        ok, msg = validate_login_password(password)
        if not ok:
            self._pw_err.setText(msg)
            self._pw_err.setVisible(True)
            valid = False

        if not valid:
            return

        user = self._db.authenticate_user(username, password)
        if user:
            self.login_success.emit(user["id"])
        else:
            self._general_err.setText("❌  Invalid username or password.")
            self._general_err.setVisible(True)
            self._shake()

    def _shake(self):
        """Brief horizontal shake on wrong credentials."""
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(300)
        pos = self.pos()
        anim.setKeyValueAt(0.0, pos)
        anim.setKeyValueAt(0.2, pos.__class__(pos.x() - 10, pos.y()))
        anim.setKeyValueAt(0.4, pos.__class__(pos.x() + 10, pos.y()))
        anim.setKeyValueAt(0.6, pos.__class__(pos.x() - 8,  pos.y()))
        anim.setKeyValueAt(0.8, pos.__class__(pos.x() + 8,  pos.y()))
        anim.setKeyValueAt(1.0, pos)
        anim.start()
        self._anim = anim  # keep reference

    def reset(self):
        self._username.clear()
        self._password.clear()
        self._clear_errors()
