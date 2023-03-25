#!/usr/bin/env python3

import argparse
import cgi
from time import sleep
from datetime import datetime
from givenergy_functions import restart_inverter, get_grid_voltage, get_inverter_status, set_AC_charge_limit, get_AC_charge_limit, get_battery_level
from solcast_functions import get_tomorrows_forecast_total
from general_functions import read_json, get_headers, send_email


def check_for_errors(headers):
	"""
	Check if inverter is in error state.
	If in an error state for more than 15 mins and
	grid voltage is not abnormally high, then
	reboot the inverter.
	"""
	inverter_status = get_inverter_status(headers)
	if inverter_status in ["UNKNOWN", "LOST"]:
		sleep(60)
		inverter_status = get_inverter_status(headers)
		if inverter_status in ["UNKNOWN", "LOST"]:
			return "Error: GivEnergy inverter status is " + inverter_status + "\n."

	if inverter_status == "ERROR":
		grid_voltage = get_grid_voltage(headers)
		if type(grid_voltage) == float and grid_voltage > 252:
			return "Error: GivEnergy inverter status is ERROR, but grid voltage is at "+str(grid_voltage)+" volts, so no action taken.\n"
		sleep(900)
		inverter_status = get_inverter_status(headers)
		if inverter_status == "ERROR":
			grid_voltage = get_grid_voltage(headers)
			if type(grid_voltage) == float and grid_voltage > 252:
				return "Error: GivEnergy inverter status is ERROR, but grid voltage is at "+str(grid_voltage)+" volts, so no action taken.\n"
			body = "Error: GivEnergy inverter status has been ERROR for 15 mins, so rebooting the inverter...\n"
			body += restart_inverter(headers)
			return body
	return ""


def calculate_max_charge(headers, j):
	tomorrows_estimate = round(get_tomorrows_forecast_total(j["solcast_key"], j["solcast_site"]), 2)
	maxmin_tomorrows_estimate = max(min(j["very_sunny_day"], tomorrows_estimate), j["not_sunny_day"])  # ensure estimate is between eg 10 and 20 kWh
	ranged_tomorrows_estimate = maxmin_tomorrows_estimate - j["not_sunny_day"]  # ensure between 0 and eg 10
	percentage_difference_per_kwh = (j["not_sunny_day_charge"] - j["very_sunny_day_charge"]) / (j["very_sunny_day"] - j["not_sunny_day"])  # eg (100-70)/(20-10) = 3
	reqd_ac_charge = int(j["not_sunny_day_charge"] - ranged_tomorrows_estimate * percentage_difference_per_kwh)  # reqd charge between eg 70% and 100%
	output = "Tomorrow's solar estimate is "+str(tomorrows_estimate)+"kWh, so have set AC charging to "+str(reqd_ac_charge)+"%.\n"
	output = set_max_charge(headers, reqd_ac_charge, output)
	return output


def force_max_charge(headers, reqd_ac_charge):
	output = "Setting AC charging to "+str(reqd_ac_charge)+"%.\n"
	output = set_max_charge(headers, reqd_ac_charge, output)
	return output


def set_max_charge(headers, reqd_ac_charge, output=""):
	attempts = 5
	for i in range(attempts):
		set_AC_charge_limit(headers, reqd_ac_charge)
		sleep(1)
		if get_AC_charge_limit(headers) == reqd_ac_charge:
			break
		sleep(5)
		if i < attempts-1:
			output += "Failed to set max charge, retrying...\n"
		else:
			output += "Failed to set max charge.\n"
	return output


def is_battery_full_enough(battery_level, device_levels):
	today = datetime.strftime(datetime.now(), "%Y%m%d")
	reqd_battery_level = 100
	for time_and_level in device_levels:
		start_time = datetime.strptime(today+time_and_level[0], "%Y%m%d%H:%M")
		if datetime.now() > start_time:
			 reqd_battery_level = time_and_level[1]
	body = "GivEnergy battery at "+str(battery_level)+"%, "
	body += "required battery is "+str(reqd_battery_level)+"%\n"
	if battery_level >= reqd_battery_level + 5:  # hysteresis
		return True, body
	elif battery_level < reqd_battery_level:
		return False, body
	return None, body


def switch_tapo(device, value):
	from tapo_functions import switch_tapo_device
	action_message = ""
	device_switched = switch_tapo_device(device, value)
	if device_switched and value == True:
		action_message = "So turning on " + device["name"] + ".\n"
	elif device_switched and value == False:
		action_message = "So turning off " + device["name"] + ".\n"
	return action_message


