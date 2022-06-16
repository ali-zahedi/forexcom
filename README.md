<!--![GitHub All Releases](https://img.shields.io/github/downloads/ali-zahedi/forex/total)-->
<!--![GitHub issues](https://img.shields.io/github/issues/ali-zahedi/forex)-->
![GitHub](https://img.shields.io/github/license/ali-zahedi/forex)
![GitHub](https://img.shields.io/pypi/pyversions/forex.svg?maxAge=2592000)
![GitHub](https://img.shields.io/pypi/v/forex.svg?maxAge=2592000)
# Forex.com config

[[_TOC_]]

This project is to help you use [Forex.com](https://forex.com) [docs gain capital](http://docs.labs.gaincapital.com/#Getting%20Started/Getting%20Started.htm?TocPath=Getting%2520Started%257C_____0). 

## Compatibility

* Python 3.6+

## Installation

* Use the following command to install using pip:

```bash
pip install forexcom
```

**OR** 

* You can use the following command to set it up locally so that you can fix bugs or whatever and send pull requests:

```shell script
pip install -e ".[dev]"
pre-commit install
```
For better understanding, please read the:
* [Gain Capital](http://docs.labs.gaincapital.com/#API%20Intro.htm?TocPath=_____2) documentation.
* [pre-commit](https://pre-commit.com/docs/installation/) documentation.
* [pip](https://pip.pypa.io/en/stable/installing/) documentation.
* [python package](https://packaging.python.org/en/latest/tutorials/packaging-projects/) documentation.
* [github pull requests](https://help.github.com/en/articles/about-pull-requests/) documentation.

## API Access

Before working with Forex.com’s API, you need to get your own **AppKey**. you must contact [Forex.com](forexcom) service team to connect their REST API with your standard account or email to [support.en@forex.com](mailto:support.en@forex.com). It's usually take 3 working days.

## Usage

Initialize connection: 

```python
import logging
import sys
from forexcom import ForexComClient

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-7s ' +
                    '%(threadName)-15s %(message)s', level=logging.INFO) # You can change it to logging.DEBUG

log = logging.getLogger()

username = '<USERNAME>'
password='<PASSWORD>'
app_key = '<APP_KEY>'

client = ForexComClient(username, password, app_key)
client.connect()
```

### Connect to streamer

#### Subscribe to symbol

```python

symbol = 'EUR/USD'
symbol_2 = 'XAU/USD'

def print_price(price):
    print(price.symbol_name, price.bid, price.offer, price.low, price.high, price.price, sep=' | ')

index_symbol_sub = client.price_symbol_subscribe(symbol, print_price)
index_symbol_2_sub = client.price_symbol_subscribe(symbol_2, print_price)
```

* output:

```
XAU/USD | 1819.58 | 1820.22 | 1818.02 | 1836.16 | 1819.90
XAU/USD | 1819.57 | 1820.23 | 1818.02 | 1836.16 | 1819.90
XAU/USD | 1819.57 | 1820.22 | 1818.02 | 1836.16 | 1819.89
XAU/USD | 1819.57 | 1820.23 | 1818.02 | 1836.16 | 1819.90
XAU/USD | 1819.58 | 1820.19 | 1818.02 | 1836.16 | 1819.89
EUR/USD | 1.05478 | 1.05483 | 1.04284 | 1.05556 | 1.05480
EUR/USD | 1.05478 | 1.05484 | 1.04284 | 1.05556 | 1.05481
EUR/USD | 1.05479 | 1.05484 | 1.04284 | 1.05556 | 1.05481
EUR/USD | 1.05478 | 1.05484 | 1.04284 | 1.05556 | 1.05481
XAU/USD | 1819.62 | 1820.20 | 1818.02 | 1836.16 | 1819.91
XAU/USD | 1819.52 | 1820.17 | 1818.02 | 1836.16 | 1819.84
EUR/USD | 1.05479 | 1.05484 | 1.04284 | 1.05556 | 1.05481
XAU/USD | 1819.48 | 1820.16 | 1818.02 | 1836.16 | 1819.82
EUR/USD | 1.05478 | 1.05484 | 1.04284 | 1.05556 | 1.05481
XAU/USD | 1819.49 | 1820.17 | 1818.02 | 1836.16 | 1819.82
XAU/USD | 1819.48 | 1820.16 | 1818.02 | 1836.16 | 1819.82
XAU/USD | 1819.40 | 1820.13 | 1818.02 | 1836.16 | 1819.76
XAU/USD | 1819.41 | 1820.13 | 1818.02 | 1836.16 | 1819.77
EUR/USD | 1.05479 | 1.05484 | 1.04284 | 1.05556 | 1.05481
EUR/USD | 1.05478 | 1.05484 | 1.04284 | 1.05556 | 1.05481
EUR/USD | 1.05477 | 1.05485 | 1.04284 | 1.05556 | 1.05481
EUR/USD | 1.05478 | 1.05485 | 1.04284 | 1.05556 | 1.05482
EUR/USD | 1.05476 | 1.05483 | 1.04284 | 1.05556 | 1.05480
```

#### Unsubscribe from symbol

```python
client.unsubscribe_listener(index_symbol_sub)
client.unsubscribe_listener(index_symbol_2_sub)

# OR it's effect all subscribers
client.unsubscribe(symbol)
client.unsubscribe(symbol_2)

```

### Subscribe orders

```python
def print_order(order):
    print(order)

index_order_sub = client.orders_subscribe(print_order)
```

* output:

```
2022-06-13 16:57:43+00:00 | 839396383 | XAU/USD | Position.Buy | PositionMethod.LongOrShortOnly | OrderType.Trade | OrderStatus.Open | 1 | 1828.36 | CityIndex.Atlas.Business.OrderExecutionPrice | 4.0 | 4.0
2022-06-13 16:58:02+00:00 | 839396439 | XAU/USD | Position.Sell | PositionMethod.LongOrShortOnly | OrderType.Limit | OrderStatus.Accepted | 1 | 0.0 | CityIndex.Atlas.Business.OrderExecutionPrice | 4.0 | 4.0
2022-06-13 16:57:43+00:00 | 839396383 | XAU/USD | Position.Buy | PositionMethod.LongOrShortOnly | OrderType.Trade | OrderStatus.Open | 1 | 1828.36 | CityIndex.Atlas.Business.OrderExecutionPrice | 4.0 | 4.0
2022-06-13 16:58:05+00:00 | 839396448 | XAU/USD | Position.Sell | PositionMethod.LongOrShortOnly | OrderType.Trade | OrderStatus.Closed | 1 | 1829.15 | CityIndex.Atlas.Business.OrderExecutionPrice | 4.0 | 0.0
2022-06-13 16:58:05+00:00 | 839396439 | XAU/USD | Position.Sell | PositionMethod.LongOrShortOnly | OrderType.Limit | OrderStatus.Cancelled | 100 | 0.0 | CityIndex.Atlas.Business.OrderExecutionPrice | 4.0 | 0.0
```

### Unsubscribe
```python
client.unsubscribe_listener(index_order_sub)
# OR completely unsubscribe. it's effect all subscribers
client.orders_unsubscribe()
```

### Get Account info


```python
account_info = client.get_account_info()
print(account_info)
```

* output: 
```
{'LogonUserName': 'Ali **', 'ClientAccountId': *****, 'CultureId': **, 'ClientAccountCurrency': 'EUR', 'AccountOperatorId': ******, 'TradingAccounts': [{'TradingAccountId': ****, 'TradingAccountCode': '****', 'TradingAccountStatus': 'Open', 'TradingAccountType': 'CFD'}], 'PersonalEmailAddress': '*****', 'HasMultipleEmailAddresses': ***, 'AccountHolders': [{'LegalPartyId': ****, 'Name': ' ****'}], 'ClientTypeId': **, 'LinkedClientAccounts': [], 'IsNfaEnabledClient': False, 'IsFifo': None, 'DaysUntilExpiryForDemo': *****, 'LegalPartyUniqueReference': ****, 'Is2FAEnabledAO': ****, 'Regulatory': {'IsMiFIDRegulator': True, 'IsPiisProvided': False, 'ClientAccountCreationDate': '/Date(*******)/'}, 'IsDMAClient': False, 'Contract': {'ContractId': ****, 'IsNIGO': False}, 'Restrictions': {'CloseOnly': False}}
```

### Trade

```python
from forexcom import Position
symbol = "EUR/USD"
position = Position.Buy
offer_price = 1.055
quantity = 1000
order = client.order_market_price(symbol, position, quantity, offer_price)
print(order)
```

* output:

```python
None | 839931205 | EUR/USD | Position.Buy | PositionMethod.LongOrShortOnly | OrderType.Trade | OrderStatus.Open | 1 | 1.03917 | 1000.0 | 1000.0
```

### Disconnect 
```python
client.disconnect()
```

## Use Rest API
```python
from forexcom import RestClient
r = RestClient(username=username, password=password, app_key=app_key)
r.connect()
```

### Get prices:

Maximum number of items: **4000**


* Get 100 most recent trades:

```python

res = r.get_prices('EUR/USD', count=100, price_type='mid') # price_type = [ask, bid, mid]

log.debug("Get prices results:")
log.debug(res)
```

output:

```
                                  price
datetime                                 
2022-05-11 16:04:43.566000+00:00  1.05379
2022-05-11 16:04:43.816000+00:00  1.05382
2022-05-11 16:04:44.066000+00:00  1.05383
2022-05-11 16:04:44.317000+00:00  1.05379
2022-05-11 16:04:44.567000+00:00  1.05380
                                   ...
2022-05-11 16:05:25.857000+00:00  1.05422
2022-05-11 16:05:27.368000+00:00  1.05423
2022-05-11 16:05:27.618000+00:00  1.05422
2022-05-13 07:32:16.461000+00:00  1.04057
2022-05-13 07:32:16.779000+00:00  1.04055
[100 rows x 1 columns]
```

* Get from date to date:

```python

res = r.get_prices('EUR/USD', start='2022-05-01', end='2022-05-10')

log.debug("Get prices results:")
log.debug(res)
```

output (it's more than 4000 records, so it's **not fetching** all of them):

```
                                  price
datetime                                 
2022-05-04 22:37:47.472000+00:00  1.06115
2022-05-04 22:37:52.084000+00:00  1.06115
2022-05-04 22:37:52.333000+00:00  1.06115
2022-05-04 22:37:56.513000+00:00  1.06116
2022-05-04 22:37:56.763000+00:00  1.06119
                                   ...
2022-05-08 22:59:54.623000+00:00  1.05381
2022-05-08 22:59:54.872000+00:00  1.05381
2022-05-08 22:59:56.542000+00:00  1.05381
2022-05-08 22:59:56.792000+00:00  1.05381
2022-05-08 22:59:57.042000+00:00  1.05380
[4000 rows x 1 columns]
```

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.
