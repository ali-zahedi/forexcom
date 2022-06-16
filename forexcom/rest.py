import logging
import re
from functools import partial
from operator import itemgetter

import pandas as pd

from forexcom.exceptions import ForexException
from forexcom.utils import send_request

from .models import Currency, InstructionStatus, Order, OrderStatus, OrderType, Position

log = logging.getLogger()
SYMBOLS_INFO = {}


class RestClient:
    def __init__(self, username, password, app_key, http_proxy=None, https_proxy=None, rest_url=None):
        if rest_url is None:
            rest_url = 'https://ciapi.cityindex.com/tradingapi/'
        self._username = username
        self._password = password
        self._app_key = app_key
        self._rest_url = rest_url
        self._session = None
        self._get = partial(
            send_request,
            'GET',
            self._rest_url,
            json_format=True,
            http_proxy=http_proxy,
            https_proxy=https_proxy,
        )
        self._post = partial(
            send_request,
            'POST',
            self._rest_url,
            json_format=True,
            http_proxy=http_proxy,
            https_proxy=https_proxy,
        )
        self._session_token = None
        self._trading_account_id = None

    @property
    def _default_headers(self):
        return {'UserName': self._username, 'Session': self._session_token}

    @property
    def trading_account_id(self):
        return self._trading_account_id

    @property
    def session_token(self):
        return self._session_token

    @property
    def is_connect(self):
        return bool(self._session_token)

    def connect(self):
        log.debug('Connecting to REST API')
        data = {
            'UserName': self._username,
            'Password': self._password,
            'AppKey': self._app_key,
        }
        res = self._post('/session', params=data)
        status = InstructionStatus(int(res['StatusCode']))
        if status != InstructionStatus.Accepted:
            raise ForexException(res)
        self._session_token = res['Session']

    def get_account_info(self):
        log.debug('Getting account info')
        res = self._get('/UserAccount/ClientAndTradingAccount', headers=self._default_headers)
        try:
            self._trading_account_id = res['TradingAccounts'][0]['TradingAccountId']
            return res
        except Exception as e:
            raise ForexException(res) from e

    def get_symbol_detail(self, symbol):
        """
        :param symbol: symbol (e.g. EUR/USD)
        :return: symbol details
        """
        log.debug('Getting symbol details for %s', symbol)
        res = self._get('/cfd/markets', params={'MarketName': symbol}, headers=self._default_headers)

        try:
            global SYMBOLS_INFO
            SYMBOLS_INFO[symbol] = res['Markets'][0]['MarketId']
            return res
        except Exception as e:
            raise ForexException(res) from e

    def get_symbol_id(self, symbol):
        log.debug('Getting symbol id for %s', symbol)
        global SYMBOLS_INFO
        symbol_id = SYMBOLS_INFO.get(symbol, None)
        if not symbol_id:
            self.get_symbol_detail(symbol)
            symbol_id = SYMBOLS_INFO[symbol]
        return symbol_id

    def get_symbol_name(self, symbol_id):
        log.debug('Getting symbol name for %s', symbol_id)
        global SYMBOLS_INFO
        try:
            return list(SYMBOLS_INFO.keys())[list(SYMBOLS_INFO.values()).index(int(symbol_id))]
        except ValueError:
            log.debug('Symbol id %s not found', symbol_id)
        log.debug('Getting symbol name for %s from server', symbol_id)
        res = self._get(f'market/{symbol_id}/information', headers=self._default_headers)

        try:
            symbol = res['MarketInformation']['Name']
            SYMBOLS_INFO[symbol] = res['MarketInformation']['MarketId']
            log.debug('Symbol %s found', symbol)
            return symbol
        except Exception as e:
            raise ForexException(res) from e

    def get_prices(self, symbol, count=None, start=None, end=None, price_type='mid'):
        """
        :param symbol: symbol (e.g. EUR/USD)
        :param count: number of ticks to return
        :param start: start date/time (YYYY-MM-DDTHH:MM:SS)
        :param end: end date/time (YYYY-MM-DDTHH:MM:SS)
        :param price_type: price type (e.g. bid, ask, mid)
        :return: pd.DataFrame with prices
        """
        log.debug('Getting prices for %s', symbol)
        if price_type not in ['bid', 'ask', 'mid']:
            raise ForexException('Invalid price type')
        price_type = price_type.upper()
        params = {
            'maxResults': None,
            'PriceTicks': None,
            'priceType': price_type,
            'fromTimeStampUTC': None,
            'toTimestampUTC': None,
        }
        if start:
            start_datetime = pd.to_datetime(start)
            params['fromTimeStampUTC'] = int(start_datetime.timestamp())

        if end:
            end_datetime = pd.to_datetime(end)
            params['toTimestampUTC'] = int(end_datetime.timestamp())

        symbol_id = self.get_symbol_id(symbol)

        url = f'/market/{symbol_id}/'
        if start and end:
            url += 'tickhistorybetween'
        else:
            if not count:
                count = 1
            if start:
                url += 'tickhistorybefore'
                params['maxResults'] = count
            elif end:
                url += 'tickhistoryafter'
                params['maxResults'] = count
            else:
                url += 'tickhistory'
                params['PriceTicks'] = count
        params = dict(filter(itemgetter(1), params.items()))
        res = self._get(url, params=params, headers=self._default_headers)
        try:
            df = pd.DataFrame(
                map(lambda x: {'datetime': re.sub(r'\D', '', x['TickDate']), 'price': x['Price']}, res['PriceTicks']),
            )
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            df.datetime = df.datetime.dt.tz_localize('UTC')
            df.set_index('datetime', inplace=True)
            return df
        except Exception as e:
            raise ForexException(res) from e

    def cancel_order(self, trading_account_id, order_id):
        """
        It's use for only 'Pending' or 'Accepted' order status
        """
        log.debug('Cancel order %s-%s', trading_account_id, order_id)
        res = self._post(
            '/order/cancel',
            params={'OrderId': order_id, 'TradingAccountId': trading_account_id},
            headers=self._default_headers,
        )
        status = InstructionStatus(int(res['StatusCode']))
        if status != InstructionStatus.Accepted:
            raise ForexException(res)
        try:
            return res
        except Exception as e:
            raise ForexException(res) from e

    def order_market_price(
        self,
        client_account_id: int,
        trading_account_id,
        symbol: str,
        position: Position,
        offer_price: float,
        quantity: int,
    ):
        log.debug('create trade %s %s %s %s %s', trading_account_id, symbol, position, offer_price, quantity)
        symbol_id = self.get_symbol_id(symbol)
        res = self._post(
            '/order/newtradeorder',
            params={
                'TradingAccountId': trading_account_id,
                'MarketName': symbol,
                'MarketId': symbol_id,
                'Direction': position.name.lower(),
                'Quantity': quantity,
                'OfferPrice': offer_price,
            },
            headers=self._default_headers,
        )
        res['StatusCode'] = res['Status']
        status = InstructionStatus(int(res['StatusCode']))
        if status != InstructionStatus.Accepted:
            raise ForexException(res)
        try:
            data = res['Orders'][0]
            order_id = int(data['OrderId'])
            currency = Currency.Unknown
            open_price = float(data['Price'])
            original_quantity = float(data['Quantity'])
            order_type = OrderType(data['OrderTypeId'])
            status = OrderStatus(int(data['Status']))
            reason_id = int(data['StatusReason'])
            return Order(
                symbol_id=symbol_id,
                symbol_name=symbol,
                order_id=order_id,
                client_account_id=client_account_id,
                trading_account_id=trading_account_id,
                currency=currency,
                position=position,
                open_price=open_price,
                original_quantity=original_quantity,
                quantity=original_quantity,
                order_type=order_type,
                status=status,
                reason_id=reason_id,
            )
        except Exception as e:
            raise ForexException(res) from e
