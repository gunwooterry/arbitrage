# Copyright (c) 2013 Alan McIntyre

import http.client
import json
import decimal
import ssl

decimal.getcontext().rounding = decimal.ROUND_DOWN
exps = [decimal.Decimal("1e-%d" % i) for i in range(16)]

domain = 'data.bter.com'

def parseJSONResponse(response):
    def parse_decimal(var):
        return decimal.Decimal(var)

    try:
        r = json.loads(response, parse_float=parse_decimal, parse_int=parse_decimal)
    except Exception as e:
        msg = "Error while attempting to parse JSON response: %s\nResponse:\n%r" % (e, response)
        raise Exception(msg)

    return r

class BTERConnection:
    def __init__(self, timeout=30):
        self.conn = http.client.HTTPSConnection(domain, timeout=timeout)

    def close(self):
        self.conn.close()

    def makeRequest(self, url, method='POST', extra_headers=None, params=''):
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        if extra_headers is not None:
            headers.update(extra_headers)

        self.conn.request(method, url, params, headers)
        response = self.conn.getresponse().read().decode()

        return response

    def makeJSONRequest(self, url, method='POST', extra_headers=None, params=""):
        response = self.makeRequest(url, method, extra_headers, params)
        return parseJSONResponse(response)

all_pairs = BTERConnection().makeJSONRequest("/api/1/pairs", method="GET")
all_currencies = list(set(sum([p.split('_') for p in all_pairs], [])))
max_digits = dict((pair, {"price": 8, "amount": 8}) for pair in all_pairs)
# min_orders = {'btc_cny': decimal.Decimal("0.1"),
#               'ltc_cny': decimal.Decimal("0.1"),
#               'ftc_cny': decimal.Decimal("0.1"),
#               'frc_cny': decimal.Decimal("0.1"),
#               'trc_cny': decimal.Decimal("0.1"),
#               'wdc_cny': decimal.Decimal("0.1"),
#               'yac_cny': decimal.Decimal("0.1"),
#               'cnc_cny': decimal.Decimal("0.1"),
#               'ftc_ltc': decimal.Decimal("0.1"),
#               'frc_ltc': decimal.Decimal("0.1"),
#               'ppc_ltc': decimal.Decimal("0.1"),
#               'trc_ltc': decimal.Decimal("0.1"),
#               'nmc_ltc': decimal.Decimal("0.1"),
#               'wdc_ltc': decimal.Decimal("0.1"),
#               'yac_ltc': decimal.Decimal("0.1"),
#               'cnc_ltc': decimal.Decimal("0.1"),
#               'bqc_ltc': decimal.Decimal("0.1"),
#               'ltc_btc': decimal.Decimal("0.1"),
#               'nmc_btc': decimal.Decimal("0.1"),
#               'ppc_btc': decimal.Decimal("0.1"),
#               'trc_btc': decimal.Decimal("0.1"),
#               'frc_btc': decimal.Decimal("0.1"),
#               'ftc_btc': decimal.Decimal("0.1"),
#               'bqc_btc': decimal.Decimal("0.1"),
#               'cnc_btc': decimal.Decimal("0.1"),
#               'btb_btc': decimal.Decimal("0.1"),
#               'yac_btc': decimal.Decimal("0.1"),
#               'wdc_btc': decimal.Decimal("0.1")}

fees = {k: 0.001 for k in list(max_digits.keys())}





def validatePair(pair):
    if pair not in all_pairs:
        if "_" in pair:
            a, b = pair.split("_")
            swapped_pair = "%s_%s" % (b, a)
            if swapped_pair in all_pairs:
                msg = "Unrecognized pair: %r -- did you mean %s?" % (pair, swapped_pair)
                raise Exception(msg)
        raise Exception("Unrecognized pair: %r" % pair)


def truncateAmountDigits(value, digits):
    quantum = exps[digits]
    return decimal.Decimal(value).quantize(quantum)


def truncateAmount(value, pair, price_or_amount):
    return truncateAmountDigits(value, max_digits[pair][price_or_amount])


def formatCurrencyDigits(value, digits):
    s = str(truncateAmountDigits(value, digits))
    dot = s.index(".")
    while s[-1] == "0" and len(s) > dot + 2:
        s = s[:-1]

    return s


def formatCurrency(value, pair, price_or_amount):
    return formatCurrencyDigits(value, max_digits[pair][price_or_amount])


def validateResponse(result, error_handler=None):
    #TODO: Proper error handling with Exception sublcass
    if type(result) is not dict:
        raise Exception('The response is not a dict.')

    if result['result'] == 'false' or not result['result']:
        if error_handler is None:
            raise Exception(errorMessage(result))
        else:
            result = error_handler(result)

    return result


def errorMessage(result):
    if 'message' in list(result.keys()):
        message = result['message']
    elif 'msg' in list(result.keys()):
        message = result['msg']
    else:
        message = result
    return message
