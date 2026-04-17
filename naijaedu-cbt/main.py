#!/usr/bin/env python3
"""
NaijaEdu CBT Application
A Computer-Based Testing application for Nigerian secondary school students.
Supports JAMB (UTME) and WAEC exam preparation.
"""

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from config import APP_NAME, APP_VERSION, APP_ORG, DATA_DIR, STYLESHEET_PATH


def setup_application() -> QApplication:
    """Initialise QApplication with HiDPI and font settings."""
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG)
    app.setStyle("Fusion")

    # Prefer Segoe UI on Windows, fall back gracefully on Linux
    font_family = "Segoe UI" 
    app.setFont(QFont(font_family, 10))

    return app


def initialise_database() -> DatabaseManager:
    """Create data directory and initialise SQLite database."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        db = DatabaseManager()
        print(f"[OK] Database ready at: {DATA_DIR / 'naijaedu.db'}")
        return db
    except Exception as exc:
        QMessageBox.critical(
            None,
            "Database Error",
            f"Failed to initialise database:\n{exc}",
        )
        sys.exit(1)


def load_stylesheet(app: QApplication) -> None:
    """Apply QSS stylesheet if it exists."""
    if STYLESHEET_PATH.exists():
        try:
            with open(STYLESHEET_PATH, "r") as f:
                app.setStyleSheet(f.read())
            print(f"[OK] Stylesheet loaded from {STYLESHEET_PATH}")
        except Exception as exc:
            print(f"[WARN] Could not load stylesheet: {exc}")
    else:
        print(f"[WARN] Stylesheet not found at {STYLESHEET_PATH}")


def main() -> None:
    print(f"Starting {APP_NAME} v{APP_VERSION} …")

    app = setup_application()
    db  = initialise_database()
    load_stylesheet(app)

    window = MainWindow(db)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
