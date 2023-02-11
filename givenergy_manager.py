#!/usr/bin/python3

from time import sleep
from datetime import datetime
from givenergy_functions import restart_inverter, get_grid_voltage, get_inverter_status, set_AC_charge_limit, get_battery_level
from solcast_functions import get_tomorrows_forecast_total
from tapo_functions import getTapoPlug, tapoPlugIsOn, switchTapoPlug
from general_functions import get_headers, send_email
from user_input import *


def check_for_errors(headers):
        """
        Check if inverter is in error state.
        If in an error state for more than 15 mins and
        grid voltage is not abnormally high, then
        reboot the inverter.
        """
        subject = "GivEnergy error checking"
        inverter_status = get_inverter_status(headers)
        if inverter_status in ["UNKNOWN", "LOST"]:
                sleep(60)
                inverter_status = get_inverter_status(headers)
                if inverter_status in ["UNKNOWN", "LOST"]:
                        body = "Error: GivEnergy inverter status is " + inverter_status
                        send_email(subject, body)
                        return

        if inverter_status == "ERROR":
                grid_voltage = get_grid_voltage(headers)
                if type(grid_voltage) == float and grid_voltage > 252:
                        body = "Error: GivEnergy inverter status is ERROR, but grid voltage is at "+str(grid_voltage)+" volts, so no action taken."
                        send_email(subject, body)
                        return
                sleep(900)
                inverter_status = get_inverter_status(headers)
                if inverter_status == "ERROR":
                        grid_voltage = get_grid_voltage(headers)
                        if type(grid_voltage) == float and grid_voltage > 252:
                                body = "Error: GivEnergy inverter status is ERROR, but grid voltage is at "+str(grid_voltage)+" volts, so no action taken."
                                send_email(subject, body)
                                return
                        body = "Error: GivEnergy inverter status has been ERROR for 15 mins, so rebooting the inverter..."
                        body += restart_inverter(headers)
                        send_email(subject, body)
                        return


def set_max_charge(headers):
        tomorrows_estimate = get_tomorrows_forecast_total(solcast_key, solcast_site)
        maxmin_tomorrows_estimate = max(min(very_sunny_day, tomorrows_estimate), not_sunny_day)  # ensure estimate is between eg 10 and 20 kWh
        ranged_tomorrows_estimate = maxmin_tomorrows_estimate - not_sunny_day  # ensure between 0 and eg 10
        percentage_difference_per_kwh = (not_sunny_day_charge - very_sunny_day_charge) / (very_sunny_day - not_sunny_day)  # eg (100-70)/(20-10) = 3
        reqd_ac_charge = int(not_sunny_day_charge - ranged_tomorrows_estimate * percentage_difference_per_kwh)  # reqd charge between eg 70% and 100%
        set_AC_charge_limit(headers, reqd_ac_charge)
        subject = "GivEnergy maximum charge set"
        body = "Tomorrow's solar estimate is "+str(tomorrows_estimate)+"kWh, so have set AC charging to "+str(reqd_ac_charge)+"%."
        send_email(subject, body)


def tapo_charge_if_battery_full(headers):
    action_message = ""
    today = datetime.strftime(datetime.now(), "%Y%m%d")
    reqd_battery_level = 100
    for time_and_level in battery_full_levels:
        start_time = datetime.strptime(today+time_and_level[0], "%Y%m%d%H:%M")
        if datetime.now() > start_time:
             reqd_battery_level = time_and_level[1]
    battery_level = get_battery_level(headers)
    body = "GivEnergy battery at "+str(battery_level)+"%\n"
    body += "Required battery is "+str(reqd_battery_level)+"%\n"
    if battery_level > reqd_battery_level + 5:  # hysteresis
        p100 = getTapoPlug()
        if not tapoPlugIsOn(p100):
            action_message = "So turning on tapo plug"
            switchTapoPlug(p100, True)
    elif battery_level < reqd_battery_level:
        p100 = getTapoPlug()
        if tapoPlugIsOn(p100):
            action_message = "So turning off tapo"
            switchTapoPlug(p100, False)
    if action_message != "":
        send_email("Switching tapo plug", body + action_message)


if __name__ == "__main__":
        headers = get_headers(givenergy_key)
        if datetime.now().minute in times_to_check_errors:
                check_for_errors(headers)
        if datetime.strftime(datetime.now(), "%H:%M") == str(time_to_set_max_charge):
                set_max_charge(headers)
        if tapo_enable_if_battery_full:
                tapo_charge_if_battery_full(headers)
