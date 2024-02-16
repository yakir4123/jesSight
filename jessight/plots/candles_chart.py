import json

import pandas as pd
import jesse.helpers as jh

from typing import Optional
from dateutil import parser
from streamlit.delta_generator import DeltaGenerator

from lightweight_charts.widgets import StreamlitChart

from jessight.const import MILLISECONDS_IN_SECOND
from jessight.models import RouteModel, Line, Marker, TrendLine


class CandleChart:
    DEFAULT_VISIBLE_BACK_CANDLES = 22
    DEFAULT_VISIBLE_FRONT_CANDLES = 23

    def __init__(
        self,
        insight: RouteModel,
        height: int,
        col: Optional[DeltaGenerator] = None,
        take_profits: Optional[dict] = None,
        stop_losses: Optional[dict] = None,
    ):
        self.df = pd.DataFrame(
            insight.candles,
            columns=["date", "open", "close", "high", "low", "volume"],
        )
        self._set_candles_colors(insight)
        self.df["date"] = pd.to_datetime(self.df["date"], unit="ms").dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.col = col
        self.exchange = insight.exchange
        self.symbol = insight.symbol
        self.timeframe = insight.timeframe
        self.chart = StreamlitChart(height=height)
        self._set_chart()
        self._set_indicators(insight)

        take_profits = take_profits or {}
        stop_losses = stop_losses or {}
        self._add_tp_lines(take_profits)
        self._add_sl_lines(stop_losses)

    def _set_chart(self):
        self.chart.topbar.textbox("exchange", self.exchange)
        self.chart.topbar.textbox("symbol", self.symbol)
        self.chart.topbar.textbox("timeframe", self.timeframe)
        self.chart.legend(visible=True)
        self.chart.set(self.df)

    def _set_candles_colors(self, insight: RouteModel):
        if len(insight.candles_colors) == 0:
            return

        self.df["color"] = "rgba(39, 157, 130, 100)"
        self.df.loc[
            self.df["close"] < self.df["open"], "color"
        ] = "rgba(200, 97, 100, 100)"
        colors_df = pd.DataFrame(
            map(lambda c: json.loads(c.json()), insight.candles_colors)
        )
        colors_df.rename(columns={"time": "date", "value": "color"}, inplace=True)
        merged_df = pd.merge(
            self.df, colors_df, on="date", how="left", suffixes=("_df1", "_df2")
        )
        resulting_colors = merged_df["color_df2"].combine_first(merged_df["color_df1"])
        self.df["color"] = resulting_colors

    def _set_indicators(self, insight: RouteModel):
        for indicator in insight.lines.values():
            self.create_line(indicator)
        insight.markers.sort(key=lambda x: x.time)
        for marker in insight.markers:
            self.create_marker(marker)
        for trend_line in insight.trend_lines:
            self.create_trend_line(trend_line)

    def create_trend_line(self, trend_line: TrendLine) -> None:
        self.chart.trend_line(**trend_line.dict())

    def create_marker(self, marker: Marker) -> None:
        self.chart.marker(**marker.dict())

    def create_line(self, indicator: Line) -> None:
        chart_ind = self.chart.create_line(**indicator.params.dict())
        df = pd.DataFrame(
            json.loads(indicator.line_points.json()),
        )
        df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[indicator.params.name] = df["value"]
        del df["timestamp"]
        del df["value"]
        chart_ind.set(df)

    def _add_tp_lines(self, take_profits):
        for line_id, tps in take_profits.items():
            chart_ind = self.chart.create_line(
                color="lime",
                name=f"tp: {line_id}",
                style="dashed",
                width=1,
                price_line=False,
                price_label=False,
            )
            df = pd.DataFrame(tps, columns=["time", f"tp: {line_id}"])
            df["time"] = pd.to_datetime(df["time"], unit="ms")
            chart_ind.set(df)

    def _add_sl_lines(self, stop_losses):
        for line_id, sls in stop_losses.items():
            chart_ind = self.chart.create_line(
                color="#CD5C5C",
                name=f"sl: {line_id}",
                style="dashed",
                width=1,
                price_line=False,
                price_label=False,
            )
            df = pd.DataFrame(sls, columns=["time", f"sl: {line_id}"])
            df["time"] = pd.to_datetime(df["time"], unit="ms")
            chart_ind.set(df)

    def goto_date(self, date: str):
        timestamp = parser.parse(date).timestamp() * MILLISECONDS_IN_SECOND
        timeframe_in_minute = jh.timeframe_to_one_minutes(self.timeframe)
        arrow_time = jh.timestamp_to_arrow(timestamp)
        self.chart.set_visible_range(
            arrow_time.shift(
                minutes=-CandleChart.DEFAULT_VISIBLE_BACK_CANDLES * timeframe_in_minute
            ).format("YYYY-MM-DD HH:mm"),
            arrow_time.shift(
                minutes=CandleChart.DEFAULT_VISIBLE_FRONT_CANDLES * timeframe_in_minute
            ).format("YYYY-MM-DD HH:mm"),
        )

    def plot(self):
        if self.col:
            with self.col:
                self.chart.load()
        else:
            self.chart.load()
