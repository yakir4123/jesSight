import numpy as np
from lightweight_charts.util import LINE_STYLE, MARKER_POSITION, MARKER_SHAPE
from pydantic import BaseModel
from pydantic.color import Color


class LineParamsModel(BaseModel):
    name: str = ""
    color: Color = "rgba(214, 237, 255, 0.6)"
    style: LINE_STYLE = "solid"
    width: int = 2
    price_line: bool = True
    price_label: bool = True


class LineModel(BaseModel):
    name: str
    values: list[float]
    time: list[int]
    params: LineParamsModel


class MarkerModel(BaseModel):
    time: int = 0
    position: MARKER_POSITION = "below"
    shape: MARKER_SHAPE = "arrow_up"
    color: Color = "#2196F3"
    text: str = ""


class TrendLineModel(BaseModel):
    start_time: int
    start_value: float
    end_time: int
    end_value: float
    round: bool = False
    color: Color = "#1E80F0"
    width: int = (2,)
    style: LINE_STYLE = "solid"


class IndicatorModel(BaseModel):
    exchange: str
    symbol: str
    timeframe: str
    lines: list[LineModel]
    markers: list[MarkerModel]
    trend_line: list[TrendLineModel]
    candles_colors: list[Color]
    # candles: np.ndarray


class Insight(BaseModel):
    indicators: list[IndicatorModel]
    trades: dict
    start_simulation_timestamp: int
