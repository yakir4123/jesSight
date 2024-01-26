import numpy as np

import jesse.helpers as jh

from typing import Optional, Any, Union

from jessight.candles_provider import CandlesProvider
from jessight.indicators.indicators_manager import IndicatorsManager
from jessight.utils.csv_writer import CSVWriter


class TradesWriter(CandlesProvider):
    def __init__(
        self,
        exchange,
        symbol,
        timeframe,
        indicators_managers: IndicatorsManager,
    ):
        super().__init__(exchange, symbol, timeframe)
        self.indicators_managers = indicators_managers
        self.csv_writer = CSVWriter()
        self.curr_write_time = -1
        self._trade_number = 0
        # map trade-number:tp -> timestamp, price
        self.take_profits = {}
        # map stop-loss:sl -> timestamp, price
        self.stop_losses = {}

    def indicators_snapshot(self) -> None:
        indicators_states = dict(
            time=self.time, datetime=jh.timestamp_to_time(self.time), price=self.price
        )
        for indicator in self.indicators_managers:
            indicators_states |= {
                f"{ind}__{indicator.route}": log for ind, log in indicator.log.items()
            }
        self.write(**indicators_states)

    def write(self, **kwargs: Any) -> None:
        if self.curr_write_time != self.time:
            self.csv_writer.write(**kwargs)
            self.curr_write_time = self.time
        else:
            self.csv_writer.append(**kwargs)

    def new_trade(self) -> None:
        self._trade_number += 1

    def write_trade_number(self) -> None:
        self.write(trade_number=self.trade_number)

    @property
    def trade_number(self) -> int:
        return self._trade_number

    def set_take_profits(self, take_profit: Union[tuple, list, np.ndarray]) -> None:
        if type(take_profit[0]) not in [list, tuple, np.ndarray]:
            take_profit = [take_profit]
        for i, tp in enumerate(take_profit):
            key = f"{self.trade_number}:{i}"
            if key not in self.take_profits:
                self.take_profits[key] = []
            self.take_profits[key].append((self.time, tp[1]))

    def set_stop_losses(self, stop_loss: Union[tuple, list, np.ndarray]) -> None:
        if type(stop_loss[0]) not in [list, tuple, np.ndarray]:
            stop_loss = [stop_loss]
        for i, sl in enumerate(stop_loss):
            key = f"{self.trade_number}:{i}"
            if key not in self.stop_losses:
                self.stop_losses[key] = []
            self.stop_losses[key].append((self.time, sl[1]))

    def to_csv(self, path: str) -> None:
        self.csv_writer.to_csv(path)

    def to_dict(self) -> dict[str, Any]:
        return {
            "take-profits": self.take_profits,
            "stop-losses": self.stop_losses,
            "trades_snapshot": self.csv_writer.data,
        }
