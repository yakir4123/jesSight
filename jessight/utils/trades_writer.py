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

    def snapshot(self) -> None:
        indicators_states = dict(
            time=self.time, datetime=jh.timestamp_to_time(self.time), price=self.price
        )
        for indicator in self.indicators_managers:
            indicators_states |= {
                f"{ind}__{indicator.route}": log for ind, log in indicator.log.items()
            }
        self.csv_writer.write(**indicators_states)

    def to_csv(self, path: str) -> None:
        self.csv_writer.to_csv(path)

    def to_dict(self) -> dict[str, Any]:
        return self.csv_writer.data
