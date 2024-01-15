import abc
import jesse.helpers as jh

from typing import Any, Union
from jessight.candles_provider import CandlesProvider


class BaseIndicator(CandlesProvider, abc.ABC):
    def __init__(self, exchange: str, symbol: str, timeframe: str):
        super().__init__(exchange, symbol, timeframe)
        _chart_params = self.chart_params()
        if _chart_params is None:
            _chart_params = {}
        self._chart_params = _chart_params
        for key in self._chart_params.keys():
            self._chart_params[key]["values"] = []
            self._chart_params[key]["timestamps"] = []

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...

    @abc.abstractmethod
    def update(self) -> None:
        ...

    @property
    @abc.abstractmethod
    def state(self) -> dict[str, Any]:
        ...

    def _draw(self) -> None:
        values = self.draw()
        if isinstance(values, dict):
            values = [values]
        timestamp = self.time
        timestamp -= jh.timeframe_to_one_minutes(self.timeframe) * 60_000
        for value in values:
            for name, v in value.items():
                try:
                    self._chart_params[name]["values"].append(v)
                    self._chart_params[name]["timestamps"].append(timestamp)
                except KeyError:
                    raise KeyError(
                        f"{name} is not a value that has been initialized in `chart_params`, make sure to "
                        f"add it."
                    )

    def draw(self) -> dict[str, Any]:
        return self.state

    @property
    def log(self) -> dict[str, Any]:
        return self.state

    def chart_params(self) -> Union[None, dict, list[dict]]:
        return None
