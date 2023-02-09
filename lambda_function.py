import requests
from datetime import datetime, timedelta


def get_headers(apikey):
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return headers


def lambda_handler(event, context):
    if "accessToken" not in event["context"]["System"]["user"]:
        return account_not_linked()
    apikey = event["context"]["System"]["user"]["accessToken"]
    headers = get_headers(apikey)
    if event["request"]["type"] == "LaunchRequest":
        return get_help()
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event, headers)


def account_not_linked():
    output = "Hello. To use this skill, you must provide your GivEnergy API key. You can do this from the Alexa app or Amazon website."
    should_end_session = True
    return build_response(build_account_linking_response(output, should_end_session))


def get_help():
    output = "Hello. For example say, 'How full is my battery?'"
    should_end_session = False
    return build_response(build_short_speechlet_response(output, should_end_session))


def get_battery_level_response(headers):
    battery_level = get_battery_level(headers)
    if type(battery_level) in (int, float):
        output = "Your battery is "+str(battery_level)+"% full."
    else:
        output = battery_level
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


def get_battery_level(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        return system_data["error"]
    else:
        return system_data["data"]["battery"]["percent"]


def get_grid_voltage_response(headers):
    grid_voltage = get_grid_voltage(headers)
    if type(grid_voltage) in (int, float):
        output = "The grid is at "+str(grid_voltage)+" volts."
    else:
        output = grid_voltage
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


def get_grid_voltage(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        return system_data["error"]
    else:
        return system_data["data"]["grid"]["voltage"]


def get_solar_power(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        output = system_data["error"]
    else:
        solar_power = system_data["data"]["solar"]["power"]
        output = "You are currently generating "+str(solar_power)+" watts."
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


def get_consumption(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        output = system_data["error"]
    else:
        consumption = system_data["data"]["consumption"]
        output = "You are currently using "+str(consumption)+" watts."
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


def get_communication_devices(headers):
    url = "https://api.givenergy.cloud/v1/communication-device"
    params = {"page": "1"}
    r = requests.get(url, headers=headers, params=params)
    return r.json()


def get_status(headers):
    system_data = get_latest_system_data(headers)
    if "error" in system_data:
        output = system_data["error"]
    else:
        consumption = system_data["data"]["consumption"]
        output = "You are currently using "+str(consumption)+" watts."
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


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
    if 'data' in r.json() and 'success' in r.json()['data']:
        return r.json()['data']['success']


def get_solcast_forecast(solcast_key, solcast_site):
    solcast_headers = get_headers(solcast_key)
    url = 'https://api.solcast.com.au/rooftop_sites/'+solcast_site+'/forecasts?format=json'
    r = requests.get(url, headers=solcast_headers)
    if 'forecasts' in r.json():
        return r.json()['forecasts']
    return []


def get_tomorrows_forecast_total(solcast_key, solcast_site):
    forecast = get_solcast_forecast(solcast_key, solcast_site)
    total = 0
    tomorrow = datetime.now()+timedelta(days=1)
    for i in forecast:
        end = datetime.strptime(i['period_end'], '%Y-%m-%dT%H:%M:%S.%f0Z')
        if end.date() == tomorrow.date():
            total += i['pv_estimate'] / 2
    return total


def on_intent(event, headers):
    intent_name = event["request"]["intent"]["name"]
    # Dispatch to your skill"s intent handlers
    if intent_name == "BatteryIntent":
        return get_battery_level_response(headers)
    elif intent_name == "GridVoltageIntent":
        return get_grid_voltage_response(headers)
    elif intent_name == "SolarGenerationIntent":
        return get_solar_power(headers)
    elif intent_name == "ConsumptionIntent":
        return get_consumption(headers)
    elif intent_name == "StatusIntent":
        return get_status(headers)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help()
    elif intent_name == "AMAZON.CancelIntent":
        return do_nothing()
    elif intent_name == "AMAZON.StopIntent":
        return do_nothing()
    else:
        raise ValueError("Invalid intent")


def build_short_speechlet_response(output, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "shouldEndSession": should_end_session
    }


def build_account_linking_response(output, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "LinkAccount"
        },
        "shouldEndSession": should_end_session
    }


def build_response(speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": {},
        "response": speechlet_response
    }

