from typing import Any

from jessight.indicators.base_indicator import BaseIndicator
from jessight.candles_provider import CandlesProvider


class RouteIndicators(CandlesProvider):
    def __init__(self, exchange: str, symbol: str, timeframe: str) -> None:
        super().__init__(exchange, symbol, timeframe)
        self.indicators: dict[str, BaseIndicator] = {}

    def __getitem__(self, key: str) -> BaseIndicator:
        return self.indicators[key]

    def insight(self) -> dict:
        res = dict(
            exchange=self.exchange,
            symbol=self.symbol,
            timeframe=self.timeframe,
            lines=[],
            markers=[],
            candles=self.candles,
        )
        for indicator in self.indicators.values():
            indicator_insights = indicator.insight()
            for line in indicator_insights["lines"].values():
                res["lines"].append(line.to_dict())
            res["markers"] += indicator_insights["markers"]
        return res

    def add(self, indicator: BaseIndicator) -> None:
        self.indicators[indicator.name] = indicator

    def update(self) -> None:
        if not self.is_new_candle:
            return
        for ind in self.indicators.values():
            ind.update()

    def draw(self) -> None:
        if not self.is_new_candle:
            return
        for ind in self.indicators.values():
            ind._draw()

    def chart_params(self) -> None:
        for ind in self.indicators.values():
            ind.chart_params()

    def __iter__(self):
        return iter(self.indicators.items())
