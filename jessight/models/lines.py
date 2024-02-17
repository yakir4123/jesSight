from lightweight_charts.util import LINE_STYLE
from pydantic import BaseModel
from pydantic.color import Color

from jessight.models.utils import BaseModelDataStructure


class LinePoint(BaseModel):
    name: str = ""
    timestamp: int = 0
    value: float = 0.0

    class Config:
        fields = {"name": {"exclude": True}}


class LineParamsModel(BaseModel):
    name: str = ""
    color: Color = "rgba(214, 237, 255, 0.6)"
    style: LINE_STYLE = "solid"
    width: int = 2
    price_line: bool = True
    price_label: bool = True


class LinePointList(BaseModelDataStructure):
    __root__: list[LinePoint]


class Line(BaseModel):
    params: LineParamsModel
    line_points: LinePointList = LinePointList.parse_obj([])


class LineDict(BaseModelDataStructure):
    __root__: dict[str, Line]
