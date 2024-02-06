from typing import Any

from jessight.indicators.base_indicator import BaseIndicator
from jessight.candles_provider import CandlesProvider
import jessight.plots.const as pconst


class RouteIndicators(CandlesProvider):
    def __init__(self, exchange: str, symbol: str, timeframe: str) -> None:
        super().__init__(exchange, symbol, timeframe)

        self.indicators: dict[str, BaseIndicator] = {}

    def __getitem__(self, name: str) -> BaseIndicator:
        return self.indicators[name]

    def insight(self) -> dict:
        res = dict(
            exchange=self.exchange,
            symbol=self.symbol,
            timeframe=self.timeframe,
            lines=[],
            markers=[],
            trend_line=[],
            candles_colors=[],
            candles=self.candles,
        )
        for indicator in self.indicators.values():
            indicator_insights = indicator.insight()

            for line in indicator_insights[pconst.LINE_CHART_PARAM].values():
                res[pconst.LINE_CHART_PARAM].append(line.to_dict())

            res[pconst.MARKER_CHART_PARAM] += indicator_insights[pconst.MARKER_CHART_PARAM]
            res[pconst.TREND_LINE_CHART_PARAM] += indicator_insights[pconst.TREND_LINE_CHART_PARAM]
            res[pconst.CANDLE_COLOR_CHART_PARAM] += indicator_insights[pconst.CANDLE_COLOR_CHART_PARAM]

        return res

    def add_indicator(self, indicator: BaseIndicator) -> None:
        self.indicators[indicator.name] = indicator

    def update(self, is_lazy=False) -> None:
        if not self.is_new_candle:
            return

        for indicator in self.indicators.values():
            if is_lazy == indicator.is_lazy:
                indicator.update()

    def draw(self, is_lazy: bool = False) -> None:
        if not self.is_new_candle:
            return

        for indicator in self.indicators.values():
            if indicator.is_lazy == is_lazy:
                indicator.draw_indicator()

    def chart_params(self) -> None:
        for ind in self.indicators.values():
            ind.chart_params()

    def __iter__(self):
        return iter(self.indicators.items())
