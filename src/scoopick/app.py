# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
"""PySide6 port of the widgets/desktop/screenshot example from Qt v6.x"""

import importlib.util
import sys
from logging import getLogger

from PySide6 import QtGui
from PySide6.QtCore import QRect, Qt, QTimer, Slot
from PySide6.QtGui import QMouseEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from scoopick.core.controller import Controller
from scoopick.widgets.crosshair import CrosshairWidget

from .core import ScreenImage
from .data import Point
from .model import PointsModel
from .screenshot import Screenshot
from .widgets import PointsWidget

logger = getLogger(__name__)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scoopick")

        self.addAction(
            QtGui.QAction(
                "Quit",
                self,
                shortcut=Qt.Modifier.CTRL | Qt.Key.Key_W,
                triggered=QApplication.instance().quit,
            )
        )

        logger.setLevel("INFO")

        self._mod = None
        self._screenshot = Screenshot()
        self._screenshot.screenshotted.connect(self.on_screenshotted)

        self._points = PointsModel()

        screen_geometry: QRect = self.screen().geometry()

        main_layout = QVBoxLayout(self)

        self._screenshot_label = QLabel(self)
        self._screenshot_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._screenshot_label.setStyleSheet("QLabel { border: 2px dashed gray; }")
        self._screenshot_label.setMinimumSize(screen_geometry.width() / 8, screen_geometry.height() / 8)
        self._screenshot_label.mousePressEvent = self._on_mouse_pressed
        main_layout.addWidget(self._screenshot_label)

        points_group_box = QGroupBox("Points", self)
        points_layout = QVBoxLayout(points_group_box)
        points_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self._points_widget = PointsWidget()
        self._points_widget.setModel(self._points)
        # self._points_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._points_widget.setFixedHeight(
            self._points_widget.sizeHintForRow(0) * min(self._points.rowCount(0), 4)
            + 2 * self._points_widget.frameWidth()
        )
        # self._points_widget.setVerticalScrollBar(QScrollBar(self._points_widget))
        # self._points_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self._points_widget.point_selected.connect(self.on_point_selected)
        for point in self._points:
            ch = CrosshairWidget(point, self._points, self._screenshot_label)
            self._screenshot.screenshotted.connect(ch.on_update_screenshot)

        points_group_box.setFixedHeight(
            self._points_widget.height()
            + points_layout.spacing() * 2
            + points_layout.contentsMargins().top()
            + points_layout.contentsMargins().bottom()
        )
        points_layout.addWidget(self._points_widget)
        main_layout.addWidget(points_group_box)

        buttons_layout = QHBoxLayout()
        self._play_button = QPushButton("Start game", self)
        self._play_button.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_Enter)
        self._play_button.clicked.connect(self.start)
        self._play_button.setEnabled(False)
        buttons_layout.addWidget(self._play_button)
        self._load_script_button = QPushButton("Load script", self)
        self._load_script_button.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_L)
        self._load_script_button.clicked.connect(self.load_script)
        buttons_layout.addWidget(self._load_script_button)
        self._update_button = QPushButton("Update screenshot", self)
        self._update_button.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_S)
        self._update_button.clicked.connect(self.request_screenshot)
        buttons_layout.addWidget(self._update_button)
        self._load_button = QPushButton("Load points", self)
        self._load_button.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_O)
        self._load_button.clicked.connect(self.load_points)
        buttons_layout.addWidget(self._load_button)
        self._save_button = QPushButton("Save points", self)
        self._save_button.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_S)
        self._save_button.clicked.connect(self.save_points)
        buttons_layout.addWidget(self._save_button)
        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)

        self._pixmap = ScreenImage(QPixmap())

    def _mouse_to_screen_position(self, event: QMouseEvent):
        if self._pixmap.is_null:
            return -1, -1
        x, y = event.position().toPoint().x(), event.position().toPoint().y()
        width_label, height_label = (
            self._screenshot_label.size().width(),
            self._screenshot_label.size().height(),
        )
        width_pixmap, height_pixmap = self._pixmap.size
        y_offset = 0
        x_offset = 0
        if width_label / height_label > width_pixmap / height_pixmap:
            # black borders on left and right
            scale = height_label / height_pixmap
            x_offset = (width_label - width_pixmap * scale) / 2
        else:
            # black borders on top and bottom
            scale = width_label / width_pixmap
            y_offset = (height_label - height_pixmap * scale) / 2
        x_screen = (x - x_offset) / scale
        y_screen = (y - y_offset) / scale
        return int(x_screen), int(y_screen)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key.Key_Cancel, Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for point in self._points.selected_points:
                self._points.update_pos(Point(point.idx, point.name, -1, -1))

    def _on_mouse_pressed(self, event: QMouseEvent):
        x_screen, y_screen = self._mouse_to_screen_position(event)
        if not (0 <= x_screen < self._pixmap.width and 0 <= y_screen < self._pixmap.height):
            x_screen, y_screen = -1, -1
        for point in self._points.selected_points:
            self._points.update_pos(Point(point.idx, point.name, x_screen, y_screen))
        QToolTip.showText(
            self.mapToGlobal(event.position().toPoint()),
            f"{x_screen}, {y_screen}",
            self,
        )

    def resizeEvent(self, event: QResizeEvent):
        scaled_size = self._pixmap.pixmap.size()
        scaled_size.scale(self._screenshot_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        if scaled_size != self._screenshot_label.pixmap().size():
            self.update_screenshot_label()

    def _set_buttons_state(self, enabled: bool):
        self._play_button.setEnabled(enabled)
        self._update_button.setEnabled(enabled)

    @Slot(object)
    def on_point_selected(self, points: tuple[Point]):
        self._points.select_points(points)

    @Slot()
    def start(self):
        print("Starting game with points:", self._points.points)
        if self._mod is None:
            logger.error("No script loaded. Please load a script before starting the game.")
            return
        self.hide()
        try:
            self._mod.run(self._points.points)
        except Exception as e:
            logger.error("Failed to run script: %s", e)
        self.show()

    @Slot()
    def request_screenshot(self):
        self.hide()
        self._set_buttons_state(False)
        QTimer.singleShot(500, self.screenshot)

    @Slot()
    def on_screenshotted(self, pixmap: QPixmap):
        self._pixmap.pixmap = pixmap
        self.update_screenshot_label()
        self._set_buttons_state(True)
        self.show()

    @Slot()
    def load_script(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load script", "", "Python Files (*.py)")
        if filepath:
            logger.info("Loading script from file '%s'", filepath)
            if "script" in sys.modules:
                del sys.modules["script"]
            try:
                importlib.invalidate_caches()
            except Exception as e:
                logger.error("Failed to invalidate caches: %s", e)
            try:
                # Import the input file as a module
                spec = importlib.util.spec_from_file_location("script", filepath)
                self._mod = importlib.util.module_from_spec(spec)
                sys.modules["script"] = self._mod
                spec.loader.exec_module(self._mod)
                # Check if the module has a 'run' function
                if not hasattr(self._mod, "run") or not callable(self._mod.run):
                    logger.error("The configuration file must contain a function called 'run'")
                    self._mod = None
            except Exception as e:
                logger.error("Failed to load script: %s", e)
                self._mod = None
        else:
            logger.info("No file selected")
            self._mod = None
        self._play_button.setEnabled(self._mod is not None)

    @Slot()
    def load_points(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load points", "", "JSON Files (*.json)")
        if filepath:
            num_points_before = len(self._points.points)
            self._points.load_from_file(filepath)
            num_points_after = len(self._points.points)
            # The excess crosshair widgets will self-destruct on layout update
            # We just need to make sure to create new ones if we have more points than before
            for i in range(max(num_points_after - num_points_before, 0)):
                ch = CrosshairWidget(
                    self._points[num_points_before + i],
                    self._points,
                    self._screenshot_label,
                )
                self._screenshot.screenshotted.connect(ch.on_update_screenshot)
            self._points_widget.setFixedHeight(
                self._points_widget.sizeHintForRow(0) * self._points.rowCount(0) + 2 * self._points_widget.frameWidth()
            )
            logger.info("Loaded points from %s", filepath)

    @Slot()
    def save_points(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save points", "points.json", "JSON Files (*.json)")
        if filepath:
            self._points.to_file(filepath)
            logger.info("Saved points to %s", filepath)

    def screenshot(self):
        self._screenshot.screenshot()
        QApplication.beep()

    def update_screenshot_label(self):
        scaled_pixelmap = self._pixmap.pixmap.scaled(
            self._screenshot_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._screenshot_label.setPixmap(scaled_pixelmap)


def main():
    app = QApplication(sys.argv)
    screenshot = App()
    screenshot.showMaximized()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
