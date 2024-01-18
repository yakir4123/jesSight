from typing import Optional

import pandas as pd
from streamlit.delta_generator import DeltaGenerator

import jesse.helpers as jh
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

    def goto(self, date: str):
        timeframe_in_minute = jh.timeframe_to_one_minutes(self.timeframe)
        timestamp = jh.date_to_timestamp(date)
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
