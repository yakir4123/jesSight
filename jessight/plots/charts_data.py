import pandas as pd
import jesse.helpers as jh

from jesse.store import store
from typing import Any, Optional
from lightweight_charts import Chart, AbstractChart


class ChartsData:
    def __init__(self) -> None:
        self.charts: list[AbstractChart] = []
        self.markers: dict[str, list] = {}
        self.trend_lines: dict[str, list] = {}
        self.line_indicators: dict[str, list] = {}
        self.indicators_properties: dict[str, dict] = {}

    @staticmethod
    def indicator_key(*args: str) -> str:
        return "-".join(args)

    def set(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        indicator_name: str,
        **properties: Any,
    ) -> None:
        indicator_key = self.indicator_key(exchange, symbol, timeframe, indicator_name)
        if indicator_key not in self.indicators_properties:
            self.indicators_properties[indicator_key] = {}

        self.indicators_properties[indicator_key] |= properties

    def vline(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        timestamp: float,
        start_price: float,
        end_price: float,
        **trend_line_properties: Any,
    ) -> None:
        indicator_key = self.indicator_key(exchange, symbol, timeframe)
        if indicator_key not in self.trend_lines:
            self.trend_lines[indicator_key] = []

        trend_line_properties["end_time"] = pd.to_datetime(timestamp, unit="ms")
        timestamp -= jh.timeframe_to_one_minutes(timeframe) * 60_000
        trend_line_properties["start_time"] = pd.to_datetime(timestamp, unit="ms")
        trend_line_properties["start_value"] = start_price
        trend_line_properties["end_value"] = end_price
        self.trend_lines[indicator_key].append(trend_line_properties)

    def marker(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        timestamp: float,
        **marker_properties: Any,
    ) -> None:
        marker_key = self.indicator_key(exchange, symbol, timeframe)
        if marker_key not in self.markers:
            self.markers[marker_key] = []

        timestamp -= jh.timeframe_to_one_minutes(timeframe) * 60_000
        marker_properties["time"] = timestamp
        self.markers[marker_key].append(marker_properties)

    def line(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        indicator_name: str,
        timestamp: float,
        value: float,
    ) -> None:
        indicator_key = self.indicator_key(exchange, symbol, timeframe, indicator_name)
        if indicator_key not in self.line_indicators:
            self.line_indicators[indicator_key] = []
        timestamp -= jh.timeframe_to_one_minutes(timeframe) * 60_000
        self.line_indicators[indicator_key].append((timestamp, value))

    def chart_of(
        self, exchange: str, symbol: str, timeframe: str, **kwargs: Any
    ) -> None:
        if not self.main_chart:
            self.charts.append(Chart(**kwargs, toolbox=True))
        else:
            self.charts.append(self.main_chart.create_subchart(**kwargs, toolbox=True))

        chart = self.charts[-1]
        self._set_time_range(timeframe, chart)
        route_key = self.indicator_key(exchange, symbol, timeframe)
        candles = store.candles.get_candles(exchange, symbol, timeframe)
        df = pd.DataFrame(
            candles, columns=["time", "open", "close", "high", "low", "volume"]
        )
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        chart.set(df)
        chart.topbar.textbox("symbol", symbol)
        chart.topbar.textbox("timeframe", timeframe)

        for indicator_key, values in self.line_indicators.items():
            if not indicator_key.startswith(route_key):
                continue
            indicator_name = indicator_key[len(route_key) + 1 :]
            properties = self.indicators_properties.get(indicator_key, {})
            line = chart.create_line(indicator_name, **properties, price_line=False)
            df = pd.DataFrame(values, columns=["time", indicator_name])
            df["time"] = pd.to_datetime(df["time"], unit="ms")
            line.set(df)

        if route_key in self.markers:
            for marker in self.markers[route_key]:
                chart.marker(**marker)

        if route_key in self.trend_lines:
            for trend_line in self.trend_lines[route_key]:
                chart.trend_line(**trend_line)

    def plot(self) -> None:
        assert (
            self.main_chart is not None
        ), "self.chart_of(..) must be called at least once"
        self.main_chart.show(block=True)  # noqa

    @property
    def main_chart(self) -> Optional[AbstractChart]:
        if len(self.charts) == 0:
            return None
        return self.charts[0]

    def _set_time_range(self, timeframe: str, chart: AbstractChart) -> None:
        def on_search(_: AbstractChart, searched_string: str) -> None:
            try:
                timeframe_in_minute = jh.timeframe_to_one_minutes(timeframe)
                timestamp = jh.date_to_timestamp(searched_string)
                arrow_time = jh.timestamp_to_arrow(timestamp)
                for sub_chart in self.charts:
                    sub_chart.set_visible_range(
                        arrow_time.shift(minutes=-15 * timeframe_in_minute).format(
                            "YYYY-MM-DD HH:mm"
                        ),
                        arrow_time.shift(minutes=35 * timeframe_in_minute).format(
                            "YYYY-MM-DD HH:mm"
                        ),
                    )
            except:  # noqa
                pass

        chart.events.search += on_search
