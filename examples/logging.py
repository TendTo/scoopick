from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from PySide6.QtGui import QPixmap

    from scoopick.data import Point

logger = getLogger("scoopick")


def run(points: "list[Point]", capture_screenshot: "Callable[[], QPixmap]"):
    logger.info("Running script with points: %s", points)
