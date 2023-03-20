import requests
from datetime import datetime, timedelta
from general_functions import get_headers


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