def switch_smartlife(device, value):
	from smartlife_functions import switch_smartlife_device
	action_message = ""
	device_switched = switch_smartlife_device(device, value)
	if device_switched and value == True:
		action_message = "So turning on " + device["name"] + ".\n"
	elif device_switched and value == False:
		action_message = "So turning off " + device["name"] + ".\n"
	return action_message


def switch_givenergyexport(device, value):
	from givenergy_functions import switch_DC_discharging
	action_message = ""
	j = read_json()
	headers = get_headers(j["givenergy_key"])
	device_switched = switch_DC_discharging(headers, value)
	if device_switched and value == True:
		action_message = "So turning on " + device["name"] + ".\n"
	elif device_switched and value == False:
		action_message = "So turning off " + device["name"] + ".\n"
	return action_message


def switch_device(device, value, msg):
	msg2 = ""
	if "type" in device and device["type"] == "tapo":
		msg2 = switch_tapo(device, value)
	elif "type" in device and device["type"] == "smartlife":
		msg2 = switch_smartlife(device, value)
	elif "type" in device and device["type"] == "givenergy-export":
		msg2 = switch_givenergyexport(device, value)
	if msg2 != "":
		msg2 = msg + msg2
	return msg2


def main(args):
	subject = "GivEnergy Manager"
	body = ""
	j = read_json()
	headers = get_headers(j["givenergy_key"])
	if args.testemail:
		body = "This is a test of the email system."
	if args.forcemaxcharge > 0:
		body += force_max_charge(headers, args.forcemaxcharge)
	if args.checkdevices:
		battery_level = get_battery_level(headers)
		for device in j["devices"]:
			if "control_enabled" not in device or device["control_enabled"] == False:
				continue
			battery_full_enough, msg = is_battery_full_enough(battery_level, device["battery_full_levels"])
			if battery_full_enough is not None:
				body += switch_device(device, battery_full_enough, msg)
	if args.calculatemaxcharge or (
			j["set_max_charge_enabled"] is True and
			datetime.strftime(datetime.now(), "%H:%M") == j["time_to_set_max_charge"]):
		body += calculate_max_charge(headers, j)
	if args.forceerrorcheck or (
			j["error_checking_enabled"] is True and
			datetime.now().minute in j["times_to_check_errors"]):
		body += check_for_errors(headers)
	if args.email or args.testemail:
		if body != "":
			send_email(subject, body)
	else:
		print(body)


if __name__ == "__main__":
	# default values
	checkdevices = False
	forever = False
	delay = 60
	forcemaxcharge = -1
	calculatemaxcharge = False
	forceerrorcheck = False
	email = False
	testemail = False

	# get from web requests
	fs = cgi.FieldStorage()
	if fs.getvalue("checkdevices") is not None and fs.getvalue("checkdevices").lower() == "true":
		checkdevices = True
	if fs.getvalue("forcemaxcharge") is not None:
		forcemaxcharge = int(fs.getvalue("forcemaxcharge"))
	if fs.getvalue("calculatemaxcharge") is not None and fs.getvalue("calculatemaxcharge").lower() == "true":
		calculatemaxcharge = True
	if fs.getvalue("forceerrorcheck") is not None and fs.getvalue("forceerrorcheck").lower() == "true":
		forceerrorcheck = True
	if fs.getvalue("email") is not None and fs.getvalue("email").lower() == "true":
		email = True
	if fs.getvalue("testemail") is not None and fs.getvalue("testemail").lower() == "true":
		testemail = True

	# command line arguments
	parser = argparse.ArgumentParser(description="")
	parser.add_argument("--checkdevices", action="store_true", default=checkdevices)
	parser.add_argument("--forever", action="store_true", default=forever)
	parser.add_argument("--delay", action="store", default=delay)
	parser.add_argument("--forcemaxcharge", action="store", type=int, default=forcemaxcharge)
	parser.add_argument("--calculatemaxcharge", action="store_true", default=calculatemaxcharge)
	parser.add_argument("--forceerrorcheck", action="store_true", default=forceerrorcheck)
	parser.add_argument("--email", action="store_true", default=email)
	parser.add_argument("--testemail", action="store_true", default=testemail)
	args, unknown = parser.parse_known_args()
	if args.forever:
		while True:
			main(args)
			sleep(int(args.delay))
	else:
		main(args)
