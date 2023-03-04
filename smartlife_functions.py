import os
import requests
import json
from datetime import datetime, timedelta
tokens_file = os.path.join(os.path.dirname(__file__), "smartlife_tokens.json")
regions = {
    "eu": "44",
    "44": "44",
    "us": "1",
    "1": "1",
    "cn": "86",
    "86": "86",
}


def check_login():
    j = read_tokens()
    if "expiry" not in j:
        return False
    expiry = j["expiry"]
    expiry_datetime = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S.%f")
    if expiry_datetime < datetime.now():
        return False
    return True


def get_base_url(region):
    if region == "44":
        return "https://px1.tuyaeu.com/homeassistant/"
    if region == "1":
        return "https://px1.tuyaus.com/homeassistant/"
    return "https://px1.tuyacn.com/homeassistant/"


def login(device):
    username = device["username"]
    password = device["password"]
    region = regions[str(device["region"]).lower()]
    base_url = get_base_url(region)
    url = base_url + "auth.do"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "userName": username,
        "password": password,
        "countryCode": region,
        "bizType": "smart_life",
        "from": "tuya",
    }
    r = requests.post(url, headers=headers, data=data)
    j = r.json()
    if "responseStatus" in j and j["responseStatus"] == "error":
        return None
    j["base_url"] = base_url
    j = store_tokens(j)
    j["devices"] = do_discovery(False)
    return j


def do_discovery(refresh=True):
    if refresh:
        j = refresh_tokens()
    else:
        j = read_tokens()
    devices = discover(j)
    store_devices(devices)
    return devices


def store_devices(devices):
    j = read_tokens()
    j["devices"] = devices
    write_tokens(j)


def read_tokens():
    if not os.path.exists(tokens_file):
        return {}
    with open(tokens_file, "r") as f:
        try:
            j = json.loads(f.read())
        except:
            j = {}
    return j


def write_tokens(j):
    with open(tokens_file, "w") as f:
        f.write(json.dumps(j, default=str, indent=4))


def store_tokens(json_response):
    j = read_tokens()
    for key in json_response:
        j[key] = json_response[key]
    if "expires_in" in json_response:
        j["expiry"] = datetime.now() + timedelta(seconds=j["expires_in"])
    j["refreshed"] = datetime.now()
    write_tokens(j)
    return j


def discover(j):
    url = j["base_url"] + "skill"
    headers = {"Content-Type": "application/json"}
    data = {
        "header": {
            "name": "Discovery",
            "namespace": "discovery",
            "payloadVersion": 1,
        },
        "payload": {
            "accessToken": j["access_token"],
        },
    }
    r = requests.post(url, headers=headers, json=data)
    if "payload" in r.json() and "devices" in r.json()["payload"]:
        devices = r.json()["payload"]["devices"]
    else:
        devices = j["devices"]
    return devices


def refresh_tokens():
    j = read_tokens()
    url = j["base_url"] + "access.do"
    params = {
        "grant_type": "refresh_token",
        "refresh_token": j["refresh_token"],
    }
    r = requests.get(url, params=params)
    json_response = r.json()
    j = store_tokens(json_response)
    return j


def turn_on_off(j, device_id, value):
    url = j["base_url"] + "skill"
    headers = {"Content-Type": "application/json"}
    data = {
        "header": {
            "name": "turnOnOff",
            "namespace": "control",
            "payloadVersion": 1
        },
        "payload": {
            "accessToken": j["access_token"],
            "devId": device_id,
            "value": value
        }
    }
    r = requests.post(url, headers=headers, json=data)
    return r.json()["header"]["code"] == "SUCCESS"


def get_device_id(devices, device_name):
    device_id = None
    for device in devices:
        if device["name"].lower() == device_name.lower():
            device_id = device["id"]
            break
    return device_id


def is_device_on(j, device_id):
    for device in j["devices"]:
        if device["id"] == device_id:
            return device["data"]["state"]


def update_device_status(j, device_id, value):
    for device in j["devices"]:
        if device["id"] == device_id:
            device["data"]["state"] = value
            break
    write_tokens(j)


def switch_smartlife_device(device, turn_on):
    if not check_login():
        j = login(device)
        if j is None:
            return False
    else:
        j = read_tokens()
        j["devices"] = do_discovery(True)
    device_id = get_device_id(j["devices"], device["device_name"])
    if device_id is None:
        return False
    device_on = is_device_on(j, device_id)
    if device_on and not turn_on:
        if turn_on_off(j, device_id, "0"):
            update_device_status(j, device_id, turn_on)
            return True
    elif turn_on and not device_on:
        if turn_on_off(j, device_id, "1"):
            update_device_status(j, device_id, turn_on)
            return True
    return False
