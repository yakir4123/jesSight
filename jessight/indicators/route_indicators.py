from typing import Any

from jessight.indicators.base_indicator import BaseIndicator
from jessight.candles_provider import CandlesProvider
from jessight.models import IndicatorModel


class RouteIndicators(CandlesProvider):
    def __init__(self, exchange: str, symbol: str, timeframe: str) -> None:
        super().__init__(exchange, symbol, timeframe)
        self.indicators: dict[str, BaseIndicator] = {}

    def __getitem__(self, key: str) -> BaseIndicator:
        return self.indicators[key]

    def insight(self) -> IndicatorModel:
        res = IndicatorModel(
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
            res.lines |= indicator_insights.lines
            res.markers += indicator_insights.markers
            res.trend_lines += indicator_insights.trend_lines
            res.candles_colors += indicator_insights.candles_colors
        return res

    def add(self, indicator: BaseIndicator) -> None:
        self.indicators[indicator.name] = indicator

    def update(self, is_lazy=False) -> None:
        if not self.is_new_candle:
            return
        for ind in self.indicators.values():
            if is_lazy == ind.is_lazy:
                ind.update()

    def draw(self, is_lazy: bool = False) -> None:
        if not self.is_new_candle:
            return
        for ind in self.indicators.values():
            if ind.is_lazy == is_lazy:
                ind._draw()

    def chart_params(self) -> None:
        for ind in self.indicators.values():
            ind.chart_params()

    def __iter__(self):
        return iter(self.indicators.items())
