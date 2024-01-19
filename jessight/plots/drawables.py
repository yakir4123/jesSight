from datetime import datetime
from typing import Union

from lightweight_charts.util import LINE_STYLE, MARKER_POSITION, MARKER_SHAPE, NUM


class LinePoint:
    def __init__(self, name: str, value: NUM):
        self.name = name
        self.value = value
        self.time = None


class Marker:
    def __init__(
        self,
        time: datetime = None,
        position: MARKER_POSITION = "below",
        shape: MARKER_SHAPE = "arrow_up",
        color: str = "#2196F3",
        text: str = "",
    ):
        self.params = dict(
            time=time, position=position, shape=shape, color=color, text=text
        )

    def to_dict(self):
        return self.params


class Line:
    def __init__(
        self,
        name: str = "",
        color: str = "rgba(214, 237, 255, 0.6)",
        style: LINE_STYLE = "solid",
        width: int = 2,
        price_line: bool = True,
        price_label: bool = True,
    ):
        self.name = name
        self.params = dict(
            name=name,
            color=color,
            style=style,
            width=width,
            price_line=price_line,
            price_label=price_label,
        )
        self._values = []
        self._time = []

    def to_dict(self):
        return dict(
            name=self.name, values=self._values, time=self._time, params=self.params
        )

    def add_value(self, point: LinePoint):
        assert point.name == self.name
        self._values.append(point.value)
        self._time.append(point.time)


ConfigurableIndicator = Union[Line]
Drawable = Union[LinePoint, Marker]
