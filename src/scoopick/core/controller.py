import keyboard
from keyboard import mouse

from ..data import Point


class Controller:
    @staticmethod
    def click_at(point: Point) -> None:
        """Simulate a mouse click at the specified (x, y) coordinates."""
        mouse.move(point.x, point.y)
        mouse.click()

    @staticmethod
    def type_text(text: str, delay: float = 0.25) -> None:
        """Simulate typing the given text."""
        keyboard.write(text, delay=int(delay * 1000))  # Type with specified pause in between each key.
        keyboard.press("enter")  # Simulate pressing the Enter key.
