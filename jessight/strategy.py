import time
import pickle
from abc import ABC
from pathlib import Path

from jesse.models import Order
from jesse.strategies import Strategy
from jessight.indicators.indicators_manager import IndicatorsManager
from jessight.utils.trades_writer import TradesWriter


class InsightStrategy(Strategy, ABC):
    def __init__(self) -> None:
        super().__init__()
        self._is_initialized = False
        self.indicator_managers: IndicatorsManager = None  # type: ignore
        self.trades_writer: TradesWriter = None  # type: ignore

    def _initialize(self) -> None:
        if self._is_initialized:
            return
        self._is_initialized = True
        self.indicator_managers = IndicatorsManager(
            self.exchange, self.symbol, self.timeframe
        )
        self.trades_writer = TradesWriter(
            self.exchange,
            self.symbol,
            self.timeframe,
            indicators_managers=self.indicator_managers,
        )
        self.initialize()

    def initialize(self):
        pass

    def before(self) -> None:
        self._initialize()
        self.indicator_managers.update()
        self.indicator_managers.draw()

    def go_long(self) -> None:
        self.trades_writer.new_trade()
        self.trades_writer.write_trade_number()
        self.trades_writer.write(
            event="go_long",
            entry=self.buy,
            take_profit=self.take_profit,
            stop_loss=self.stop_loss,
        )
        self.trades_writer.indicators_snapshot()

    def go_short(self) -> None:
        self.trades_writer.new_trade()
        self.trades_writer.write_trade_number()
        self.trades_writer.write(
            event="go_short",
            entry=self.sell,
            take_profit=self.take_profit,
            stop_loss=self.stop_loss,
        )
        self.trades_writer.indicators_snapshot()

    def on_cancel(self) -> None:
        self.trades_writer.write_trade_number()
        self.trades_writer.write(
            event="on_cancel",
        )
        self.trades_writer.indicators_snapshot()

    def on_open_position(self, order: Order) -> None:
        self.trades_writer.write_trade_number()
        self.trades_writer.write(
            event="on_open_position",
        )
        self.trades_writer.indicators_snapshot()

    # def update_position(self) -> None:
    #     self.trades_writer.write(
    #         event="update_position",
    #         entry=self.sell,
    #         take_profit=self.take_profit,
    #         stop_loss=self.stop_loss,
    #     )
    #     self.trades_writer.indicators_snapshot()

    def on_close_position(self, order: Order) -> None:
        self.trades_writer.write_trade_number()
        self.trades_writer.write(
            event="on_tp_close" if order.is_take_profit else "on_sl_close",
        )
        self.trades_writer.indicators_snapshot()

    def terminate(self):
        self._save_insight_file()

    def _save_insight_file(self):
        insight = self.insight()
        insight_path = Path("storage/insights")
        insight_path.mkdir(parents=True, exist_ok=True)
        with open(insight_path / f"{int(time.time())}.pkl", "wb") as f:
            pickle.dump(insight, f)

    def insight(self):
        res = {
            "indicators": self.indicator_managers.insight(),
            "trades": self.trades_writer.to_dict(),
        }
        return res
