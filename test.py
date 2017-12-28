from lambda_function import lambda_handler


def test_data(term):
    data = {
        'context': {
            'AudioPlayer': {'playerActivity': 'IDLE'},
            'System': {
                'apiAccessToken': 'xxxxxxxxxx',
                'apiEndpoint': 'https://api.amazonalexa.com',
                'application': {'applicationId': 'amzn1.ask.skill.xxxxxxxxxx'},
                'device': {
                    'deviceId': 'amzn1.ask.device.XXXXXXXXXX',
                    'supportedInterfaces': {'AudioPlayer': {}}
                },
                'user': {'userId': 'amzn1.ask.account.XXXXXXXXXX'}
            }
        },
        'request': {
            'intent': {
                'confirmationStatus': 'NONE',
                'name': 'UrbanLookup',
                'slots': {
                    'term': {
                        'confirmationStatus': 'NONE',
                        'name': 'term',
                        'value': term
                    }
                }
            },
            'locale': 'en-US',
            'requestId': 'amzn1.echo-api.request.xxxxxxxxxx',
            'timestamp': '2017-12-27T03:31:56Z',
            'type': 'IntentRequest'
        },
        'session': {
            'application': {'applicationId': 'amzn1.ask.skill.xxxxxxxxxx'},
            'new': True,
            'sessionId': 'amzn1.echo-api.session.xxxxxxxxxx',
            'user': {'userId': 'amzn1.ask.account.XXXXXXXXXX'}
        },
        'version': '1.0'
    }
    return data


if __name__ == '__main__':
    bad_resp = lambda_handler({}, None)
    error_resp = lambda_handler(test_data('notarealword'), None)
    good_resp = lambda_handler(test_data('python'), None)
    if not good_resp or not error_resp or not bad_resp:
        raise ValueError('Error: missing alexa_resp')  # pragma: no cover
