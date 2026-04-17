"""
NaijaEdu CBT - Timer Widget
Countdown timer with color-coded warning states and pulse animation.
"""

from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QVariantAnimation
from PyQt5.QtGui import QFont

from config import TIMER_WARNING_THRESHOLD, TIMER_DANGER_THRESHOLD
from utils.helpers import format_time_hms


class TimerWidget(QLabel):
    time_up = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("00:00:00", parent)
        self._remaining = 0
        self._elapsed   = 0
        self._running   = False
        self._pulse_on  = False

        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Courier New", 32, QFont.Bold))
        self.setFixedHeight(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._apply_style("normal")

        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.setInterval(1000)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._toggle_pulse)
        self._pulse_timer.setInterval(500)

    # ─── Public API ───────────────────────────────────────────────────────────

    def set_time(self, seconds: int):
        self._remaining = max(0, int(seconds))
        self._elapsed   = 0
        self._update_display()

    def start(self):
        if not self._running:
            self._running = True
            self._tick_timer.start()

    def stop(self):
        self._running = False
        self._tick_timer.stop()
        self._pulse_timer.stop()

    def get_elapsed_seconds(self) -> int:
        return self._elapsed

    # ─── Private ──────────────────────────────────────────────────────────────

    def _tick(self):
        if self._remaining <= 0:
            self.stop()
            self._update_display()
            self.time_up.emit()
            return
        self._remaining -= 1
        self._elapsed   += 1
        self._update_display()
        self._update_state()

    def _update_display(self):
        self.setText(format_time_hms(self._remaining))

    def _update_state(self):
        if self._remaining <= TIMER_DANGER_THRESHOLD:
            self._apply_style("danger")
            if not self._pulse_timer.isActive():
                self._pulse_timer.start()
        elif self._remaining <= TIMER_WARNING_THRESHOLD:
            self._apply_style("warning")
            self._pulse_timer.stop()
            self._pulse_on = False
        else:
            self._apply_style("normal")
            self._pulse_timer.stop()
            self._pulse_on = False

    def _apply_style(self, state: str):
        colors = {
            "normal" : ("#2c3e50", "#f8f9fa"),
            "warning": ("#f39c12", "#fff8e1"),
            "danger" : ("#e74c3c", "#fdecea"),
        }
        fg, bg = colors.get(state, colors["normal"])
        self.setStyleSheet(f"""
            QLabel {{
                color: {fg};
                background-color: {bg};
                border-radius: 8px;
                padding: 10px 20px;
                font-family: 'Courier New', monospace;
                font-size: 32px;
                font-weight: bold;
            }}
        """)

    def _toggle_pulse(self):
        """Alternate opacity for pulse effect in danger state."""
        self._pulse_on = not self._pulse_on
        opacity = "0.5" if self._pulse_on else "1.0"
        fg, bg = "#e74c3c", "#fdecea"
        self.setStyleSheet(f"""
            QLabel {{
                color: {fg};
                background-color: {bg};
                border-radius: 8px;
                padding: 10px 20px;
                font-family: 'Courier New', monospace;
                font-size: 32px;
                font-weight: bold;
                opacity: {opacity};
            }}
        """)
