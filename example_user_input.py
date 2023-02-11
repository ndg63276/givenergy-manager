givenergy_key = ""

solcast_key = ""
solcast_site = ""

email_address = ""  # gmail addresses only
email_password = ""  # use an app password, not google password

very_sunny_day = 20  # anything above this (in kWh) is considered very sunny
very_sunny_day_charge = 70  # charge to this percentage for any very sunny day

not_sunny_day = 10  # anything below this (in kWh) is considered not sunny
not_sunny_day_charge = 100  # charge to this percentage for any not sunny day

time_to_set_max_charge = "20:00"  # 24hr clock representation of the time to set the max charge

times_to_check_errors = [2,32]  # minutes past the hour to check for errors
