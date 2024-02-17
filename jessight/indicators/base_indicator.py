import abc
import jesse.helpers as jh

from typing import Any, Union, Iterable
from jessight.candles_provider import CandlesProvider
import jessight.const as const
import jessight.plots.const as pconst
from jessight.models import (
    Marker,
    TrendLine,
    LineParamsModel,
    Line,
    LinePoint,
    ConfigurableIndicator,
    CandleColor,
    Drawable,
    RouteModel,
)


class BaseIndicator(CandlesProvider, abc.ABC):
    def __init__(
        self, exchange: str, symbol: str, timeframe: str, is_lazy: bool = False
    ):
        super().__init__(exchange, symbol, timeframe)

        self._chart_params = self._initial_chart_params()
        self.is_lazy = is_lazy

    def insight(self) -> RouteModel:
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

        if isinstance(values, Drawable):
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
        self._chart_params.candles_colors.append(value)

    def _draw_trend_line(self, value: TrendLine) -> None:
        self._chart_params.trend_lines.append(value)

    def _draw_marker(self, marker: Marker) -> None:
        marker.time = self.get_draw_timestamp()
        self._chart_params.markers.append(marker)

    def _draw_line(self, point: LinePoint) -> None:
        point.timestamp = self.get_draw_timestamp()

        try:
            self._chart_params.lines[point.name].line_points.append(point)
        except KeyError:
            raise KeyError(
                f"{point.name} is not a line that has been initialized in `chart_params`,"
                f" make sure to add correspond LineParamsModel it."
            )

    def get_draw_timestamp(self) -> int:
        return (
            self.time
            - jh.timeframe_to_one_minutes(self.timeframe) * const.MILLISECONDS_IN_MINUTE
        )

    def draw(self) -> Union[Iterable[Drawable], Drawable, None]:
        return None

    @property
    def log(self) -> dict[str, Any]:
        return self.state

    def chart_params(
        self,
    ) -> ConfigurableIndicator | list[ConfigurableIndicator] | None:
        return None

    def _initial_chart_params(self) -> RouteModel:
        """
        reorganize the chart params from list of dicts with key of indicator name to dictionary with indicator name
        as the key of the params
        """
        chart_params = self.chart_params()
        indicator_modes = RouteModel()

        if chart_params is None:
            return indicator_modes

        if isinstance(chart_params, ConfigurableIndicator):
            chart_params = [chart_params]

        for params in chart_params:
            if isinstance(params, LineParamsModel):
                indicator_modes.lines[params.name] = Line(params=params)

        return indicator_modes
