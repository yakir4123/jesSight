from typing import Union

from .utils import *
from .insight_models import *
from .lines import *
from .markers import *
from .trend_lines import *
from .candle_colors import *

ConfigurableIndicator = Union[LineParamsModel]
Drawable = Union[Marker, LinePoint, TrendLine, CandleColor]
