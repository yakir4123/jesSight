from pydantic import BaseModel

from jessight.models.lines import LineDict
from jessight.models.markers import MarkerList
from jessight.models.trend_lines import TrendLineList
from jessight.models.candle_colors import CandleColorList


class RouteModel(BaseModel):
    exchange: str = ""
    symbol: str = ""
    timeframe: str = ""
    lines: LineDict = LineDict.parse_obj([])
    markers: MarkerList = MarkerList.parse_obj([])
    trend_lines: TrendLineList = TrendLineList.parse_obj([])
    candles_colors: CandleColorList = CandleColorList.parse_obj([])
    candles: list[list] = []


class Insight(BaseModel):
    indicators: list[RouteModel]
    trades: dict
    start_simulation_timestamp: int
