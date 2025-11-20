import os
import sys
import time
from logging import getLogger
from typing import TYPE_CHECKING

from pynput.keyboard import Controller, Key

file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(file_path)

# Weave the method to load words from the correct path
from wordle_solver.wordle_solver import Dictionary

original_get_words = Dictionary.get_words
Dictionary.get_words = lambda self, filename: original_get_words(
    self, os.path.join(file_path, "wordle_solver", filename)
)
from wordle_solver.wordle_solver import Solver

if TYPE_CHECKING:
    from typing import Callable

    from PySide6.QtGui import QPixmap

    from scoopick.data import Point


logger = getLogger("scoopick")


class WordleRunner:
    INITIAL_WORD = "SLATE"

    def __init__(self, points: "list[Point]", capture_screenshot: "Callable[[], QPixmap]"):
        self.points = [points[i * 5 : (i + 1) * 5] for i in range(6)]
        self.gray = (50, 50, 50)
        self.green = (83, 141, 78)
        self.yellow = (181, 159, 59)
        self.keyboard = Controller()
        self.solver = Solver()
        self.current_try = 0
        self.capture_screenshot = capture_screenshot
        self.last_screenshot = None

    # Distance between two colors
    def dist(self, p0: "tuple[int, int, int]", p1: "tuple[int, int, int]") -> int:
        return abs(p0[0] - p1[0]) + abs(p0[1] - p1[1]) + abs(p0[2] - p1[2])

    def submit_word(self, word: str):
        for letter in word:
            self.keyboard.press(letter)
            self.keyboard.release(letter)
            time.sleep(0.1)
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        time.sleep(3)  # Wait for the result to show up

    def get_feedback(self) -> "list[str]":
        feedback = []
        screenshot = self.capture_screenshot()
        for point in self.points[self.current_try]:
            x, y = point.x, point.y
            color = screenshot.toImage().pixelColor(x, y).getRgb()[:3]
            logger.debug(f"Getting pixel color at ({x}, {y}): {color}")
            distances = tuple(self.dist(color, c) for c in (self.gray, self.green, self.yellow))
            min_dist = min(distances)
            if min_dist == distances[0]:
                feedback.append("_")
            elif min_dist == distances[1]:
                feedback.append("g")
            else:
                feedback.append("y")
        self.current_try += 1
        return feedback

    def run(self):
        guess = self.INITIAL_WORD
        for _ in range(6):
            logger.debug(f"Submitting word: {guess}")
            self.submit_word(guess)
            feedback = self.get_feedback()
            logger.debug(f"Feedback: {''.join(feedback)}")
            green = "".join(letter if feedback[i] == "g" else "_" for i, letter in enumerate(guess))
            yellow = "".join(letter for i, letter in enumerate(guess) if feedback[i] == "y")
            logger.debug(f"Guess: {guess}, Green: {green}, Yellow: {yellow}")
            self.solver.guess(guess, green, yellow)
            guess = self.solver.next_guess()
            if self.solver.is_solved():
                logger.info("Solved!")
                return


def run(points: "list[Point]", capture_screenshot: "Callable[[], QPixmap]"):
    logger.debug("Waiting 3 sec")
    time.sleep(3)
    WordleRunner(points, capture_screenshot).run()
