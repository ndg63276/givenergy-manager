# givenergy-manager

This repo has some utilities for GivEnergy batteries/inverters. It has 3 main functions:
* Checking the inverter for errors, if the inverter is in an error state for 15 mins, it is rebooted.
* Getting the solar forecast from Solcast, and setting the AC charge level appropriately (eg if tomorrow will be sunny, there's no need to charge to 100% tonight) - this is designed for tariffs like Octopus Go with cheap night time electricity.
* Turning on a Tapo or Smartlife smart plug, or forcing export from your GivEnergy battery, if the battery is full enough, to eg charge an electric car, run a heater, or take advantage of the Octopus Flux tariff.

### Instructions
1) Clone this repo
2) Copy example_user_input.json to user_input.json (see below for more info)
3) Run a cron job every minute or so for givenergy_manager.py, eg
```shell
*/5 * * * * /home/pi/givenergy-manager/cgi-bin/givenergy_manager.py --checkdevices --email >> /var/log/cron.log 2>&1
```

### Docker
Alternatively, you can build and run from a Docker image. It is on [Dockerhub](https://hub.docker.com/r/markwilliams4/givenergymanager), or you can build your own. You will require [docker](https://docs.docker.com/get-docker/ "docker") and docker-compose setup and working first.

1. Clone this repository
```shell
git clone https://github.com/ndg63276/givenergy-manager.git
```
2. Enter the project folder
```shell
cd givenergy-manager
```
3. Build a local docker image
```shell
docker build -t ndg63276/givenergymanager .
```
4. Run Your locally built docker image with docker compose
```shell
docker compose up -d
```
5. The cron job will run every 5 minutes on the Docker image.
6. Navigate to http://localhost:8001 in your browser to use the web editor for user_input.json

### user_input.json
I recommend using the Docker image above, or running the webserver by using
```shell
python serve.py 8001
```
and then going to http://localhost:8001 in a browser, to use the web editor.
But if you are manually editing the user_input.json file, here are the keys. 
* givenergy_key - this is the API key you get from https://givenergy.cloud/account-settings/security
* email_address - this is a gmail address you can use to email yourself notifications when the manager does something
* email_password - you need a gmail app password here, not your google password, see https://myaccount.google.com/apppasswords
* set_max_charge_enabled - Enable or disable the feature to set the overnight charging percentage based on a Solcast forecast
* time_to_set_max_charge - the time you want to set the charge percentage for tomorrow. Needs to be before midnight, and before your cheap import rate starts. Format is eg "21:00"
* solcast_key - this is the API key you get from https://toolkit.solcast.com.au/account
* solcast_site - this is the Resource Id your address is given by Solcast, get it from https://toolkit.solcast.com.au/rooftop-sites
* very_sunny_day - how many kWh (or above) for tomorrows forecast for you to consider it very sunny
* very_sunny_day_charge - how high a percentage you want your battery to charge to if tomorrow is very sunny
* not_sunny_day - anything below this (in kWh) is considered not sunny
* not_sunny_day_charge - charge to this percentage for any not sunny day, usually 100 (percent)
* error_checking_enabled - Enable or disable the feature to check the inverter for errors and reboot if necessary
* times_to_check_errors - a list of times per hour to check the inverter for errors. Recommend [0,30] to check every half hour, or [] to disable error checking.
* devices - a list of dictionaries, of the devices you want the GivEnergy Manager to turn on/off based on battery level. Each device needs these keys:
  * name - a friendly name to use in GivEnergy Manager
  * control_enabled - set True/False if you want GivEnergy manager to control the device or not
  * type - either "tapo", "smartlife", or "givenergy-export"
  * username - your login to the Tapo or Smartlife apps
  * password - your password to the Tapo or Smartlife apps
  * ip - Tapo only - the (local) IP address of the Tapo device you wanr to control, you can find this in the Tapo app
  * region - Smartlife only - your region, EU, US or CN
  * device_name - Smartlife only - the name the device has in the Smartlife app
  * battery_full_levels - a list of pairs of times and battery percentages for controlling a Tapo or Smartlife smart plug. eg
```
"battery_full_levels": [
    ["01:30", 10],
    ["05:30", 50],
    ["09:00", 85],
    ["18:00", 100],
]
```
This might correspond to 4 hours of cheap electricity from 01:30 to 05:30, so keep the battery level above 10% for that time (probably while charging the battery)
Between 9am and 6pm keep the battery level high, but if it gets above 85%, turn on the smart plug to avoid exporting if possible. (There is a 5% buffer, so will actually only turn on at 90%)

### GivEnergy Smart plugs
GivEnergy smart plugs are just rebadged Smartlife plugs, so if you want to switch them based on your battery level, you can! But you will lose the ability to control them from the GivEnergy app. Simply download the Smartlife app if you haven't already, then:
* Press the + button in the Smartlife app and select Add Device
* Choose "Socket (Wi-Fi)" from the list
* Put in your wifi details
* Follow the instructions in the app


### Alexa Skill
GivEnergy has it's own official Alexa skill, but if you want to deploy your own, you can do using the included interaction model. Upload that to the JSON editor in the Amazon developer console. Then upload all the files in cgi-bin/ to AWS Lambda, and the skill will use the lambda_function.py file.
