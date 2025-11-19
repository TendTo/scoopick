from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scoopick.data import Point
    from typing import Callable
    from PySide6.QtGui import QPixmap

logger = getLogger("scoopick")


def run(points: "list[Point]", capture_screenshot: "Callable[[], QPixmap]"):
    logger.info("Running script with points: %s", points)
