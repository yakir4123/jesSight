from typing import Union, Optional

import jesse.helpers as jh
from jessight.indicators.base_indicator import BaseIndicator
from jessight.indicators.route_indicators import RouteIndicators


class IndicatorsManager:
    def __init__(
        self, default_exchange: str, default_symbol: str, default_timeframe: str
    ):
        self.default_exchange = default_exchange
        self.default_symbol = default_symbol
        self.default_timeframe = default_timeframe
        self.indicators: dict[str, RouteIndicators] = {}

    def add(self, indicator: BaseIndicator):
        if indicator.route not in self.indicators:
            self.indicators[indicator.route] = RouteIndicators(
                indicator.exchange, indicator.symbol, indicator.timeframe
            )
        self.indicators[indicator.route].add(indicator)

    def update(self) -> None:
        for ind in self.indicators.values():
            ind.update()

    def draw(self) -> None:
        for ind in self.indicators.values():
            ind.draw()

    def chart_params(self) -> None:
        for ind in self.indicators.values():
            ind.chart_params()

    def __getitem__(self, index: Union[str, tuple]) -> BaseIndicator:
        if isinstance(index, str):
            index = (index,)
        kwargs = dict(name=index[0])
        if len(index) > 1:
            kwargs["timeframe"] = index[-1]
        if len(index) > 2:
            kwargs["symbol"] = index[-2]
        if len(index) > 3:
            kwargs["exchange"] = index[-3]
        return self.get(**kwargs)

    def get(
        self,
        name: str,
        exchange: Optional[str] = None,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
    ) -> BaseIndicator:
        exchange = exchange or self.default_exchange
        symbol = symbol or self.default_symbol
        timeframe = timeframe or self.default_timeframe
        route = jh.key(exchange, symbol, timeframe)
        return self.indicators[route][name]
