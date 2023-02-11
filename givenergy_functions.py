import requests
from general_functions import get_headers


def get_battery_level(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        return system_data["error"]
    else:
        return system_data["data"]["battery"]["percent"]


def get_grid_voltage(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        return system_data["error"]
    else:
        return system_data["data"]["grid"]["voltage"]


def get_solar_power(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        return system_data["error"]
    else:
        return system_data["data"]["solar"]["power"]


def get_consumption(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        return system_data["error"]
    else:
        return system_data["data"]["consumption"]


def get_communication_devices(headers):
    url = "https://api.givenergy.cloud/v1/communication-device"
    params = {"page": "1"}
    r = requests.get(url, headers=headers, params=params)
    return r.json()


def get_inverter_id(headers):
    devices = get_communication_devices(headers)
    if "data" in devices:
        return devices["data"][0]["inverter"]["serial"]
    else:
        return None


def get_latest_system_data(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    if inverter_id is None:
        return {"error": "I wasn't able to get device data from your system. Please try re-linking the skill."}
    url = "https://api.givenergy.cloud/v1/inverter/"+inverter_id+"/system-data/latest"
    r = requests.get(url, headers=headers)
    return r.json()


def get_inverter_status(headers):
    devices = get_communication_devices(headers)
    inverter_status = devices["data"][0]["inverter"]["status"]
    return inverter_status


def restart_inverter(headers):
    inverter_id = get_inverter_id(headers)
    url = "https://givenergy.cloud/internal-api/inverter/actions/"+inverter_id+"/restart"
    r = requests.post(url, headers=headers)
    return r.json()


def get_AC_charge_limit(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    url = 'https://api.givenergy.cloud/v1/inverter/'+inverter_id+'/settings/77/read'
    r = requests.post(url, headers=headers)
    if 'data' in r.json() and 'value' in r.json()['data']:
        return r.json()['data']['value']
    return None


def set_AC_charge_limit(headers, value, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    url = 'https://api.givenergy.cloud/v1/inverter/'+inverter_id+'/settings/77/write'
    payload = { "value": value }
    r = requests.post(url, headers=headers, json=payload)
    success = False
    if 'data' in r.json() and 'success' in r.json()['data']:
        success = r.json()['data']['success']
    if success and value < 100:
        # enable AC charge upper limit
        url = 'https://api.givenergy.cloud/v1/inverter/'+inverter_id+'/settings/17/write'
        payload = { "value": True }
        r = requests.post(url, headers=headers, json=payload)
        if 'data' in r.json() and 'success' in r.json()['data']:
            success = r.json()['data']['success']
        else:
            success = False
    return success
