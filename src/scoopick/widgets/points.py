from PySide6.QtWidgets import QListView
from PySide6.QtCore import QItemSelection, QModelIndex, Qt, Signal

from scoopick.data.point import Point


class PointsWidget(QListView):
    point_selected = Signal(object, name="pointSelected")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)

    def selected_rows(self, selection: QItemSelection | list[QModelIndex]) -> tuple[Point]:
        if isinstance(selection, QItemSelection):
            selection = selection.indexes()
        selected_points = tuple(
            self.model().data(index, Qt.ItemDataRole.UserRole) for index in selection if index.isValid()
        )
        return selected_points

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        super().selectionChanged(selected, deselected)
        self.point_selected.emit(self.selected_rows(selected))
