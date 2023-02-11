# givenergy-manager

This repo has some utilities for GivEnergy batteries/inverters. It has 3 main functions:
* Checking the inverter for errors, if the inverter is in an error state for 15 mins, it is rebooted.
* Getting the solar forecast from solcast, and setting the AC charge level appropriately (eg if tomorrow will be sunny, there's no need to charge to 100% tonight)
* Turning on a Tapo smart plug if the battery is full enough, to eg charge an electric car, run a heater etc

### Instructions
1) Clone this repo
2) Copy example_user_input.py to user_input.py (see below for more info)
3) Run a cron job every minute for givenergy_manager.py

### user_input.py
* givenergy_key - this is the API key you get from https://givenergy.cloud/account-settings/security
* solcast_key - this is the API key you get from https://toolkit.solcast.com.au/account
* solcast_site - this is the Resource Id your address is given by solcast
* email_address - this is a gmail address you can use to email yourself notifications when the manager does something
* email_password - you need a gmail app password here, not your google password, see https://myaccount.google.com/apppasswords
* very_sunny_day - how many kWh (or above) for tomorrows forecast for you to consider it very sunny
* very_sunny_day_charge - how high a percentage you want your battery to charge to if tomorrow is very sunny
* not_sunny_day - anything below this (in kWh) is considered not sunny
* not_sunny_day_charge - charge to this percentage for any not sunny day, usually 100 (percent)
* time_to_set_max_charge - the time you want to set the charge percentage for tomorrow. Needs to be before midnight, and before your cheap import rate starts. Format is eg "21:00"
* times_to_check_errors - a list of times per hour to check the inverter for errors. Recommend [0,30] to check every half hour, or [] to disable error checking.
* tapo_enable_if_battery_full - set True or False to enable/disable the Tapo switching. True requires the Tapo library from https://github.com/fishbigger/TapoP100 to be installed
* battery_full_levels - a list of pairs of times and battery percentages for controlling a Tapo smart plug. eg
```
battery_full_levels = [
    ["01:30", 10],
    ["05:30", 50],
    ["09:00", 85],
    ["18:00", 100],
]
```
This might correspond to 4 hours of cheap electricity from 01:30 to 05:30, so keep the battery level above 10% for that time (probably while charging the battery)
Between 9am and 6pm keep the battery level high, but if it gets above 85%, turn on the Tapo plug to avoid exporting if possible. (There is a 5% buffer, so will actually only turn on at 90%)
* tapo_ip - local IP address of the Tapo plug
* tapo_username - your Tapo username
* tapo_password - your Tapo password
