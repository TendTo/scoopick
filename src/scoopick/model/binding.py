from typing import Callable, TypeVar, Generic

T = TypeVar("T")


class Binding(Generic[T]):
    def __init__(
        self, getter: Callable[[], T], setter: Callable[[T], None], updater: Callable[[], None] = lambda: None
    ):
        self._getter = getter
        self._setter = setter
        self._updater = updater

    @property
    def getter(self):
        return self._getter

    @property
    def setter(self):
        return self._setter

    @property
    def updater(self):
        return self._updater

    @updater.setter
    def updater(self, updater: callable):
        self._updater = updater

    @property
    def value(self):
        return self._getter()

    @value.setter
    def value(self, value):
        self._setter(value)
        self._updater()
