from logging import getLogger

from PySide6.QtCore import QModelIndex, QRect, QSize, Slot
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QWidget

logger = getLogger(__name__)

from scoopick.model.points import PointsModel

from ..data import Point


class CrosshairWidget(QWidget):

    def __init__(self, point: Point, points_model: PointsModel, *args, **kwargs):
        super().__init__(*args, size=QSize(40, 40), **kwargs)
        self._idx = point.idx
        self._points_model = points_model
        self._label: QLabel = self.parent()
        self._pixmap: QPixmap | None = None

        self._points_model.layoutChanged.connect(self.on_layout_update)
        self._points_model.dataChanged.connect(self.on_point_update)
        self.updateGeometry()

        logger.debug("Created CrosshairWidget for point idx=%d", self._idx)

    def set_model(self, points_model: PointsModel):
        self._points_model = points_model

    @property
    def _point(self) -> Point:
        return self._points_model[self._idx]

    @property
    def _selected(self) -> bool:
        for p in self._points_model.selected_points:
            if p.idx == self._idx:
                return True
        return False

    def _from_screen_to_label(self) -> tuple[int, int]:
        x, y = self._point.x, self._point.y
        if self._pixmap is None or self._pixmap.isNull():
            return -1, -1
        lw, lh = self._label.size().width(), self._label.size().height()
        scaled_pixmap_w, scaled_pixmap_h = (
            self._label.pixmap().size().width(),
            self._label.pixmap().size().height(),
        )
        pixmap_w, pixmap_h = self._pixmap.size().width(), self._pixmap.size().height()
        scale_x = scaled_pixmap_w / pixmap_w
        scale_y = scaled_pixmap_h / pixmap_h

        diff_x = (lw - scaled_pixmap_w) // 2
        diff_y = (lh - scaled_pixmap_h) // 2

        if scale_x > scale_y:
            scale_x = scale_y
        else:
            scale_y = scale_x
        return int(x * scale_x + diff_x), int(y * scale_y + diff_y)

    @Slot()
    def on_update_screenshot(self, pixmap: QPixmap):
        self._pixmap = pixmap
        if self._pixmap.isNull():
            return
        self.updateGeometry()

    def on_layout_update(self, *args):
        if self._idx not in self._points_model:
            logger.debug(
                "CrosshairWidget: point %d no longer in model, destroying widget %d",
                self._idx,
                id(self),
            )
            self._points_model.layoutChanged.disconnect(self.on_layout_update)
            self._points_model.dataChanged.disconnect(self.on_point_update)
            self.deleteLater()
        else:
            self.updateGeometry()

    def on_point_update(self, idx_from: QModelIndex, idx_to: QModelIndex):
        # Only update if our point is in the updated range
        if idx_from.row() <= self._idx <= idx_to.row():
            logger.debug(
                "CrosshairWidget: point %d updated, updating widget %d",
                self._idx,
                id(self),
            )
            self.updateGeometry()

    def updateGeometry(self):
        super().updateGeometry()
        x_label, y_label = self._from_screen_to_label()
        if x_label < 0 or y_label < 0:
            logger.debug(
                "CrosshairWidget: point %d is out of bounds, hiding widget %d",
                self._idx,
                id(self),
            )
            self.hide()
        else:
            self.show()
            self.move(x_label - self.width() // 2, y_label - self.height() // 2)
            logger.debug(
                "CrosshairWidget: point %d moved to (%d, %d) in widget %d",
                self._idx,
                x_label,
                y_label,
                id(self),
            )

    def paintEvent(self, event):
        super().paintEvent(event)
        try:
            point = self._point
        except IndexError:
            return
        if point.x < 0 or point.y < 0:
            return

        painter = QPainter(self)
        pen = QPen()
        pen.setColor(QColor(*point.color))
        painter.setPen(pen)
        painter.drawEllipse(QRect(self.width() // 2 - 2, self.height() // 2 - 2, 4, 4))
        painter.drawRect(QRect(self.width() // 2, 0, 1, self.height() // 2 - 5))
        painter.drawRect(QRect(self.width() // 2, self.height() // 2 + 5, 1, self.height() // 2 - 5))
        painter.drawRect(QRect(0, self.height() // 2, self.width() // 2 - 5, 1))
        painter.drawRect(QRect(self.width() // 2 + 5, self.height() // 2, self.width() // 2 - 5, 1))
        if self._selected:
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
