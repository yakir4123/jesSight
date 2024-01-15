import glob
import os
import pickle
import tkinter as tk
from tkinter import filedialog


import pandas as pd
import streamlit as st
from lightweight_charts.widgets import StreamlitChart


def latest_insight_file():
    list_of_files = glob.glob("storage\insights\*")
    return max(list_of_files, key=os.path.getctime)


def filename(path):
    return os.path.basename(path)


def browsing_files():
    latest_file = latest_insight_file()
    latest_file = filename(latest_file)
    st.text_input("Insight file - The simulation result", latest_file)
    clicked = st.button("Choose insight file.")
    if clicked:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)
        return filename(filedialog.askopenfile(master=root).name)

    return latest_file


def main():
    st.set_page_config(layout="wide")
    st.title(f"Jesse Insights")
    file_return = browsing_files()
    st.subheader(file_return)
    with open("storage/insights/1705357392.pkl", "rb") as f:
        insights_data = pickle.load(f)
    df = pd.DataFrame(
        insights_data[0]["candles"],
        columns=["date", "open", "close", "high", "low", "volume"],
    )
    df["date"] = pd.to_datetime(df["date"], unit="ms").dt.strftime("%Y-%m-%d %H:%M:%S")
    chart = StreamlitChart(height=600)
    chart.set(df)
    chart.load()


if __name__ == "__main__":
    main()
