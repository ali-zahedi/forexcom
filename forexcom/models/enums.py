import enum


class EnumMixin:
    @classmethod
    def find_by_name(cls, name):
        name = name.upper().replace(' ', '')
        return next((item for item in cls if item.name.upper() == name), cls.Unknown)


class InstructionStatus(enum.Enum):
    Accepted = 1
    RedCard = 2
    YellowCard = 3
    Error = 4
    Pending = 5


class Position(enum.Enum):
    Sell = 1
    Buy = 2


class PositionMethod(enum.Enum):
    LongOrShortOnly = 1
    LongAndShort = 2


class OrderType(EnumMixin, enum.Enum):
    Unknown = 0
    Trade = 1
    Stop = 2
    Limit = 3


class OrderStatus(EnumMixin, enum.Enum):
    Unknown = 0
    Pending = 1
    Accepted = 2
    Open = 3
    Cancelled = 4
    Rejected = 5
    Suspended = 6
    YellowCard = 8
    Closed = 9
    RedCard = 10
    Triggered = 11


class OrderActionType(EnumMixin, enum.Enum):
    Unknown = 0
    OpeningOrder = 1
    FullClose = 2
    PartClose = 3
    QuantityDecrease = 4
    QuantityIncrease = 5
    AddOrder = 6
    RolledOrder = 7
    CancelledOrder = 8


class QuoteStatus(EnumMixin, enum.Enum):
    Unknown = 0
    Pending = 1
    Accepted = 2
    Rejected = 3
    Closed = 4
    Error = 5
    RedCard = 6


class Currency(EnumMixin, enum.Enum):
    Unknown = 0
    AUD = 1
    CAD = 2
    CHF = 3
    EUR = 4
    GBP = 6
    HKD = 7
    JPY = 8
    SEK = 9
    SGD = 10
    USD = 11
    ZAR = 12
    DKK = 14
    IDR = 15
    KRW = 16
    MXN = 17
    MYR = 18
    NOK = 19
    NZD = 20
    THB = 21
    TWD = 22
    INR = 23
    PLN = 24
    TRY = 31
    CZK = 32
    HUF = 33
    SKK = 34
    CNH = 36
    AED = 37
    BRL = 38
    ILS = 39
    RON = 40
    RUB = 41
    SAR = 42
    XAU = 43
    XAG = 44
    CNY = 45
