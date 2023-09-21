#!/usr/bin/env python3

import cgi
import json
import argparse
import requests
from time import sleep
from general_functions import read_json, get_headers


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


def is_in_eco_mode(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    return get_inverter_setting(headers, 24, inverter_id)


def is_in_paused_mode(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    battery_discharge_power = get_inverter_setting(headers, 73, inverter_id)
    return battery_discharge_power < 100


def switch_DC_discharging(headers, value, inverter_id=None):
    changed = False
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    in_eco_mode = is_in_eco_mode(headers, inverter_id)
    if value is True and in_eco_mode is True:
        changed = start_DC_discharging(headers, inverter_id)
    if value is False and in_eco_mode is False:
        changed = end_DC_discharging(headers, inverter_id)
    return changed


def start_DC_discharging(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    # Disable Eco mode
    success = set_inverter_setting(headers, 24, False, inverter_id)
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
    success = set_inverter_setting(headers, 24, True, inverter_id)
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


def switch_battery_use(headers, value, inverter_id=None):
    # value == True means use the battery
    # value == False means dont use the battery
    changed = False
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    is_paused = is_in_paused_mode(headers, inverter_id)
    if value is True and is_paused is True:
        changed = resume_battery_use(headers, inverter_id)
    if value is False and is_paused is False:
        changed = pause_battery_use(headers, inverter_id)
    return changed


def pause_battery_use(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    # Set zero battery charge power
    success = set_inverter_setting(headers, 72, 0, inverter_id)
    if success:
        # set zero battery discharge power
        sleep(5)
        success = set_inverter_setting(headers, 73, 0, inverter_id)
    return success


def resume_battery_use(headers, inverter_id=None):
    if inverter_id is None:
        inverter_id = get_inverter_id(headers)
    # Set full battery charge power
    success = set_inverter_setting(headers, 72, 3000, inverter_id)
    if success:
        # Set full battery discharge power
        sleep(5)
        success = set_inverter_setting(headers, 73, 3000, inverter_id)
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


def do_get_status():
    output = {}
    j = read_json()
    headers = get_headers(j["givenergy_key"])
    inverter_id = get_inverter_id(headers)
    output["inverter_id"] = inverter_id
    output["ac_charge_limit"] = get_AC_charge_limit(headers, inverter_id)
    output["eco_mode"] = is_in_eco_mode(headers, inverter_id)
    output["inverter_status"] = get_inverter_status(headers)
    output["system_data"] = get_latest_system_data(headers)
    return output


def do_get_ac_settings():
    output = {}
    j = read_json()
    headers = get_headers(j["givenergy_key"])
    inverter_id = get_inverter_id(headers)
    output["inverter_id"] = inverter_id
    output["ac_charge_limit"] = get_AC_charge_limit(headers, inverter_id)
    output["ac_charge_enabled"] = get_inverter_setting(headers, 66, inverter_id)
    output["ac_charge_start_time"] = get_inverter_setting(headers, 64, inverter_id)
    output["ac_charge_end_time"] = get_inverter_setting(headers, 65, inverter_id)
    return output


def do_set_ac_settings(args):
    output = {}
    j = read_json()
    headers = get_headers(j["givenergy_key"])
    inverter_id = get_inverter_id(headers)
    output["inverter_id"] = inverter_id
    if args.set_ac_charge_enabled:
        success = set_inverter_setting(headers, 66, args.set_ac_charge_enabled, inverter_id)
        if success:
            output["ac_charge_enabled"] = args.set_ac_charge_enabled
    if args.set_ac_charge_limit:
        success = set_AC_charge_limit(headers, args.set_ac_charge_limit, inverter_id)
        if success:
            output["ac_charge_limit"] = args.set_ac_charge_limit
    if args.set_ac_charge_start_time:
        success = set_inverter_setting(headers, 64, args.set_ac_charge_start_time, inverter_id)
        if success:
            output["ac_charge_start_time"] = args.set_ac_charge_start_time
    if args.set_ac_charge_end_time:
        success = set_inverter_setting(headers, 65, args.set_ac_charge_end_time, inverter_id)
        if success:
            output["ac_charge_end_time"] = args.set_ac_charge_end_time
    return output


if __name__ == "__main__":
    # defaults
    get_status = False
    get_ac_settings = False
    set_ac_charge_enabled = None
    set_ac_charge_limit = None
    set_ac_charge_start_time = None
    set_ac_charge_end_time = None
    output = {}

    # get from web requests
    fs = cgi.FieldStorage()
    if fs.getvalue("get_status") is not None and fs.getvalue("get_status").lower() == "true":
        get_status = True
    if fs.getvalue("get_ac_settings") is not None and fs.getvalue("get_ac_settings").lower() == "true":
        get_ac_settings = True
    if fs.getvalue("set_ac_charge_enabled") is not None:
        set_ac_charge_enabled = fs.getvalue("set_ac_charge_enabled")
    if fs.getvalue("set_ac_charge_limit") is not None:
        set_ac_charge_limit = int(fs.getvalue("set_ac_charge_limit"))
    if fs.getvalue("set_ac_charge_start_time") is not None:
        set_ac_charge_start_time = fs.getvalue("set_ac_charge_start_time")
    if fs.getvalue("set_ac_charge_end_time") is not None:
        set_ac_charge_end_time = fs.getvalue("set_ac_charge_end_time")

    # command line arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--get_status", action="store_true", default=get_status)
    parser.add_argument("--get_ac_settings", action="store_true", default=get_ac_settings)
    parser.add_argument("--set_ac_charge_enabled", action="store", default=set_ac_charge_enabled)
    parser.add_argument("--set_ac_charge_limit", action="store", type=int, default=set_ac_charge_limit)
    parser.add_argument("--set_ac_charge_start_time", action="store", default=set_ac_charge_start_time)
    parser.add_argument("--set_ac_charge_end_time", action="store", default=set_ac_charge_end_time)

    args, unknown = parser.parse_known_args()
    if args.get_status:
        output = do_get_status()
    elif args.get_ac_settings:
        output = do_get_ac_settings()
    elif args.set_ac_charge_enabled or args.set_ac_charge_limit or args.set_ac_charge_start_time or args.set_ac_charge_end_time:
        output = do_set_ac_settings(args)
    print("Content-Type: application/json")
    print()
    print(json.dumps(output))
