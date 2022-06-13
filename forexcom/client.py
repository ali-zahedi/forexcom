import logging
import re

import pandas as pd

from .lightstream import StreamerClient, StreamerSubscription
from .models import Order, OrderStatus, OrderType, Position, PositionMethod, Price
from .rest import RestClient

log = logging.getLogger()


class ForexComClient:
    def __init__(self, username, password, app_key, http_proxy=None, https_proxy=None, rest_url=None, stream_url=None):
        self._username = username
        self._password = password
        self._app_key = app_key
        self._http_proxy = http_proxy
        self._https_proxy = https_proxy
        self._rest_url = rest_url
        self._stream_url = stream_url
        self._rest = RestClient(username, password, app_key, http_proxy, https_proxy, rest_url)
        self._streamer = StreamerClient(self._stream_url, "STREAMINGALL")
        self._subscriber = {}

    def connect(self):
        if self._rest.is_connect:
            log.debug("Rest connected before.")
        else:
            self._rest.connect()

        self._streamer.set_username(self._username)
        self._streamer.set_password(self._rest.session_token)

        if self._streamer.is_connect:
            log.debug("Streamer connected before.")
        else:
            self._streamer.connect()

    def disconnect(self):
        for sub_key in self._subscriber.keys():
            self._streamer.unsubscribe(self._subscriber[sub_key][0])
        self._subscriber = {}
        self._streamer.disconnect()

    def get_account_info(self):
        return self._rest.get_account_info()

    def price_symbol_subscribe(self, symbol, callback):
        if not self._streamer.is_connect:
            log.debug("Streamer not connected.")
            return False

        if symbol in self._subscriber:
            log.debug("Already subscribed to %s", symbol)
            return True

        symbol_id = self._rest.get_symbol_id(symbol)

        # Making a new Subscription in MERGE mode
        subscription = StreamerSubscription(
            mode="MERGE",
            items=[f"PRICE.{symbol_id}"],
            fields=[
                "MarketId",
                "TickDate",
                "Bid",
                "Offer",
                "Price",
                "High",
                "Low",
                "Change",
                "Direction",
                "AuditId",
                "StatusSummary",
            ],
            adapter="PRICES",
        )
        subscription.addlistener(self.on_price_update)
        # Registering the Subscription
        sub_key = self._streamer.subscribe(subscription)
        self._subscriber[symbol] = (sub_key, callback)
        return True

    def price_symbol_unsubscribe(self, symbol):
        if symbol in self._subscriber:
            self._streamer.unsubscribe(self._subscriber[symbol][0])
            del self._subscriber[symbol]
        log.debug("Unsubscribed from %s", symbol)
        return True

    def on_price_update(self, data):
        log.debug("On price update: %s", data)
        data = data["values"]
        symbol_id = data['MarketId']
        symbol_name = self._rest.get_symbol_name(symbol_id)
        callback = self._subscriber[symbol_name][1]
        pattern = re.compile(r'Date\(([\d]+)\)')
        ts = pattern.search(data['TickDate'])[1].strip()
        tick_datetime = pd.to_datetime(ts, unit='ms').tz_localize('UTC')
        bid = data['Bid']
        offer = data['Offer']
        price = data['Price']
        high = data['High']
        low = data['Low']
        change = data['Change']
        direction = 1 if str(data['Direction']) == '1' else -1
        audit_id = data['AuditId']
        status_summary = data['StatusSummary']
        price = Price(
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
        )
        log.debug("Price update: %s", price)
        callback(price)

    def orders_subscribe(self, callback):
        if not self._streamer.is_connect:
            log.debug("Streamer not connected.")
            return False
        channel = 'ORDERS'
        if channel in self._subscriber:
            log.debug("Already subscribed to %s", channel)
            return True

        # Making a new Subscription in MERGE mode
        subscription = StreamerSubscription(
            mode="MERGE",
            items=[channel],
            fields=[
                "OrderId",
                "MarketId",
                "ClientAccountId",
                "TradingAccountId",
                "CurrencyId",
                "CurrencyISO",
                "Direction",
                "AutoRollover",
                "ExecutionPrice",
                "LastChangedTime",
                "OpenPrice",
                "OriginalLastChangedDateTime",
                "OriginalQuantity",
                "PositionMethodId",
                "Quantity",
                "Type",
                "Status",
                "ReasonId",
            ],
            adapter="ORDERS",
        )
        subscription.addlistener(self.on_orders_update)
        # Registering the Subscription
        sub_key = self._streamer.subscribe(subscription)
        self._subscriber[channel] = (sub_key, callback)
        return True

    def orders_unsubscribe(self):
        raise NotImplementedError

    def on_orders_update(self, data):
        log.debug("On orders update: %s", data)
        data = data["values"]
        pattern = re.compile(r'Date\(([\d]+)\)')
        ts = pattern.search(data['LastChangedTime'])[1].strip()
        last_changed_time = pd.to_datetime(ts, unit='ms').tz_localize('UTC')
        ts = pattern.search(data['OriginalLastChangedDateTime'])[1].strip()
        original_last_changed_date_time = pd.to_datetime(ts, unit='ms').tz_localize('UTC')

        symbol_id = data['MarketId']
        symbol_name = self._rest.get_symbol_name(symbol_id)
        callback = self._subscriber["ORDERS"][1]
        order_id = int(data['OrderId'])
        client_account_id = int(data['ClientAccountId'])
        trading_account_id = int(data['TradingAccountId'])
        currency = data['CurrencyId']
        position = Position(int(data['Direction']))
        auto_rollover = bool(data['AutoRollover'])
        execution_price = data['ExecutionPrice']
        open_price = float(data['OpenPrice'])
        original_quantity = float(data['OriginalQuantity'])
        position_method_id = PositionMethod(int(data['PositionMethodId']))
        quantity = float(data['Quantity'])
        order_type = OrderType(data['Type'])
        status = OrderStatus(data['Status'])
        reason_id = data['ReasonId']

        order = Order(
            order_id=order_id,
            symbol_id=symbol_id,
            symbol_name=symbol_name,
            client_account_id=client_account_id,
            trading_account_id=trading_account_id,
            currency=currency,
            position=position,
            auto_rollover=auto_rollover,
            execution_price=execution_price,
            open_price=open_price,
            last_changed_time=last_changed_time,
            original_last_changed_date_time=original_last_changed_date_time,
            original_quantity=original_quantity,
            position_method=position_method_id,
            quantity=quantity,
            order_type=order_type,
            status=status,
            reason_id=reason_id,
        )
        log.debug("Orders update: %s", order)
        callback(order)
