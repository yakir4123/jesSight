from enum import StrEnum, auto


class Event(StrEnum):
    GO_LONG = auto()
    GO_SHORT = auto()
    ON_CANCEL = auto()
    ON_OPEN_POSITION = auto()
    UPDATE_POSITION = auto()
    ON_TP_CLOSE = auto()
    ON_SL_CLOSE = auto()
