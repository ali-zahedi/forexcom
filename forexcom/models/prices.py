class Price:
    """
    direction: The direction of movement since the last price. 1 == up, -1 == down.
    audit_id: Unique identifier for each price tick. Read this value from the prices stream.
              Treat it as a unique but random string.
    Status_summary: The current status summary for this price.
                    Values are: 0 = Normal 1 = Indicative 2 = PhoneOnly 3 = Suspended 4 = Closed
    """

    def __init__(
        self,
        symbol_id,
        symbol_name,
        tick_datetime,
        bid,
        offer,
        price,
        high,
        low,
        change,
        direction,
        audit_id,
        status_summary,
    ):
        self.symbol_id = symbol_id
        self.symbol_name = symbol_name
        self.tick_datetime = tick_datetime
        self.bid = bid
        self.offer = offer
        self.price = price
        self.high = high
        self.low = low
        self.change = change
        self.direction = direction
        self.audit_id = audit_id
        self.status_summary = status_summary

    def __str__(self):
        return (
            f"{self.tick_datetime} | {self.symbol_name} | {self.bid} | {self.offer} | {self.change} | {self.direction}"
        )
