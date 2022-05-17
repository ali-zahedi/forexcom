import logging
import re

import pandas as pd

from forexcom import RestClient, StreamerClient, StreamerSubscription
from forexcom.models.prices import Price

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
        self._rest.connect()
        self._streamer.set_username(self._username)
        self._streamer.set_password(self._rest.session_token)
        self._streamer.connect()

    def disconnect(self):
        for sub_key, symbol in self._subscriber:
            self._streamer.unsubscribe(self._subscriber[sub_key])
        self._streamer.disconnect()

    def get_account_info(self):
        return self._rest.get_account_info()

    def price_symbol_subscribe(self, symbol, callback):
        if symbol in self._subscriber:
            log.debug("Already subscribed to %s", symbol)
            return

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

    def price_symbol_unsubscribe(self, symbol):
        if symbol in self._subscriber:
            self._streamer.unsubscribe(self._subscriber[symbol][0])
            del self._subscriber[symbol]
        log.debug("Unsubscribed from %s", symbol)

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
