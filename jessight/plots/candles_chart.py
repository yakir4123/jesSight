import pandas as pd
import jesse.helpers as jh
import const

from typing import Optional
from dateutil import parser
from streamlit.delta_generator import DeltaGenerator
from lightweight_charts.widgets import StreamlitChart


class CandleChart:
    def __init__(
        self,
        insight: dict,
        height: int,
        col: Optional[DeltaGenerator] = None,
        take_profits: Optional[dict] = None,
        stop_losses: Optional[dict] = None,
    ):
        # TODO: Refactor, this method should not know that a 'candle' key exist in the provided dict
        #       example of good naming for dict: 'assetsByID' here we can assume that the keys are ids.
        #       otherwise come up with a different way
        # TODO: Refactor columns param, if this data related to every candle, get if from appropriate class
        #       and not hard code it
        self.df = pd.DataFrame(
            insight["candles"],
            columns=["date", "open", "close", "high", "low", "volume"],
        )
        self._set_candles_colors(insight)
        self.df["date"] = pd.to_datetime(self.df["date"], unit=const.DATE_MS_UNIT).dt.strftime(const.DATE_FORMAT)
        self.col = col
        # TODO: Refactor, this class should not know about the existence of those dict keys
        self.exchange = insight["exchange"]
        self.symbol = insight["symbol"]
        self.timeframe = insight["timeframe"]
        self.chart = StreamlitChart(height=height)
        self._set_chart()
        self._set_indicators(insight)

        take_profits = take_profits or {}
        stop_losses = stop_losses or {}
        self._add_tp_lines(take_profits)
        self._add_sl_lines(stop_losses)

    def _set_chart(self):
        # TODO: Refactor, this class should not know about the existence of those dict keys
        self.chart.topbar.textbox("exchange", self.exchange)
        self.chart.topbar.textbox("symbol", self.symbol)
        self.chart.topbar.textbox("timeframe", self.timeframe)
        self.chart.legend(visible=True)
        self.chart.set(self.df)

    def _set_candles_colors(self, insight: dict):
        if len(insight[const.CANDLE_COLOR_CHART_PARAM]) == 0:
            return

        # TODO: Should not accessed via hardcoded fields
        self.df["color"] = "rgba(39, 157, 130, 100)"
        self.df.loc[
            self.df["close"] < self.df["open"], "color"
        ] = "rgba(200, 97, 100, 100)"
        colors_df = pd.DataFrame(insight["candles_colors"])
        colors_df.rename(columns={"time": "date", "value": "color"}, inplace=True)
        merged_df = pd.merge(self.df, colors_df, on="date", how="left", suffixes=("_df1", "_df2"))
        resulting_colors = merged_df["color_df2"].combine_first(merged_df["color_df1"])
        self.df["color"] = resulting_colors

    def _set_indicators(self, insight: dict):
        # TODO: Refactor, should not access insight fields by magic keys

        for indicator in insight[const.LINE_CHART_PARAM]:
            self.create_line(indicator)

        # TODO: Dont use x as param names, change to more describing name
        insight[const.MARKER_CHART_PARAM].sort(key=lambda x: x["time"])

        for marker in insight[const.MARKER_CHART_PARAM]:
            self.create_marker(marker)

        for trend_line in insight[const.TREND_LINE_CHART_PARAM]:
            self.create_trend_line(trend_line)

    def create_trend_line(self, trend_line) -> None:
        self.chart.trend_line(**trend_line)

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
        df["time"] = pd.to_datetime(df["time"], unit=const.DATE_MS_UNIT)
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
            df["time"] = pd.to_datetime(df["time"], unit=const.DATE_MS_UNIT)
            chart_ind.set(df)

    # TODO: 1. Change method name
    #       2. Change hardcoded field to well defined
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
