import jesse.helpers as jh

from typing import Optional, Any

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

    def to_csv(self, path: str) -> None:
        self.csv_writer.to_csv(path)

    def to_dict(self) -> dict[str, Any]:
        return self.csv_writer.data
