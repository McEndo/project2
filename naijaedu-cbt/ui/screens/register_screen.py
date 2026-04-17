"""
NaijaEdu CBT - Register Screen
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea,
    QProgressBar, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from utils.validators import (
    validate_username, validate_password, validate_full_name,
    validate_email, validate_exam_number, validate_confirm_password,
    password_strength,
)


class RegisterScreen(QWidget):
    register_success  = pyqtSignal(int)   # user_id
    navigate_login    = pyqtSignal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db = db
        self._build_ui()

    # ─── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("background-color: #f8f9fa;")

        # Outer scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        v = QVBoxLayout(container)
        v.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        v.setContentsMargins(20, 40, 20, 40)

        card = QFrame()
        card.setFixedWidth(460)
        card.setObjectName("regCard")
        card.setStyleSheet("""
            QFrame#regCard {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(14)

        # Header
        logo = QLabel("NAIJAEDU CBT")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Segoe UI", 20, QFont.Bold))
        logo.setStyleSheet("color: #27ae60;")
        layout.addWidget(logo)

        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        layout.addSpacing(6)

        # Fields
        fields = [
            ("full_name",    "👤  Full Name",       False, "Full Name"),
            ("username",     "🆔  Username",         False, "Username"),
            ("email",        "📧  Email (optional)", False, "Email"),
            ("exam_number",  "🎓  Exam Number",      False, "e.g. 12345678AB"),
            ("password",     "🔒  Password",         True,  "Password"),
            ("confirm_pw",   "🔒  Confirm Password", True,  "Confirm Password"),
        ]
        self._inputs: dict[str, QLineEdit] = {}
        self._errs  : dict[str, QLabel]    = {}

        for key, label_text, is_pw, placeholder in fields:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #2c3e50; font-size: 13px; font-weight: 600;")
            layout.addWidget(lbl)

            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedHeight(44)
            inp.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #e0e0e0; border-radius: 6px;
                    padding: 0 12px; font-size: 14px; color: #2c3e50; background: white;
                }
                QLineEdit:focus { border-color: #27ae60; }
            """)
            if is_pw:
                inp.setEchoMode(QLineEdit.Password)
            layout.addWidget(inp)
            self._inputs[key] = inp

            # Password strength bar
            if key == "password":
                self._strength_bar = QProgressBar()
                self._strength_bar.setFixedHeight(6)
                self._strength_bar.setTextVisible(False)
                self._strength_bar.setRange(0, 3)
                self._strength_bar.setValue(0)
                self._strength_bar.setStyleSheet("""
                    QProgressBar { border: none; background: #e0e0e0; border-radius: 3px; }
                    QProgressBar::chunk { border-radius: 3px; background: #e74c3c; }
                """)
                layout.addWidget(self._strength_bar)
                self._strength_lbl = QLabel("")
                self._strength_lbl.setStyleSheet("font-size: 11px; color: #7f8c8d;")
                layout.addWidget(self._strength_lbl)
                inp.textChanged.connect(self._update_strength)

            err = QLabel()
            err.setStyleSheet("color: #e74c3c; font-size: 12px;")
            err.setVisible(False)
            layout.addWidget(err)
            self._errs[key] = err

        # Username availability hint
        self._inputs["username"].textChanged.connect(self._check_username_live)

        # Register button
        self._reg_btn = QPushButton("Create Account")
        self._reg_btn.setFixedHeight(50)
        self._reg_btn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self._reg_btn.setCursor(Qt.PointingHandCursor)
        self._reg_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60; color: white;
                border: none; border-radius: 6px;
            }
            QPushButton:hover   { background: #229954; }
            QPushButton:disabled{ background: #bdc3c7; }
        """)
        self._reg_btn.clicked.connect(self._attempt_register)
        layout.addWidget(self._reg_btn)

        # Login link
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.addWidget(QLabel("Already have an account?"))
        login_btn = QPushButton("Sign In")
        login_btn.setFlat(True)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet(
            "color: #3498db; border: none; background: transparent; font-size: 13px;"
        )
        login_btn.clicked.connect(self.navigate_login.emit)
        row.addWidget(login_btn)
        layout.addLayout(row)

        v.addWidget(card)

    # ─── Validation ───────────────────────────────────────────────────────────

    def _check_username_live(self, text: str):
        if len(text) >= 3 and self._db.username_exists(text.strip()):
            self._show_err("username", "Username already taken.")
        else:
            self._clear_err("username")

    def _update_strength(self, text: str):
        lvl = password_strength(text)
        vals = {"weak": (1, "#e74c3c", "Weak"), "medium": (2, "#f39c12", "Medium"), "strong": (3, "#27ae60", "Strong")}
        v, color, label = vals.get(lvl, (0, "#e74c3c", ""))
        self._strength_bar.setValue(v)
        self._strength_bar.setStyleSheet(f"""
            QProgressBar {{ border: none; background: #e0e0e0; border-radius: 3px; }}
            QProgressBar::chunk {{ border-radius: 3px; background: {color}; }}
        """)
        self._strength_lbl.setText(f"Strength: {label}" if text else "")

    def _show_err(self, key: str, msg: str):
        self._errs[key].setText(msg)
        self._errs[key].setVisible(True)

    def _clear_err(self, key: str):
        self._errs[key].setVisible(False)

    def _attempt_register(self):
        # Hide all errors
        for err in self._errs.values():
            err.setVisible(False)

        data = {k: w.text().strip() for k, w in self._inputs.items()}
        valid = True

        checks = [
            ("full_name",   validate_full_name(data["full_name"])),
            ("username",    validate_username(data["username"])),
            ("email",       validate_email(data["email"])),
            ("exam_number", validate_exam_number(data["exam_number"])),
            ("password",    validate_password(data["password"])),
            ("confirm_pw",  validate_confirm_password(data["password"], data["confirm_pw"])),
        ]
        for key, (ok, msg) in checks:
            if not ok:
                self._show_err(key, msg)
                valid = False

        if not valid:
            return

        # DB uniqueness
        if self._db.username_exists(data["username"]):
            self._show_err("username", "Username already taken.")
            return
        if data["exam_number"] and self._db.exam_number_exists(data["exam_number"]):
            self._show_err("exam_number", "Exam number already registered.")
            return

        try:
            uid = self._db.create_user(
                username    = data["username"],
                password    = data["password"],
                full_name   = data["full_name"],
                exam_number = data["exam_number"] or None,
                email       = data["email"] or None,
            )
            self.register_success.emit(uid)
        except Exception as e:
            self._show_err("username", f"Registration failed: {e}")

    def reset(self):
        for inp in self._inputs.values():
            inp.clear()
        for err in self._errs.values():
            err.setVisible(False)
