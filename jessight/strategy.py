import json
import time
import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from enum import Enum

import numpy as np


from jesse.models import Order
from jesse.strategies import Strategy

from jessight.indicators.indicators_manager import IndicatorsManager
from jessight.models import Insight
from jessight.utils.trades_writer import TradesWriter
from jessight.indicators.base_indicator import BaseIndicator
from jessight.strategy_interface import Strategy as CustomStrategy
from jessight.risk_manager import RiskManager
from jessight.events.events import Event


class InsightStrategy(Strategy, ABC):
    OUTPUT_FILE_PATH = "storage/insights"

    def __init__(self) -> None:
        super().__init__()
        self._is_initialized = False
        self.indicator_managers: IndicatorsManager = None  # type: ignore
        self.trades_writer: TradesWriter = None  # type: ignore
        self.start_simulation_timestamp: float = 0

    def _initialize(self) -> None:
        self.indicator_managers = IndicatorsManager(self.exchange, self.symbol, self.timeframe, self.indicators())
        self.trades_writer = TradesWriter(self.exchange, self.symbol, self.timeframe, self.indicator_managers)
        self.risk_manager = RiskManager(self.strategies())
        self.start_simulation_timestamp = self.time

    # Intended to be implemented by the child object
    def strategies(self) -> List[CustomStrategy]:
        pass

    # Intended to be implemented by the child object
    def indicators(self) -> List[BaseIndicator]:
        pass

    def before(self) -> None:
        if not self._is_initialized:
            self._initialize()

        self.indicator_managers.update()
        self.indicator_managers.draw()

    def go_long(self) -> None:
        self.trades_writer.new_trade()
        self.trades_writer.write_trade_number()
        self.trades_writer.write(
            event=Event.GO_LONG,
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
            event=Event.GO_SHORT,
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
            event=Event.ON_CANCEL,
        )
        self.trades_writer.indicators_snapshot()

    def on_open_position(self, order: Order) -> None:
        self.trades_writer.write_trade_number()
        self.trades_writer.write(
            event=Event.ON_OPEN_POSITION,
        )
        self.trades_writer.indicators_snapshot()

    def update_position(self) -> None:
        if not self.is_position_updated:
            return
        self.trades_writer.write(
            event=Event.UPDATE_POSITION,
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
            self.trades_writer.write(event=Event.ON_TP_CLOSE, take_profit=order.price)
        else:
            self.trades_writer.write(event=Event.ON_SL_CLOSE, stop_loss=order.price)
        self.trades_writer.indicators_snapshot()

    def terminate(self):
        self._save_insight_file()

    def _save_insight_file(self):
        insight = json.loads(self.insight().json())
        insight_path = Path(InsightStrategy.OUTPUT_FILE_PATH)
        insight_path.mkdir(parents=True, exist_ok=True)
        with open(insight_path / f"{int(time.time())}.pkl", "wb") as f:
            pickle.dump(insight, f)

    def insight(self) -> Insight:
        return Insight(
            indicators=self.indicator_managers.insight(),
            trades=self.trades_writer.to_dict(),
            start_simulation_timestamp=self.start_simulation_timestamp,
        )

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
