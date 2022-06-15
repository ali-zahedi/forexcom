from .enums import OrderStatus, OrderType, Position, PositionMethod


class Order:
    def __init__(
        self,
        order_id: int,
        symbol_id: int,
        symbol_name: str,
        client_account_id: int,
        trading_account_id: int,
        currency,
        position: Position,
        open_price: float,
        original_quantity: float,
        quantity: float,
        order_type: OrderType,
        status: OrderStatus,
        reason_id,
        position_method: PositionMethod = PositionMethod.LongOrShortOnly,
        original_last_changed_date_time=None,
        last_changed_time=None,
        auto_rollover: bool = False,
    ):
        self.order_id = order_id
        self.symbol_id = symbol_id
        self.symbol_name = symbol_name
        self.client_account_id = client_account_id
        self.trading_account_id = trading_account_id
        self.currency = currency
        self.position = position
        self.auto_rollover = auto_rollover
        self.last_changed_time = last_changed_time
        self.open_price = open_price
        self.original_last_changed_date_time = original_last_changed_date_time
        self.original_quantity = original_quantity
        self.position_method = position_method
        self.quantity = quantity
        self.order_type = order_type
        self.status = status
        self.reason_id = reason_id

    def __str__(self):
        return (
            f"{self.last_changed_time} | {self.order_id} | {self.symbol_name} | {self.position} |"
            f" {self.position_method} | {self.order_type} | {self.status} | {self.reason_id} |"
            f" {self.open_price} | {self.original_quantity} | {self.quantity}"
        )
