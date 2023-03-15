import requests
from time import sleep


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
    value = get_inverter_setting(headers, 77, inverter_id)
    return value


def set_AC_charge_limit(headers, value, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    # Set AC charge limit percentage
    success = set_inverter_setting(headers, 77, value, inverter_id)
    if success and value < 100:
        # enable AC charge upper limit
        success = set_inverter_setting(headers, 17, True, inverter_id)
    return success


def is_DC_discharging(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    return get_inverter_setting(headers, 56)


def switch_DC_discharging(headers, value, inverter_id=None):
    changed = False
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    is_discharging = is_DC_discharging(headers, inverter_id)
    if value is True and is_discharging is False:
        changed = start_DC_discharging(headers, inverter_id)
    if value is False and is_discharging is True:
        changed = end_DC_discharging(headers, inverter_id)
    return changed


def start_DC_discharging(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    # Disable Eco mode
    success = set_eco_mode(headers, False)
    if success:
        # set Discharge 2 start time
        sleep(5)
        success = set_inverter_setting(headers, 41, "00:00", inverter_id)
    if success:
        # set Discharge 2 end time
        sleep(5)
        success = set_inverter_setting(headers, 42, "23:59", inverter_id)
    if success:
        # enable DC discharge
        sleep(5)
        success = set_inverter_setting(headers, 56, True, inverter_id)
    if success:
        # disable AC charge
        sleep(5)
        success = set_inverter_setting(headers, 66, False, inverter_id)
    return success


def end_DC_discharging(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    # Enable Eco mode
    success = set_eco_mode(headers, True)
    if success:
        # set Discharge 2 start time
        sleep(5)
        success = set_inverter_setting(headers, 41, "00:00", inverter_id)
    if success:
        # set Discharge 2 end time
        sleep(5)
        success = set_inverter_setting(headers, 42, "00:00", inverter_id)
    if success:
        # disable DC discharge
        sleep(5)
        success = set_inverter_setting(headers, 56, False, inverter_id)
    if success:
        # enable AC charge
        sleep(5)
        success = set_inverter_setting(headers, 66, True, inverter_id)
    return success


def set_eco_mode(headers, value, inverter_id=None):
    success = False
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    url = 'https://api.givenergy.cloud/v1/inverter/'+inverter_id+'/presets/0'
    payload = { "enabled": value }
    for i in range(5):
        r = requests.post(url, headers=headers, json=payload)
        if 'data' in r.json() and 'success' in r.json()['data']:
            success = r.json()['data']['success']
        if success:
            break
        sleep(60)
    return success


def set_inverter_setting(headers, setting_no, value, inverter_id=None):
    success = False
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    url = 'https://api.givenergy.cloud/v1/inverter/'+inverter_id+'/settings/'+str(setting_no)+'/write'
    payload = { "value": value }
    for i in range(3):
        r = requests.post(url, headers=headers, json=payload)
        if 'data' in r.json() and 'success' in r.json()['data']:
            success = r.json()['data']['success']
        if success:
            break
        sleep(60)
    return success


def get_inverter_setting(headers, setting_no, inverter_id=None):
    value = None
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    url = 'https://api.givenergy.cloud/v1/inverter/'+inverter_id+'/settings/'+str(setting_no)+'/read'
    r = requests.post(url, headers=headers)
    if 'data' in r.json() and 'value' in r.json()['data']:
        value = r.json()['data']['value']
    return value
