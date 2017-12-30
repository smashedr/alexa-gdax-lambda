import json
import os
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TXT_UNKNOWN = 'I did not understand that request, please try something else.'
TXT_ERROR = 'Error looking up {}, please try something else.'

CURRENCIES = {
    'bitcoin': 'BTC',
    'bitcoin cash': 'BCH',
    'litecoin': 'LTC',
    'ethereum': 'ETH',
}

PRODUCTS = {
    'bitcoin': 'BTC-USD',
    'bitcoin cash': 'BCH-USD',
    'litecoin': 'LTC-USD',
    'ethereum': 'ETH-USD',
}


def build_speech_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def alexa_response(session_attributes, speech_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speech_response
    }


def alexa_error(error='Unknown error, please try something else', title='UE'):
    alexa = alexa_response(
        {}, build_speech_response(title, error, None, True)
    )
    return alexa


def ez_alexa(msg, title):
    alexa = alexa_response(
        {}, build_speech_response(title, msg, None, True)
    )
    return alexa


def round_usd(in_float):
    return round(float(in_float), 2)


def no_float(in_float):
    return int(str(in_float).replace('.', ''))


def coin_status(event):
    try:
        value = event['request']['intent']['slots']['currency']['value']
        value = value.lower().replace('define', '').strip()
        value = value.lower().replace('lookup', '').strip()
        value = value.lower().replace('look up', '').strip()
        value = value.lower().replace('search', '').strip()
        value = value.lower().replace('find', '').strip()
        print('value: {}'.format(value))
        if value in PRODUCTS:
            url = 'https://api.gdax.com/products/{}/stats'.format(
                PRODUCTS[value]
            )
            r = requests.get(url)
            d = json.loads(r.content.decode())
            speech = ('{} stats for the last 24 hours. '
                       'The low was {}, the high was {} '
                       'and the last price is {}').format(
                PRODUCTS[value][:3],
                round_usd(d['high']),
                round_usd(d['low']),
                round_usd(d['last']),
            )
            return ez_alexa(speech, 'Coin Status')
        else:
            msg = 'Unknown currency {}. Please try one of: {}'.format(
                value, ', '.join([*PRODUCTS])
            )
            return alexa_error(error=msg)

    except Exception as error:
        print('error: {}'.format(error))
        return alexa_error(error=TXT_UNKNOWN)


def acct_overview(event):
    try:
        url = 'https://dev.alexa-gdax.space/api/accounts/'
        data = {
            'api_token': os.environ.get('api_token'),
            'key': os.environ.get('access_token'),
        }
        r = requests.post(url, data=data)
        d = json.loads(r.content.decode())

        accts = []
        for a in d:
            if int(a['balance'].replace('.', '')) > 0:
                c = {
                    'balance': a['balance'],
                    'currency': a['currency'],
                    'available': a['available'],
                    'hold': a['hold'],
                }
                accts.append(c)

        if not accts:
            msg = 'No accounts with currency found.'
            ar = ez_alexa(msg, 'Accounts Overview')
            print(ar)
            return ar

        speech = 'Found {} account{} of interest. '.format(
            len(accts), 's' if len(accts) > 1 else ''
        )
        for a in accts:
            if a['currency'] == 'USD':
                balance = '{} dollars'.format(
                    round_usd(a['balance'])
                )
                available = round_usd(a['available'])
                hold = round_usd(a['hold'])
            else:
                balance = a['balance']
                if balance.endswith('0'):
                    balance = '{}0'.format(balance.rstrip('0'))
                available = a['available']
                if available.endswith('0'):
                    available = '{}0'.format(available.rstrip('0'))
                hold = a['hold']
                if hold.endswith('0'):
                    hold = '{}0'.format(hold.rstrip('0'))

            speech += '{} account contains {}. '.format(
                a['currency'], balance
            )
            if no_float(available) > 0 \
                    and round_usd(a['balance']) != round_usd(a['available']):
                speech += '{} is available '.format(available)

            if no_float(hold) > 0:
                speech += 'with {} on hold. '.format(hold)

        ar = ez_alexa(speech, 'Accounts Overview')
        print(ar)
        return ar
    except Exception as error:
        print(error)
        logger.exception(error)
        return alexa_error()


def lambda_handler(event, context):
    print('event: {}'.format(event))
    os.environ["access_token"] = event['session']['user']['accessToken']
    try:
        intent = event['request']['intent']['name']
        if intent == 'AccountOverview':
            return acct_overview(event)
        elif intent == 'CoinStatus':
            return coin_status(event)
        else:
            raise ValueError('Unknown Intent')
    except ValueError:
        return alexa_error()
    except Exception as error:
        print('error: {}'.format(error))
        return alexa_error()
