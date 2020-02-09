import sys
import json
import calendar
import time
import os
import jwt
import ast
import pathlib
from hyper import HTTPConnection

UTF_8 = 'utf-8'


def create_push_notification_request(secret_path, team_id, key_id, env):

    if not is_valid_env(env):
        print('APNs enviornment is not valid. Select either sand (Sandbox) or prod (Production)')
        return

    secret = read_from_file(secret_path)
    payload = get_payload()
    bundle_id = get_bundle_id()
    device_tokens = get_tokens()

    host = 'api.sandbox.push.apple.com:443' if env == 'sand' else 'api.push.apple.com:443'
    url = '/3/device/'

    epoch_time = time.time()
    header = {'alg': 'ES256', 'kid': key_id}
    payload_jwt = {'iss': team_id, 'iat': epoch_time}

    key_bytes = jwt.encode(payload=payload_jwt, key=secret,
                           algorithm='ES256', headers=header)

    key = key_bytes.decode(UTF_8)

    url_headers = {'Content-Type': 'application/json',
                   'Authorization': f'bearer {key}',
                   'apns-expiration': '0',
                   'apns-priority': '10',
                   'apns-push-type': 'alert',
                   'apns-topic': bundle_id
                   }
    payload_data = json.dumps(payload)

    for device_token in device_tokens:
        send_notification(host, url, device_token, payload_data, url_headers)


def is_valid_env(env):
    return env == "sand" or env == "prod"


def read_from_file(path):
    filehandle = open(path)
    contents = filehandle.read()
    filehandle.close()
    return contents


def read_lines_from_file(path):
    filehandle = open(path)
    contents = filehandle.readlines()
    filehandle.close()
    return contents


def get_payload():
    payload_path = get_script_directory() + "/payload.txt"
    raw_payload = read_from_file(payload_path)
    return ast.literal_eval(raw_payload)


def get_script_directory():
    return str(pathlib.Path(__file__).parent.absolute())


def get_bundle_id():
    bundle_path = get_script_directory() + "/bundle.txt"
    return read_from_file(bundle_path)


def get_tokens():
    tokens_path = get_script_directory() + "/tokens.txt"
    return read_lines_from_file(tokens_path)


def send_notification(host, url, device_token, payload, url_headers):
    conn = HTTPConnection(host)
    complete_url = url + device_token
    conn.request('POST', complete_url, payload, url_headers)
    respsone = conn.get_response()
    response_body = respsone.read()

    if not response_body:
        print(f'\nSuccess sending notification to: {device_token}')
    else:
        print(f'\nFailed to send notification to: {device_token}')
        print(f'Failure reason: {get_failure_reason(response_body)}')


def get_failure_reason(response_body):
    response = response_body.decode(UTF_8)
    response_dic = ast.literal_eval(response)
    return response_dic['reason']


create_push_notification_request(sys.argv[1], sys.argv[2],
                                 sys.argv[3], sys.argv[4])
