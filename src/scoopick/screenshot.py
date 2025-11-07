import os
import sys
from logging import getLogger


from PySide6.QtCore import QObject, SLOT, Slot, Signal
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage
from PySide6.QtGui import QGuiApplication, QPixmap

logger = getLogger(__name__)


class Screenshot(QObject):
    screenshotted = Signal(QPixmap, name="screenshotted")

    def __init__(self):
        super().__init__()
        # Check if running on Wayland and on Linux
        self._wayland = "WAYLAND_DISPLAY" in os.environ and sys.platform.startswith("linux")

    def screenshot(self):
        if self._wayland:
            self._screenshot_wayland()
        else:
            screen = QGuiApplication.primaryScreen()
            self.screenshotted.emit(screen.grabWindow(0))

    def _check_portal_response(self, response, error_message):
        if response.type() in (QDBusMessage.MessageType.ErrorMessage, QDBusMessage.MessageType.InvalidMessage):
            logger.error("Error taking screenshot: %s", error_message)
            return False
        return True

    @Slot("uint", "QVariantMap")
    def response_callback(self, status, response):
        logger.debug("Received response: %d, with results: %s", status, response)
        if status == 0:
            image_path = response.get("uri", "").replace("file://", "")
            image = QPixmap()
            image.load(image_path)
            os.remove(image_path)
            self.screenshotted.emit(image)

    def _screenshot_wayland(self):
        service = "org.freedesktop.portal.Desktop"
        path = "/org/freedesktop/portal/desktop"
        iface = "org.freedesktop.portal.Screenshot"

        logger.info("Taking screenshot via portal...")
        iface = QDBusInterface(service, path, interface=iface, connection=QDBusConnection.sessionBus())
        screenshot_response = iface.call("Screenshot", "", {"interactive": False, "handle_token": "scoopick"})
        if not self._check_portal_response(screenshot_response, "Failed to call Screenshot method"):
            return

        QDBusConnection.sessionBus().connect(
            "",
            screenshot_response.arguments()[0].path(),
            "org.freedesktop.portal.Request",
            "Response",
            self,
            SLOT("response_callback(uint, QVariantMap)"),
        )
