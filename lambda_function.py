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
    url = 'https://api.gdax.com/accounts'
    alexa = alexa_response(
        {},
        build_speech_response(
            'Accounts Overview', 'Coming soon...', None, True
        )
    )
    return alexa


def lambda_handler(event, context):
    print('event: {}'.format(event))
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
