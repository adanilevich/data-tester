from enum import Enum


class Status(Enum):
    LOADING = "LOADING"
    LOADED = "LOADED"
    ERROR = "ERROR"
    UNCLEAR = "UNCLEAR"
