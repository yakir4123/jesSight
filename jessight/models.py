from datetime import datetime

import numpy as np
import pandas as pd
from lightweight_charts.util import LINE_STYLE, MARKER_POSITION, MARKER_SHAPE, TIME
from pydantic import BaseModel
from pydantic.color import Color


class InsightModel(BaseModel):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        cls = self.__class__
        for field_name, field_type in cls.__annotations__.items():
            if field_type == TIME:
                setattr(
                    self,
                    field_name,
                    self._convert_to_timestamp(self.__dict__[field_name]),
                )

    @staticmethod
    def _convert_to_timestamp(value):
        if isinstance(value, datetime):
            return pd.Timestamp(value)
        elif isinstance(value, int):
            return pd.Timestamp(value, unit="ms")
        return value


class LineParamsModel(InsightModel):
    name: str = ""
    color: Color = "rgba(214, 237, 255, 0.6)"
    style: LINE_STYLE = "solid"
    width: int = 2
    price_line: bool = True
    price_label: bool = True


class LineModel(InsightModel):
    name: str
    values: list[float]
    time: list[TIME]
    params: LineParamsModel


class MarkerModel(InsightModel):
    time: TIME
    position: MARKER_POSITION = "below"
    shape: MARKER_SHAPE = "arrow_up"
    color: Color = "#2196F3"
    text: str = ""


class TrendLineModel(InsightModel):
    start_time: TIME
    start_value: float
    end_time: TIME
    end_value: float
    round: bool = False
    color: Color = "#1E80F0"
    width: int = (2,)
    style: LINE_STYLE = "solid"


class IndicatorModel(InsightModel):
    exchange: str
    symbol: str
    timeframe: str
    lines: list[LineModel]
    markers: list[MarkerModel]
    trend_line: list[TrendLineModel]
    candles_colors: list[Color]
    candles: np.ndarray


class Insight(InsightModel):
    indicators: list[IndicatorModel]
    trades: dict
    start_simulation_timestamp: int
