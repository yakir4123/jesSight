from typing import Union

import numpy as np

import jesse.helpers as jh
from jesse.store import store


class CandlesProvider:
    def __init__(self, exchange: str, symbol: str, timeframe: str):
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe

    @property
    def route(self):
        return jh.key(self.exchange, self.symbol, self.timeframe)

    @property
    def candles(self) -> np.ndarray:
        return store.candles.get_candles(self.exchange, self.symbol, self.timeframe)

    @property
    def get_1m_candles(self) -> np.ndarray:
        return store.candles.get_candles(self.exchange, self.symbol, "1m")

    @property
    def curr_candle(self) -> np.ndarray:
        return self.candles[-1]

    @property
    def time(self) -> int:
        return store.app.time

    @property
    def open(self) -> float:
        return self.curr_candle[1]

    @property
    def close(self) -> float:
        return self.curr_candle[2]

    @property
    def price(self) -> float:
        return self.curr_candle[2]

    @property
    def high(self) -> float:
        return self.curr_candle[3]

    @property
    def low(self) -> float:
        return self.curr_candle[4]

    @property
    def volume(self) -> float:
        return self.curr_candle[5]

    def is_green_candle(self, index: Union[int, slice] = -1) -> Union[bool, np.ndarray]:
        return self.candles[index, 2] > self.candles[index, 1]
