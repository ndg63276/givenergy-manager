import requests
from datetime import datetime, timedelta
from givenergy_functions import get_battery_level, get_grid_voltage, get_solar_power, get_consumption
from general_functions import get_headers


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


def do_nothing():
    return build_response({})


def get_battery_level_response(headers):
    battery_level = get_battery_level(headers)
    if type(battery_level) in (int, float):
        output = "Your battery is "+str(battery_level)+"% full."
    else:
        output = battery_level
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


def get_grid_voltage_response(headers):
    grid_voltage = get_grid_voltage(headers)
    if type(grid_voltage) in (int, float):
        output = "The grid is at "+str(grid_voltage)+" volts."
    else:
        output = grid_voltage
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


def get_solar_power_response(headers):
    solar_power = get_solar_power(headers)
    if type(solar_power) in (int, float):
        output = "You are currently generating "+str(solar_power)+" watts."
    else:
        output = solar_power
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


def get_consumption_response(headers):
    consumption = get_consumption(headers)
    if type(consumption) in (int, float):
        output = "You are currently using "+str(consumption)+" watts."
    else:
        output = consumption
    should_end_session = True
    return build_response(build_short_speechlet_response(output, should_end_session))


def on_intent(event, headers):
    intent_name = event["request"]["intent"]["name"]
    # Dispatch to your skill"s intent handlers
    if intent_name == "BatteryIntent":
        return get_battery_level_response(headers)
    elif intent_name == "GridVoltageIntent":
        return get_grid_voltage_response(headers)
    elif intent_name == "SolarGenerationIntent":
        return get_solar_power_response(headers)
    elif intent_name == "ConsumptionIntent":
        return get_consumption_response(headers)
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

