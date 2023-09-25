import os
import requests
import json
from datetime import datetime, timedelta
tokens_file = os.path.join(os.path.dirname(__file__), "daikin_tokens.json")
log_file = os.path.join(os.path.dirname(__file__), "daikin_log.json")


def read_tokens(file_name):
    if not os.path.exists(file_name):
        return {}
    with open(file_name, "r") as f:
        try:
            j = json.loads(f.read())
        except:
            j = {}
    return j


def check_login(j=None):
    if j is None:
        j = read_tokens()
    if "ExpiresIn" not in j or "refreshed" not in j:
        return False
    refresh_datetime = datetime.strptime(j["refreshed"], "%Y-%m-%d %H:%M:%S.%f")
    expiry = refresh_datetime + timedelta(seconds=j["ExpiresIn"])
    if expiry < datetime.now():
        return False
    return True


def refresh_tokens():
    j = read_tokens(tokens_file)
    url = "https://cognito-idp.eu-west-1.amazonaws.com"
    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "x-amz-target": "AWSCognitoIdentityProviderService.InitiateAuth",
    }
    data = {
        "ClientId": "7rk39602f0ds8lk0h076vvijnb",
        "AuthFlow": "REFRESH_TOKEN_AUTH",
        "AuthParameters": {
            "REFRESH_TOKEN": j["refresh_token"]
        }
    }
    r = requests.post(url, headers=headers, json=data)
    json_response = r.json()["AuthenticationResult"]
    j = store_tokens(json_response, tokens_file)
    return j


def write_tokens(j, file_name):
    with open(file_name, "w") as f:
        f.write(json.dumps(j, default=str, indent=4))


def store_tokens(json_response, file_name):
    j = read_tokens(file_name)
    for key in json_response:
        j[key] = json_response[key]
    j["refreshed"] = datetime.now()
    write_tokens(j, file_name)
    return j


def get_base_url():
    return "https://api.prod.unicloud.edc.dknadmin.be/v1/gateway-devices"


def get_temps():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temps = {now: {"hot_water_temp": 0, "heating_temp": 0}}
    devices = do_discovery()
    for device in devices:
        if device["managementPointType"] == "domesticHotWaterTank":
            temps[now]["hot_water_temp"] = device["sensoryData"]["value"]["tankTemperature"]["value"]
        elif device["managementPointType"] == "climateControl":
            temps[now]["heating_temp"] = device["sensoryData"]["value"]["roomTemperature"]["value"]
            temps[now]["outdoor_temp"] = device["sensoryData"]["value"]["outdoorTemperature"]["value"]
    store_tokens(temps, log_file)
    return temps


def do_discovery():
    j = read_tokens(tokens_file)
    if not check_login(j):
        j = refresh_tokens()
    devices = discover(j)
    store_devices(devices, tokens_file)
    return devices


def discover(j):
    url = get_base_url()
    headers = {
        "Authorization": "Bearer "+j["AccessToken"],
        "x-api-key": "xw6gvOtBHq5b1pyceadRp6rujSNSZdjx2AqT03iC"
    }
    r = requests.get(url, headers=headers)
    devices = r.json()[0]["managementPoints"]
    return devices


def store_devices(devices, file_name):
    j = read_tokens(file_name)
    j["devices"] = devices
    write_tokens(j, file_name)
