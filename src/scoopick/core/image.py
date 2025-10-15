from PySide6.QtGui import QMouseEvent, QPixmap, QIcon, QResizeEvent

from ..data import Point


class ScreenImage:
    def __init__(self, pixmap: QPixmap):
        self._pixmap = pixmap

    def get_pixel_color(self, point: Point) -> QIcon:
        if self._pixmap.isNull():
            return QIcon()
        image = self._pixmap.toImage()
        color = image.pixelColor(point.x, point.y)
        return color.red(), color.green(), color.blue()

    @property
    def pixmap(self) -> QPixmap:
        return self._pixmap

    @pixmap.setter
    def pixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap

    @property
    def is_null(self) -> bool:
        return self._pixmap.isNull()

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    @property
    def width(self) -> int:
        if self._pixmap.isNull():
            return 0
        return self._pixmap.size().width()

    @property
    def height(self) -> int:
        if self._pixmap.isNull():
            return 0
        return self._pixmap.size().height()
