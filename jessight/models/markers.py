from lightweight_charts.util import MARKER_POSITION, MARKER_SHAPE
from pydantic import BaseModel
from pydantic.color import Color

from jessight.models.utils import BaseModelDataStructure


class Marker(BaseModel):
    time: int = 0
    position: MARKER_POSITION = "below"
    shape: MARKER_SHAPE = "arrow_up"
    color: Color = "#2196F3"
    text: str = ""


class MarkerList(BaseModelDataStructure):
    __root__: list[Marker]
