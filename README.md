# Scoopick

Scoopick is a simple GUI application that somewhat simplifies task automation.
It's very rough around the edges and primarily intended for personal use.
The core functionality is to provide an easy way to take a screenshot and put some points as (x, y) coordinate on it.
The points will then be passed to a user-provided Python script to power whatever automatic task the user wants to perform.

See the `examples/` folder for some simple tasks that use Scoopick's functionality.

## Installation

Scoopick can be installed via pip:

```bash
pip install git+https://github.com/TendTo/scoopick.git
```

## Usage

Scoopick can be run from the command line:

```bash
scoopick
```

A GUI window will open, allowing you to take a screenshot and place points on it.
Once you have placed the points, you can run a script by selecting it via the "Load Script" button.
The script should define a `run(points: list[Point], capture_screenshot: Callable[[], QPixmap])` function, which will be called with the list of points and a function to capture screenshots on demand.

```python
# My script example
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scoopick.data import Point
    from typing import Callable
    from PySide6.QtGui import QPixmap

def run(points: "list[Point]", capture_screenshot: "Callable[[], QPixmap]"):
    for point in points:
        print(f"Point at ({point.x}, {point.y})")
    screenshot = capture_screenshot()
    screenshot.save("screenshot.png")
```

## Examples

There are a couple of scripts in the `examples/` folder that demonstrate how to use Scoopick.

- **logging**: basic example showing how to interact with Scoopick's GUI via logging.
- **balatro**: automatically look for the legendary jokers with the goal of unlocking the corresponding achievement.
  It does so by restarting the game and skipping the blinds until a legendary joker is found in one of the tarot booster packs.
- **wordle**: solves the daily Wordle puzzles on Discord by taking a screenshot of the game to understand the current state and then computing the next best guess using the [wordle-solver](https://github.com/joshstephenson/Wordle-Solver) script.
