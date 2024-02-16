from lightweight_charts.util import LINE_STYLE
from pydantic import BaseModel
from pydantic.color import Color

from jessight.models.utils import BaseModelDataStructure


class TrendLine(BaseModel):
    start_time: int
    start_value: float
    end_time: int
    end_value: float
    round: bool = False
    color: Color = "#1E80F0"
    width: int = 2
    style: LINE_STYLE = "solid"


class TrendLineList(BaseModelDataStructure):
    __root__: list[TrendLine]
