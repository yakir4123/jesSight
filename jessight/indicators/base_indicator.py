import abc
import jesse.helpers as jh

from typing import Any, Union
from jessight.candles_provider import CandlesProvider


class BaseIndicator(CandlesProvider, abc.ABC):
    def __init__(self, exchange: str, symbol: str, timeframe: str):
        super().__init__(exchange, symbol, timeframe)
        self._chart_params = self._initial_chart_params()

    def insight(self) -> dict:
        return self._chart_params

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
        if self._chart_params is None:
            return
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

    def _initial_chart_params(self) -> Union[None, dict[str, dict]]:
        """
        reorganize the chart params from list of dicts with key of indicator name to dictionary with indicator name
        as the key of the params
        """
        res = {}
        chart_params = self.chart_params()
        if chart_params is None:
            return None
        if isinstance(chart_params, dict):
            chart_params = [chart_params]
        for params in chart_params:
            param_name = params["name"]
            res[param_name] = {}
            res[param_name]["values"] = []
            res[param_name]["timestamps"] = []
            res[param_name]["type"] = params["type"]
            del params["type"]
            res[param_name]["params"] = params
        return res
