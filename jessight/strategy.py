import os
import time
import pickle
import subprocess
from abc import ABC
from pathlib import Path

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
        self.trades_writer = TradesWriter(self.exchange, self.symbol, self.timeframe)
        self.initialize()

    def initialize(self):
        pass

    def before(self) -> None:
        self._initialize()
        self.indicator_managers.update()
        self.indicator_managers.draw()

    def terminate(self):
        self._save_insight_file()
        path = Path(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run(["streamlit", "run", path / "plots" / "app.py"])

    def _save_insight_file(self):
        insight = self.insight()
        insight_path = Path("storage/insights")
        insight_path.mkdir(parents=True, exist_ok=True)
        with open(insight_path / f"{int(time.time())}.pkl", "wb") as f:
            pickle.dump(insight, f)

    def insight(self):
        return self.indicator_managers.insight()
