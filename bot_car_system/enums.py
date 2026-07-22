from enum import Enum

class Role(Enum):
    SYSTEN = "system"
    ASSISTANT = "assistant"
    USER = "user"

class Actions(Enum):
    RECOMMENDATION = "recommendation"
    SEARCH = "search"
    LANGUAGE = "language"

class Commands(Enum):
    START = "start"
    CANCEL = "cancel"
    TRAIN = "train"
    HELP = "help"

class Languages(Enum):
    HEBREW = "Hebrew"
    ENGLISH = "English"
