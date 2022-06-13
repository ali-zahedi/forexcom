from .enums import OrderStatus, OrderType, Position, PositionMethod


class Order:
    """
    position: of the order (1 == buy, 0 == sell).
    position_method_id: Indicates the position of the trade. 1 == LongOrShortOnly, 2 == LongAndShort.
    order_type: The type of the order (1 = Trade / 2 = Stop / 3 = Limit).
    """

    def __init__(
        self,
        order_id,
        symbol_id,
        symbol_name,
        client_account_id,
        trading_account_id,
        currency,
        position: Position,
        auto_rollover,
        execution_price,
        open_price,
        last_changed_time,
        original_last_changed_date_time,
        original_quantity,
        position_method: PositionMethod,
        quantity,
        order_type: OrderType,
        status: OrderStatus,
        reason_id,
    ):
        self.order_id = order_id
        self.symbol_id = symbol_id
        self.symbol_name = symbol_name
        self.client_account_id = client_account_id
        self.trading_account_id = trading_account_id
        self.currency = currency
        self.position = position
        self.auto_rollover = auto_rollover
        self.execution_price = execution_price
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
            f" {self.open_price} | {self.execution_price} | {self.original_quantity} | {self.quantity}"
        )
