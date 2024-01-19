from typing import Optional

from jessight.candles_provider import CandlesProvider
from jessight.indicators.indicators_manager import IndicatorsManager
from jessight.utils.csv_writer import CSVWriter


class TradesWriter(CandlesProvider):
    def __init__(
        self,
        exchange: str = "",
        symbol: str = "",
        timeframe: str = "",
        indicators_managers: Optional[dict[str, IndicatorsManager]] = None,
    ):
        super().__init__(exchange, symbol, timeframe)
        self.indicators_managers: dict[str, IndicatorsManager] = (
            indicators_managers or {}
        )
        self.csv_writer = CSVWriter()

    def snapshot(self) -> None:
        import jesse.helpers as jh

        indicators_states = dict(
            time=self.time, datetime=jh.timestamp_to_date(self.time), price=self.price
        )
        for timeframe, manager in self.indicators_managers.items():
            for indicator in manager._indicators:
                indicators_states |= {
                    f"{timeframe}_{ind}": state for ind, state in indicator.log.items()
                }
        self.csv_writer.write(**indicators_states)

    def to_csv(self, path: str) -> None:
        self.csv_writer.to_csv(path)
