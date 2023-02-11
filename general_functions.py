def get_headers(apikey):
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return headers
