import uuid
from typing import Any

import pandas as pd


class CSVWriter:
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}

    def write(self, index: str = "", **kwargs: Any) -> None:
        if index == "":
            index = uuid.uuid4().hex[:8]
        self.data[index] = kwargs

    def to_csv(self, path: str) -> None:
        pd.DataFrame.from_dict(self.data, orient="index").to_csv(path)
