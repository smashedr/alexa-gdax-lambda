import json
import os
import requests

TXT_UNKNOWN = 'I did not understand that request, please try something else.'
TXT_ERROR = 'Error looking up {}, please try something else.'

KEYS = {
    'bitcoin': 'BTC',
    'bitcoin cash': 'BCH',
    'litecoin': 'LTC',
    'ethereum': 'ETH',
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


def acct_overview(event):
    url = 'https://dev.alexa-gdax.space/api/accounts/'
    data = {
        'api_token': os.environ.get('api_token'),
        'key': os.environ.get('access_token'),
    }
    r = requests.post(url, data=data)
    d = json.loads(r.content)

    accts = []
    for a in d:
        if int(a['balance'].replace('.', '')) > 0:
            c = {'balance': a['balance'], 'currency': a['currency']}
            accts.append(c)

    if not accts:
        msg = 'No accounts with currency found.'
        alexa = alexa_response(
            {},
            build_speech_response(
                'Accounts Overview', msg, None, True
            )
        )
        return alexa

    speech = 'Found {} account{} of interest. '.format(
        len(accts), 's' if len(accts) > 1 else ''
    )
    for a in accts:
        if a['currency'] == 'USD':
            balance = '{} dollars'.format(
                round(float(a['balance']), 2)
            )
        else:
            balance = a['balance']
        speech += '{} contains {}'.format(
            a['currency'], balance
        )

    alexa = alexa_response(
        {},
        build_speech_response(
            'Accounts Overview', speech, None, True
        )
    )
    return alexa


def lambda_handler(event, context):
    print('event: {}'.format(event))
    os.environ["access_token"] = event['session']['user']['accessToken']
    try:
        intent = event['request']['intent']['name']
        if intent == 'AccountOverview':
            return acct_overview(event)
        else:
            raise ValueError('Unknown Intent')
    except ValueError:
        return alexa_error()
    except Exception as error:
        print('error: {}'.format(error))
        return alexa_error()
