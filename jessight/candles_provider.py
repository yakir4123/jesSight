from typing import Union

import numpy as np

import jesse.helpers as jh
from jessight import const
from jesse.store import store
from jesse.enums import timeframes


class CandlesProvider:
    def __init__(self, exchange: str, symbol: str, timeframe: str):
        # TODO: Check whether exchange is supported
        self.exchange = exchange
        # TODO: Check whether symbol/asset is supported
        self.symbol = symbol
        self.timeframe = timeframe
        self.timeframe_in_ms = (
            jh.timeframe_to_one_minutes(self.timeframe) * const.MILLISECONDS_IN_MINUTE
        )

    @property
    def route(self):
        return jh.key(self.exchange, self.symbol, self.timeframe)

    @property
    def candles(self) -> np.ndarray:
        return store.candles.get_candles(self.exchange, self.symbol, self.timeframe)

    @property
    def get_1m_candles(self) -> np.ndarray:
        return store.candles.get_candles(
            self.exchange, self.symbol, timeframes.MINUTE_1
        )

    @property
    def curr_candle(self) -> np.ndarray:
        return self.candles[-1]

    @property
    def time(self) -> int:
        return store.app.time

    @property
    def is_new_candle(self) -> bool:
        return (self.time % self.timeframe_in_ms) == 0

    # TODO: Refactor properties, not makes sense to return ndarray as float
    @property
    def open(self) -> float:
        return self.curr_candle[const.OPEN]

    @property
    def close(self) -> float:
        return self.curr_candle[const.CLOSE]

    @property
    def price(self) -> float:
        return self.curr_candle[const.CLOSE]

    @property
    def high(self) -> float:
        return self.curr_candle[const.HIGH]

    @property
    def low(self) -> float:
        return self.curr_candle[const.LOW]

    @property
    def volume(self) -> float:
        return self.curr_candle[const.VOLUME]

    # Is it possible to get more than two-dimensional array?
    def is_green_candle(self, index: Union[int, slice] = -1) -> Union[bool, np.ndarray]:
        return self.candles[index, const.CLOSE] > self.candles[index, const.OPEN]
