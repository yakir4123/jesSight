import pandas as pd
import jesse.helpers as jh

from typing import Optional
from dateutil import parser
from streamlit.delta_generator import DeltaGenerator
from lightweight_charts.widgets import StreamlitChart


class CandleChart:
    def __init__(
        self, insight: dict, height: int, col: Optional[DeltaGenerator] = None
    ):
        self.df = pd.DataFrame(
            insight["candles"],
            columns=["date", "open", "close", "high", "low", "volume"],
        )
        self.df["date"] = pd.to_datetime(self.df["date"], unit="ms").dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.col = col
        self.exchange = insight["exchange"]
        self.symbol = insight["symbol"]
        self.timeframe = insight["timeframe"]
        self.chart = StreamlitChart(height=height)
        self.chart.topbar.textbox("exchange", self.exchange)
        self.chart.topbar.textbox("symbol", self.symbol)
        self.chart.topbar.textbox("timeframe", self.timeframe)
        self.chart.legend(visible=True)
        self.chart.set(self.df)
        self.set_indicators(insight)

    def set_indicators(self, insight: dict):
        for indicator in insight["lines"]:
            self.create_line(indicator)
        insight["markers"].sort(key=lambda x: x["time"])
        for marker in insight["markers"]:
            self.create_marker(marker)

    def create_marker(self, marker) -> None:
        self.chart.marker(**marker)

    def create_line(self, indicator) -> None:
        chart_ind = self.chart.create_line(**indicator["params"])
        df = pd.DataFrame.from_dict(
            {
                "time": indicator["time"],
                indicator["name"]: indicator["values"],
            },
            orient="columns",
        )
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        chart_ind.set(df)

    def goto(self, date: str):
        timestamp = parser.parse(date).timestamp() * 1000
        timeframe_in_minute = jh.timeframe_to_one_minutes(self.timeframe)
        arrow_time = jh.timestamp_to_arrow(timestamp)
        self.chart.set_visible_range(
            arrow_time.shift(minutes=-22 * timeframe_in_minute).format(
                "YYYY-MM-DD HH:mm"
            ),
            arrow_time.shift(minutes=23 * timeframe_in_minute).format(
                "YYYY-MM-DD HH:mm"
            ),
        )

    def plot(self):
        if self.col:
            with self.col:
                self.chart.load()
        else:
            self.chart.load()
