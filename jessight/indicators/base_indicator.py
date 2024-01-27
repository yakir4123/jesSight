import abc
import jesse.helpers as jh

from typing import Any, Union, Optional, Iterable
from jessight.candles_provider import CandlesProvider
from jessight.plots.drawables import (
    ConfigurableIndicator,
    Line,
    Drawable,
    Marker,
    LinePoint,
    CandleColor,
    TrendLine,
)


class BaseIndicator(CandlesProvider, abc.ABC):
    def __init__(
        self, exchange: str, symbol: str, timeframe: str, is_lazy: bool = False
    ):
        super().__init__(exchange, symbol, timeframe)
        self._chart_params = self._initial_chart_params()
        self.is_lazy = is_lazy

    def insight(self) -> dict:
        return self._chart_params

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    def update(self) -> None:
        ...

    @property
    @abc.abstractmethod
    def state(self) -> dict[str, Any]:
        ...

    def _draw(self) -> None:
        values = self.draw()
        if values is None:
            return
        if not isinstance(values, Iterable):
            values = [values]
        for value in values:
            if isinstance(value, LinePoint):
                self._draw_line(value)
            if isinstance(value, Marker):
                self._draw_marker(value)
            if isinstance(value, CandleColor):
                self._draw_candle_color(value)
            if isinstance(value, TrendLine):
                self._draw_trend_line(value)

    def _draw_candle_color(self, value: CandleColor) -> None:
        value.time = self.get_draw_timestamp()
        self._chart_params["candles_colors"].append(value.to_dict())

    def _draw_trend_line(self, value: TrendLine) -> None:
        # value.time = self.get_draw_timestamp()
        self._chart_params["trend_line"].append(value.to_dict())

    def _draw_marker(self, value: Marker) -> None:
        value.params["time"] = self.get_draw_timestamp()
        self._chart_params["markers"].append(value.to_dict())

    def _draw_line(self, value: LinePoint) -> None:
        timestamp = self.get_draw_timestamp()
        try:
            self._chart_params["lines"][value.name]._values.append(value.value)
            self._chart_params["lines"][value.name]._time.append(timestamp)
        except KeyError:
            raise KeyError(
                f"{value.name} is not a line that has been initialized in `chart_params`, make sure to "
                f"add it."
            )

    def get_draw_timestamp(self):
        timestamp = self.time
        timestamp -= jh.timeframe_to_one_minutes(self.timeframe) * 60_000
        return timestamp

    def draw(self) -> Union[Iterable[Drawable], Drawable, None]:
        return None

    @property
    def log(self) -> dict[str, Any]:
        return self.state

    def chart_params(
        self,
    ) -> Union[None, ConfigurableIndicator, list[ConfigurableIndicator]]:
        return None

    def _initial_chart_params(self) -> Union[None, dict[str, Any]]:
        """
        reorganize the chart params from list of dicts with key of indicator name to dictionary with indicator name
        as the key of the params
        """
        chart_params = self.chart_params()
        res = {"markers": [], "lines": {}, "candles_colors": [], "trend_line": []}
        if chart_params is None:
            return res
        if isinstance(chart_params, ConfigurableIndicator):
            chart_params = [chart_params]

        for params in chart_params:
            if isinstance(params, Line):
                param_name = params.name
                res["lines"][param_name] = params

        return res
