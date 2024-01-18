import os
import time
import pickle
import subprocess
from abc import ABC
from pathlib import Path

from jesse.routes import router
from jesse.strategies import Strategy
from jessight.indicators.indicators_manager import IndicatorsManager


class InsightStrategy(Strategy, ABC):
    def __init__(self) -> None:
        super().__init__()
        self._is_initialized = False
        self.indicator_managers: IndicatorsManager = IndicatorsManager()

    def _initial(self) -> None:
        if self._is_initialized:
            return
        self._is_initialized = True
        self.indicator_managers = IndicatorsManager(
            self.exchange, self.symbol, self.timeframe
        )
        self.initialize()

    def initialize(self):
        pass

    def before(self) -> None:
        self.initial()
        self.indicator_managers.update()
        self.indicator_managers.draw()

    def terminate(self):
        self._save_insight_file()
        path = Path(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run(["streamlit", "run", path / "plots" / "app.py"])

    def _save_insight_file(self):
        insight = []
        for format_route in router.all_formatted_routes:
            route = dict(
                exchange=format_route["exchange"],
                symbol=format_route["symbol"],
                timeframe=format_route["timeframe"],
            )
            insight.append(dict(**route, candles=self.get_candles(**route)))
        insight_path = Path("storage/insights")
        insight_path.mkdir(parents=True, exist_ok=True)
        with open(insight_path / f"{int(time.time())}.pkl", "wb") as f:
            pickle.dump(insight, f)
