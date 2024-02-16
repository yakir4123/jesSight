from pydantic import BaseModel
from pydantic.color import Color

from jessight.models.utils import BaseModelDataStructure


class CandleColor(BaseModel):
    color: Color = "#1E80F0"
    time: int = 0


class CandleColorList(BaseModelDataStructure):
    __root__: list[CandleColor]
