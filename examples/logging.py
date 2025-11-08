from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scoopick.data import Point

logger = getLogger("scoopick")

def run(points: "list[Point]"):
    logger.info("Running script with points: %s", points)
