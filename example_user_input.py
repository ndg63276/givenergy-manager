givenergy_key = "" # GivEnergy API key

solcast_key = "" # Solcast API key
solcast_site = "" # Solcast Site ID

email_address = ""  # gmail addresses only, if you want to be notified
email_password = ""  # use a Google app password, not Google password itself

very_sunny_day = 20  # anything above this (in kWh) is considered very sunny
very_sunny_day_charge = 70  # charge to this percentage for any very sunny day

not_sunny_day = 10  # anything below this (in kWh) is considered not sunny
not_sunny_day_charge = 100  # charge to this percentage for any not sunny day

time_to_set_max_charge = "20:00"  # 24hr clock representation of the time to set the max charge
times_to_check_errors = [0,30]  # minutes past the hour to check for errors

# Clock times must be in order
# eg ["09:00", 90] means turn on something if after 9am until battery < 90% full
# set 100 to not turn on

devices = [
        {
                "name": "Car charger",
                "control_enabled": False,
                "type": "tapo",
                "username": "example@mail.com",
                "password": "password123",
                "ip": "192.168.1.100", # must be local IP for Tapo devices
                "battery_full_levels": [
                        ["00:00", 100],
                        ["12:00", 50],
                        ["12:30", 100],
                ]
        },
        {
                "name": "Heater",
                "control_enabled": False,
                "type": "smartlife",
                "username": "example@mail.com",
                "password": "p4ssw0rd",
                "region": "EU", # EU, US or CN
                "device_name": "Heater smart plug", # name from Smartlife app
                "battery_full_levels": [
                        ["00:00", 100],
                        ["12:00", 50],
                        ["12:30", 100],
                ]
        }
]
