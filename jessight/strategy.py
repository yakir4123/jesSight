import time
import pickle
from abc import ABC
from pathlib import Path

import numpy as np

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
        self.start_simulation_timestamp: float = 0

    def _initialize(self) -> None:
        if self._is_initialized:
            return

        self.start_simulation_timestamp = self.time
        self._is_initialized = True
        self.indicator_managers = IndicatorsManager(self.exchange, self.symbol, self.timeframe)

        self.trades_writer = TradesWriter(
            self.exchange,
            self.symbol,
            self.timeframe,
            indicators_managers=self.indicator_managers,
        )
        # Why is it here? not makes sense to call the global func from private like that, in addition it does nothing
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
        self.trades_writer.set_take_profits(self.take_profit)
        self.trades_writer.set_stop_losses(self.stop_loss)
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
        self.trades_writer.set_take_profits(self.take_profit)
        self.trades_writer.set_stop_losses(self.stop_loss)
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

    def update_position(self) -> None:
        if not self.is_position_updated:
            return
        self.trades_writer.write(
            event="update_position",
            entry=self.sell,
            take_profit=self.take_profit,
            stop_loss=self.stop_loss,
        )
        self.trades_writer.set_take_profits(self.take_profit)
        self.trades_writer.set_stop_losses(self.stop_loss)
        self.trades_writer.indicators_snapshot()

    def on_close_position(self, order: Order) -> None:
        self.trades_writer.write_trade_number()
        if order.is_take_profit:
            self.trades_writer.write(event="on_tp_close", take_profit=order.price)
        else:
            self.trades_writer.write(event="on_sl_close", stop_loss=order.price)
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
            "start_simulation_timestamp": self.start_simulation_timestamp,
        }
        return res

    @property
    def is_position_updated(self) -> bool:
        if self.position.is_close:
            return False

        if self.is_long and not np.array_equal(self.buy, self._buy):
            return True

        if self.is_short and not np.array_equal(self.sell, self._sell):
            return True

        if not np.array_equal(self.take_profit, self._take_profit):
            return True
        if not np.array_equal(self.stop_loss, self._stop_loss):
            return True
        return False

    def update_lazy_indicators(self) -> None:
        self.indicator_managers.update_lazy_indicators()
        self.indicator_managers.draw_lazy_indicators()
