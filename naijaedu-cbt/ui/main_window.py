"""
NaijaEdu CBT - Main Window
Orchestrates the sidebar, screen stack, and all inter-screen navigation.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
    QMessageBox, QStatusBar,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent

from ui.components.sidebar import Sidebar
from ui.screens.login_screen     import LoginScreen
from ui.screens.register_screen  import RegisterScreen
from ui.screens.dashboard        import Dashboard
from ui.screens.subject_selection import SubjectSelection
from ui.screens.test_engine      import TestEngine
from ui.screens.results_screen   import ResultsScreen
from ui.screens.history_screen   import HistoryScreen

from config import (
    APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    WINDOW_DEF_WIDTH, WINDOW_DEF_HEIGHT,
)


class MainWindow(QMainWindow):

    def __init__(self, db):
        super().__init__()
        self._db = db

        # State
        self._current_user_id   : int  = -1
        self._current_user_data : dict = {}
        self._current_test_sub  : str  = ""
        self._current_test_type : str  = ""

        self._setup_window()
        self._build_ui()
        self._connect_signals()
        self.switch_screen("login")

    # ─── Window Setup ─────────────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEF_WIDTH, WINDOW_DEF_HEIGHT)
        self.statusBar().showMessage("Ready")

    # ─── Build UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        h = QHBoxLayout(central)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar()
        self._sidebar.navigate.connect(self.switch_screen)
        self._sidebar.logout.connect(self._logout)
        h.addWidget(self._sidebar)

        # Screen stack
        self._stack = QStackedWidget()
        h.addWidget(self._stack, 1)

        # Instantiate all screens
        self._screens: dict[str, QWidget] = {}
        self._login_screen    = LoginScreen(self._db)
        self._register_screen = RegisterScreen(self._db)
        self._dashboard       = Dashboard(self._db)
        self._subject_sel     = SubjectSelection(self._db)
        self._test_engine     = TestEngine(self._db)
        self._results_screen  = ResultsScreen(self._db)
        self._history_screen  = HistoryScreen(self._db)

        for name, widget in [
            ("login",    self._login_screen),
            ("register", self._register_screen),
            ("dashboard",self._dashboard),
            ("subjects", self._subject_sel),
            ("test",     self._test_engine),
            ("results",  self._results_screen),
            ("history",  self._history_screen),
        ]:
            self._stack.addWidget(widget)
            self._screens[name] = widget

    # ─── Signal Wiring ────────────────────────────────────────────────────────

    def _connect_signals(self):
        # Login
        self._login_screen.login_success.connect(self._on_login)
        self._login_screen.navigate_register.connect(
            lambda: self.switch_screen("register")
        )

        # Register
        self._register_screen.register_success.connect(self._on_login)
        self._register_screen.navigate_login.connect(
            lambda: self.switch_screen("login")
        )

        # Dashboard
        self._dashboard.start_test.connect(lambda: self.switch_screen("subjects"))
        self._dashboard.view_history.connect(lambda: self.switch_screen("history"))

        # Subject selection
        self._subject_sel.start_test.connect(self._on_start_test)

        # Test engine
        self._test_engine.test_completed.connect(self._on_test_complete)
        self._test_engine.exit_to_dash.connect(lambda: self.switch_screen("dashboard"))

        # Results
        self._results_screen.back_to_dash.connect(lambda: self.switch_screen("dashboard"))
        self._results_screen.retake_test.connect(self._retake)
        self._results_screen.review_answers.connect(
            lambda _: None  # already loaded in results screen
        )

        # History
        self._history_screen.view_session.connect(self._view_session)

    # ─── Navigation ───────────────────────────────────────────────────────────

    def switch_screen(self, name: str, **kwargs):
        widget = self._screens.get(name)
        if widget is None:
            return

        # Show/hide sidebar
        auth_screens = {"login", "register"}
        self._sidebar.setVisible(name not in auth_screens)
        if name not in auth_screens:
            self._sidebar.set_active(name)

        self._stack.setCurrentWidget(widget)

        # Screen-specific refresh
        if name == "dashboard" and self._current_user_id != -1:
            self._dashboard.load_user(self._current_user_id)
        elif name == "history" and self._current_user_id != -1:
            self._history_screen.load_user(self._current_user_id)

    # ─── Event Handlers ───────────────────────────────────────────────────────

    def _on_login(self, user_id: int):
        self._current_user_id = user_id
        user = self._db.get_user_by_id(user_id)
        if user:
            self._current_user_data = user
            self._sidebar.set_user(user["full_name"])
        self.switch_screen("dashboard")
        self.show_notification(f"Welcome back, {user['full_name'].split()[0]}! 👋")

    def _logout(self):
        if self._test_engine.is_test_active():
            reply = QMessageBox.question(
                self, "Exam in Progress",
                "You have an active exam. Leaving will abandon it. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            self._db.abandon_test_session(self._test_engine._session_id)

        self._current_user_id   = -1
        self._current_user_data = {}
        self._login_screen.reset()
        self.switch_screen("login")
        self.show_notification("Logged out successfully.")

    def _on_start_test(self, subject: str, exam_type: str):
        self._current_test_sub  = subject
        self._current_test_type = exam_type
        self.switch_screen("test")
        self._test_engine.start_session(
            self._current_user_id, subject, exam_type
        )

    def _on_test_complete(self, session_id: int):
        self._results_screen.load_session(session_id)
        self.switch_screen("results")

    def _retake(self):
        if self._current_test_sub and self._current_test_type:
            self._on_start_test(self._current_test_sub, self._current_test_type)
        else:
            self.switch_screen("subjects")

    def _view_session(self, session_id: int):
        self._results_screen.load_session(session_id)
        self.switch_screen("results")

    # ─── Utilities ────────────────────────────────────────────────────────────

    def set_user(self, user_id: int):
        self._current_user_id = user_id
        user = self._db.get_user_by_id(user_id)
        if user:
            self._current_user_data = user
            self._sidebar.set_user(user["full_name"])

    def show_notification(self, message: str, msg_type: str = "info"):
        self.statusBar().showMessage(message, 5000)

    # ─── Close Guard ──────────────────────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent):
        if self._test_engine.is_test_active():
            reply = QMessageBox.question(
                self, "Exam in Progress",
                "You have an active exam. Closing will abandon it.\nAre you sure?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                event.ignore()
                return
            self._db.abandon_test_session(self._test_engine._session_id)
        self._db.close()
        event.accept()
