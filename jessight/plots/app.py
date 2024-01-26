import os
import pickle
from pathlib import Path

import pandas as pd
import jesse.helpers as jh

import streamlit as st

from jessight.plots.candles_chart import CandleChart
from jessight.plots.trades_table import draw_grid


class App:
    def __init__(self):
        self.trades_df = st.session_state.get("trades_df", None)
        self.chosen_file = st.session_state.get("chosen_file", None)
        self.charts_date = st.session_state.get("charts_date", None)
        self.insights_data = st.session_state.get("insights_data", None)

    def latest_insight_file(self):
        try:
            path = Path("storage/insights")
            list_of_files = path.glob("*.pkl")
            return max(list_of_files, key=os.path.getctime).absolute()
        except ValueError:
            return os.getcwd()

    def filename(self):
        try:
            return os.path.basename(self.chosen_file)
        except FileNotFoundError:
            return ""

    def load_trades_df(self, insight_trades: dict):
        df = pd.DataFrame.from_dict(insight_trades, orient="index")
        if "Viewed" not in df.columns:
            df.insert(loc=0, column="Viewed", value=False)
        self.trades_df = df

    def browsing_files(self):
        self.chosen_file = st.text_input(
            "Insight file - The simulation result", self.chosen_file
        )
        if self.chosen_file:
            with open(self.chosen_file, "rb") as f:
                self.insights_data = pickle.load(f)

    def load_charts(self):
        if self.insights_data is None:
            return
        insights_data = self.insights_data
        self.load_trades_df(insights_data["trades"])
        unseen_aggrid = self.trades_manager_aggrid(self.trades_df)

        # main_chart
        self.charts = []
        indicators_data = insights_data["indicators"]
        n_of_charts = len(indicators_data)
        height = 600 if n_of_charts == 1 else 400

        goto_date = self.charts_date or jh.timestamp_to_date(
            indicators_data[0]["candles"][22, 0]
        )
        selection = unseen_aggrid.selected_rows
        if len(selection) == 1:
            goto_date = selection[0]["datetime"]

        if n_of_charts % 2 == 1:
            chart = CandleChart(indicators_data[0], height)
            self.charts.append(chart)
            indicators_data = indicators_data[1:]

        col1, col2 = st.columns((1, 1))
        for insight in indicators_data[::2]:
            chart = CandleChart(insight, height, col1)
            self.charts.append(chart)
        for insight in indicators_data[1::2]:
            chart = CandleChart(insight, height, col2)
            self.charts.append(chart)

        for chart in self.charts:
            chart.goto(goto_date)
            chart.plot()

    def trades_manager_aggrid(self, df):
        return draw_grid(df)

    def change_charts_date(self, date: str) -> None:
        self.charts_date = date
        for chart in self.charts:
            chart.goto(date)
            chart.plot()

    def go_to_date_bt(self) -> str:
        return st.text_input(
            label="Go to:",
            value="",
            help="Format: YYYY-MM-DD [HH:mm]",
        )

    def run(self):
        st.title(f"Jesse Insights")
        self.browsing_files()
        if not self.chosen_file:
            return

        self.charts_date = self.go_to_date_bt()
        self.load_charts()
        if self.charts_date:
            self.change_charts_date(self.charts_date)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    app = App()
    app.run()
    st.session_state.chosen_file = app.chosen_file
    st.session_state.charts_date = app.charts_date
    st.session_state.trades_df = app.trades_df
    st.session_state.insights_data = app.insights_data
