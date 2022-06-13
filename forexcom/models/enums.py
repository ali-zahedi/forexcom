import enum


class Position(enum.Enum):
    Sell = 1
    Buy = 2


class PositionMethod(enum.Enum):
    LongOrShortOnly = 1
    LongAndShort = 2


class OrderType(enum.Enum):
    Trade = 'Trade'
    Stop = 'Stop'
    Limit = 'Limit'


class OrderStatus(enum.Enum):
    Open = 'Open'
    Closed = 'Closed'
    Accepted = 'Accepted'
    Cancelled = 'Cancelled'
