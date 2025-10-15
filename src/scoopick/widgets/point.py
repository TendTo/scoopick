from PySide6.QtWidgets import QListWidgetItem
from scoopick.data import Point


class PointWidget(QListWidgetItem):
    def __init__(self, point: Point, parent=None):
        super().__init__(parent)
        self.setText(str(point))
        self.setData(QListWidgetItem.ItemType.UserType, point)

    def get_point(self) -> Point:
        return self.data(QListWidgetItem.ItemType.UserType)
