from dataclasses import asdict, dataclass


@dataclass
class Point:
    idx: int
    name: str
    x: int
    y: int
    color: tuple[int, int, int] = (255, 0, 0)

    def update(self, point: "Point"):
        for key, value in asdict(point).items():
            setattr(self, key, value)

    def __str__(self):
        if self.x < 0 or self.y < 0:
            return f"{self.name} (not set)"
        return f"{self.name} ({self.x}, {self.y})"
