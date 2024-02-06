from datetime import datetime
from typing import Union

import pandas as pd
from lightweight_charts.util import LINE_STYLE, MARKER_POSITION, MARKER_SHAPE, NUM

# TODO: Come up with a better solution for the to_dict method, its not makes sense that the caller
#       should know all the hardcoded fields, at least create static class variables for those hardcoded fields


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
        self.time = time
        self.position = position
        self.shape = shape
        self.color = color
        self.text = text

    def set_timestamp(self, timestamp: int) -> None:
        self.time = datetime.utcfromtimestamp(timestamp)

    def to_dict(self):
        return {
            "time": self.time,
            "position": self.position,
            "shape": self.shape,
            "color": self.color,
            "text": self.text
        }


class CandleColor:
    def __init__(self, value: str):
        self.value = value
        self.time = 0

    def to_dict(self):
        return {"value": self.value, "time": self.time}


class TrendLine:
    def __init__(
        self,
        start_time: float,
        start_value: float,
        end_time: float,
        end_value: float,
        round: bool = False,
        color: str = "#1E80F0",
        width: int = 2,
        style: LINE_STYLE = "solid",
    ):
        self.start_time = start_time
        self.start_value = start_value
        self.end_time = end_time
        self.end_value = end_value
        self.round = round
        self.color = color
        self.width = width
        self.style = style

    def to_dict(self):
        return {
            "start_time": pd.to_datetime(self.start_time, unit="ms"),
            "start_value": self.start_value,
            "end_time": pd.to_datetime(self.end_time, unit="ms"),
            "end_value": self.end_value,
            "round": self.round,
            "color": self.color,
            "width": self.width,
            "style": self.style,
        }


class Line:
    def __init__(
        self,
        name: str = "",
        color: str = "rgba(214, 237, 255, 0.6)",
        style: LINE_STYLE = "solid",
        width: int = 2,
        price_line: bool = False,
        price_label: bool = False,
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
Drawable = Union[LinePoint, Marker, CandleColor, TrendLine]
