# Scoopick

Scoopick is a simple GUI application that somewhat simplifies task automation.
It's very rough around the edges and primarily intended for personal use.
The core functionality is to provide an easy way to take a screenshot and put some points on it.
The points will then be passed to a user-provided Python script for further processing.
All while providing a function to capture screenshots on demand while the script is running.

See the `examples/` folder for example scripts that use Scoopick's functionality.

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
The script should define a `run(points: list[Point], capture_screenshot: Callable[[], QPixmap])` function,
which will be called with the list of points and a function to capture screenshots.

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
