import time
from logging import getLogger
from typing import TYPE_CHECKING

from pyautogui import pixel
from pynput.mouse import Button, Controller

if TYPE_CHECKING:
    from typing import Callable

    from PySide6.QtGui import QPixmap

    from scoopick.data import Point

logger = getLogger("scoopick")


class BalatroRunner:

    def __init__(self, points: "list[Point]"):
        # Position of the skip icons
        self.skip_1_icon_pos = points[0].to_tuple()
        self.skip_2_icon_pos = points[1].to_tuple()
        self.skip_2_icon_under_pos = points[2].to_tuple()
        # Position of the skip buttons
        self.skip_1_btn_pos = points[3].to_tuple()
        self.skip_2_btn_pos = points[4].to_tuple()
        self.skip_arcane_pack_pos = points[5].to_tuple()
        # Position of the new game button
        self.new_game_btn_pos = points[6].to_tuple()
        self.play_btn_pos = points[7].to_tuple()
        self.options_btn_pos = points[8].to_tuple()
        # Positions of the cards
        self.card_1_pos = points[9].to_tuple()
        self.card_2_pos = points[10].to_tuple()
        self.card_3_pos = points[11].to_tuple()
        self.card_4_pos = points[12].to_tuple()
        self.card_5_pos = points[13].to_tuple()
        self.card_1_icon_pos = points[14].to_tuple()
        self.card_2_icon_pos = points[15].to_tuple()
        self.card_3_icon_pos = points[16].to_tuple()
        self.card_4_icon_pos = points[17].to_tuple()
        self.card_5_icon_pos = points[18].to_tuple()
        self.card_1_use_pos = points[19].to_tuple()
        self.card_2_use_pos = points[20].to_tuple()
        self.card_3_use_pos = points[21].to_tuple()
        self.card_4_use_pos = points[22].to_tuple()
        self.card_5_use_pos = points[23].to_tuple()
        self.cards = tuple(
            zip(
                [self.card_1_pos, self.card_2_pos, self.card_3_pos, self.card_4_pos, self.card_5_pos],
                [
                    self.card_1_icon_pos,
                    self.card_2_icon_pos,
                    self.card_3_icon_pos,
                    self.card_4_icon_pos,
                    self.card_5_icon_pos,
                ],
                [
                    self.card_1_use_pos,
                    self.card_2_use_pos,
                    self.card_3_use_pos,
                    self.card_4_use_pos,
                    self.card_5_use_pos,
                ],
            )
        )
        # Color of the tarot card
        self.tarot_color = (158, 116, 206)
        # Color of the tarot skip 1
        self.arcane_pack_color = (125, 96, 224)
        # Color of the tarot skip 2
        self.arcane_pack_color_dark = (93, 89, 155)

        self.mouse = Controller()

    # Distance between two colors
    def dist(self, p0: "tuple[int, int, int]", p1: "tuple[int, int, int]") -> int:
        return abs(p0[0] - p1[0]) + abs(p0[1] - p1[1]) + abs(p0[2] - p1[2])

    # After opening an arcane pack, look for the legendary card
    def select_arcane_card(self):
        # Hover over card all five cards
        for card_pos, icon_pos, use_pos in self.cards:
            time.sleep(0.5)
            self.mouse.position = card_pos
            time.sleep(0.1)
            color = pixel(icon_pos[0], icon_pos[1])
            # print(color)
            if self.dist(color, self.tarot_color) > 10:
                print("Legendary card found!")
                self.mouse.click(Button.left)
                time.sleep(1)
                self.mouse.position = use_pos
                time.sleep(0.1)
                self.mouse.click(Button.left)
                time.sleep(10)
                return
        print("No legendary card found")

    def reset_game(self):
        # Reset the game
        self.mouse.position = self.options_btn_pos
        time.sleep(0.1)
        self.mouse.click(Button.left)
        time.sleep(0.5)
        self.mouse.position = self.new_game_btn_pos
        time.sleep(0.1)
        self.mouse.click(Button.left)
        time.sleep(0.5)
        self.mouse.position = self.play_btn_pos
        time.sleep(0.1)
        self.mouse.click(Button.left)
        time.sleep(2)
        print("New game")

    def click_arcane_pack(self):
        time.sleep(1)
        skip_1_pixel = pixel(self.skip_1_icon_pos[0], self.skip_1_icon_pos[1])
        skip_2_pixel = pixel(self.skip_2_icon_under_pos[0], self.skip_2_icon_under_pos[1])

        print("Skip 1 and 2 pixels")
        # print(skip_1_pixel, skip_2_pixel)
        has_first = self.dist(skip_1_pixel, self.arcane_pack_color) < 10
        has_second = self.dist(skip_2_pixel, self.arcane_pack_color_dark) < 10

        if has_first or has_second:

            # Click of the first skip
            self.mouse.position = self.skip_1_btn_pos
            time.sleep(0.1)
            self.mouse.click(Button.left)
            print("Skip 1")
            time.sleep(2.5)

            if has_first:
                print("Skip 1 is a booster pack")
                self.select_arcane_card()
                time.sleep(1)
                self.mouse.position = self.skip_arcane_pack_pos
                time.sleep(0.1)
                self.mouse.click(Button.left)
                time.sleep(1)
            else:
                print("Skip 1 is not a booster pack")

        if has_second:

            # Do the same for the second skip
            self.mouse.position = self.skip_2_btn_pos
            time.sleep(0.1)
            self.mouse.click(Button.left)
            print("Skip 2")
            time.sleep(2.5)

            if has_second:
                print("Skip 2 is a booster pack")
                self.select_arcane_card()
                time.sleep(1)
                self.mouse.position = self.skip_arcane_pack_pos
                time.sleep(0.1)
                self.mouse.click(Button.left)
                time.sleep(1)
            else:
                print("Skip 2 is not a booster pack")

        self.reset_game()


def run(points: "list[Point]", capture_screenshot: "Callable[[], QPixmap]"):
    logger.info("Waiting 10 sec")
    time.sleep(10)
    balatro = BalatroRunner(points)
    while True:
        balatro.click_arcane_pack()
