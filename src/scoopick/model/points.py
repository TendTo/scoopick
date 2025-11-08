import json
from dataclasses import asdict, replace
from logging import getLogger

from PySide6.QtCore import QAbstractListModel, QModelIndex
from PySide6.QtGui import Qt

from ..data import PACKAGE_NAME, Point, Schema, validate_data

logger = getLogger(PACKAGE_NAME)

DEFAULT_POINTS = (
    Point(idx=0, name="Point 1", x=-1, y=-1, color=(0, 255, 0)),
    Point(idx=1, name="Point 2", x=-1, y=-1, color=(255, 0, 0)),
    Point(idx=2, name="Point 3", x=-1, y=-1, color=(0, 0, 255)),
    Point(idx=3, name="Point 4", x=-1, y=-1, color=(0, 255, 255)),
    Point(idx=4, name="Point 5", x=-1, y=-1, color=(255, 255, 0)),
    Point(idx=5, name="Point 6", x=-1, y=-1, color=(255, 0, 255)),
)


class PointsModel(QAbstractListModel):
    def __init__(self, points: list[Point] | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._points: list[Point] = points or [replace(point) for point in DEFAULT_POINTS]
        self._selected_point: tuple[Point] = tuple()

    @classmethod
    def from_file(cls, filepath: str) -> "PointsModel":
        points_instance = cls()
        points_instance.load_from_file(filepath)
        return points_instance

    def load_from_file(self, filepath: str) -> bool:
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data: dict = json.load(f)
            except json.JSONDecodeError:
                return False
        if not validate_data(Schema.POINTS, data):
            return False
        self._points = [Point(**point_data) for point_data in data.get("points", [])]
        self.layoutChanged.emit()
        return True

    def to_file(self, filepath: str):
        data = {"points": [asdict(point) for point in self._points]}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def data(self, index: QModelIndex, role=...):
        point = self._points[index.row()]
        if role in (
            Qt.ItemDataRole.ToolTipRole,
            Qt.ItemDataRole.WhatsThisRole,
            Qt.ItemDataRole.DisplayRole,
        ):
            return str(point)
        if role == Qt.ItemDataRole.UserRole:
            return point
        return None

    def rowCount(self, index: QModelIndex):
        return len(self._points)

    def select_points(self, points: tuple[Point]):
        self._selected_point = points
        # self.layoutChanged.emit()

    def add_point(self, point: Point):
        point.idx = len(self._points)
        self._points.append(replace(point))
        self.layoutChanged.emit()

    def set_points(self, points: list[Point]):
        self._points = [replace(point) for point in points]
        self.layoutChanged.emit()

    def remove_point(self, point: Point):
        self._points.remove(point)
        self.layoutChanged.emit()

    def __getitem__(self, index: int) -> Point:
        return self._points[index]

    def __contains__(self, index: int) -> bool:
        return 0 <= index < len(self._points)

    @property
    def points(self):
        return self._points

    @property
    def selected_points(self) -> tuple[Point]:
        return self._selected_point

    def update_point(self, point: Point):
        self._points[point.idx].update(point)
        self.dataChanged.emit(self.index(point.idx), self.index(point.idx))

    def update_pos(self, point: Point):
        self._points[point.idx].x = point.x
        self._points[point.idx].y = point.y
        self.dataChanged.emit(self.index(point.idx), self.index(point.idx))
