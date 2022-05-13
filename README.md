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
from forexcom import RestClient

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-7s ' +
                    '%(threadName)-15s %(message)s', level=logging.DEBUG)
log = logging.getLogger()

username = '<USERNAME>'
password='<PASSWORD>'
app_key = '<APP_KEY>'

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
