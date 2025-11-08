from logging import (
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    Logger,
    StreamHandler,
    getLogger,
)
from typing import TYPE_CHECKING

from pyqttoast import Toast, ToastPreset
from pyqttoast.toast_enums import ToastPosition

from ..data import PACKAGE_NAME

if TYPE_CHECKING:
    from scoopick.app import App


class CustomHandler(StreamHandler):

    def __init__(self, app: "App", stream=None):
        super().__init__(stream)
        self._app = app

    def emit(self, record):
        super().emit(record)
        if record.levelno == DEBUG:
            return  # Do not show toasts for debug messages
        title = "Notification"
        preset = ToastPreset.INFORMATION
        if record.levelno >= INFO:
            title = "Info"
            preset = ToastPreset.INFORMATION
        if record.levelno >= WARNING:
            title = "Warning"
            preset = ToastPreset.WARNING
        if record.levelno >= ERROR:
            title = "Error"
            preset = ToastPreset.ERROR
        self.show_toast(text=record.message, title=title, preset=preset)

    def show_toast(
        self, text: str, title: str = "", preset: ToastPreset = ToastPreset.INFORMATION, duration: int = 5000
    ):
        toast = Toast(self._app)
        toast.applyPreset(preset)  # Apply style preset
        toast.setDuration(duration)
        toast.setTitle(title)
        toast.setText(text)
        toast.setPosition(ToastPosition.BOTTOM_RIGHT)
        toast.show()


def init_logger(app: "App", log_level: int = DEBUG) -> Logger:
    """Initialize and configure the logger for the application."""
    logger = getLogger(PACKAGE_NAME)
    logger.setLevel(log_level)

    custom_handler = CustomHandler(app=app)
    formatter = Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    custom_handler.setFormatter(formatter)

    logger.addHandler(custom_handler)
    return logger
