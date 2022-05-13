import re
from functools import partial
from operator import itemgetter

import pandas as pd

from forexcom.exceptions import ForexException
from forexcom.utils import send_request

INSTRUMENTS_INFO = {}


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

    def connect(self):
        data = {
            'UserName': self._username,
            'Password': self._password,
            'AppKey': self._app_key,
        }
        res = self._post('/session', params=data)
        if res['StatusCode'] != 1:
            raise ForexException(res)
        self._session_token = res['Session']

        return self._session_token is not None

    def get_account_info(self):
        res = self._get('/UserAccount/ClientAndTradingAccount', headers=self._default_headers)
        try:
            self._trading_account_id = res['TradingAccounts'][0]['TradingAccountId']
            return res
        except Exception as e:
            raise ForexException(res) from e

    def get_instrument_detail(self, instrument):
        """
        :param instrument: instrument (e.g. EUR/USD)
        :return: instrument details
        """
        res = self._get('/cfd/markets', params={'MarketName': instrument}, headers=self._default_headers)

        try:
            global INSTRUMENTS_INFO
            INSTRUMENTS_INFO[instrument] = res['Markets'][0]['MarketId']
            return res
        except Exception as e:
            raise ForexException(res) from e

    def get_instrument_id(self, instrument):
        global INSTRUMENTS_INFO
        instrument_id = INSTRUMENTS_INFO.get(instrument, None)
        if not instrument_id:
            self.get_instrument_detail(instrument)
            instrument_id = INSTRUMENTS_INFO[instrument]
        return instrument_id

    def get_prices(self, instrument, count=None, start=None, end=None, price_type='MID'):
        """
        :param instrument: instrument (e.g. EUR/USD)
        :param count: number of ticks to return
        :param start: start date/time (YYYY-MM-DDTHH:MM:SS)
        :param end: end date/time (YYYY-MM-DDTHH:MM:SS)
        :param price_type: price type (e.g. BID, ASK, MID)
        :return: pd.DataFrame with prices
        """
        if price_type not in ['BID', 'ASK', 'MID']:
            raise ForexException('Invalid price type')
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

        instrument_id = self.get_instrument_id(instrument)

        url = f'/market/{instrument_id}/'
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
