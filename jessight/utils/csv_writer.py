import uuid
from typing import Any, Optional

import pandas as pd


class CSVWriter:
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}
        self.last_index = None

    def write(self, index: str = "", **kwargs: Any) -> None:
        if index == "":
            index = uuid.uuid4().hex[:8]
        self.data[index] = kwargs
        self.last_index = index

    def append(self, index: Optional[str] = None, **kwargs: Any) -> None:
        if index is None:
            index = self.last_index
        self.data[index] |= kwargs

    def to_csv(self, path: str) -> None:
        pd.DataFrame.from_dict(self.data, orient="index").to_csv(path)
