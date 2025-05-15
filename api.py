import time
import base64
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from config import client_id, client_secret, api_key


# Function to get access token
def get_access_token():
    TOKEN_URL = "https://ext-api.vasttrafik.se/token" # URL for token endpoint
    auth_value = f"{client_id}:{client_secret}" # Basic auth value
    encoded_credentials = base64.b64encode(auth_value.encode()).decode('utf-8') # Encode credentials in base64

    # Set headers for the request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_credentials}'
    }
    # Set data for the request
    data = { 'grant_type': 'client_credentials' }
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data) # Send POST request to token endpoint
        response.raise_for_status()  # If statuscode is not 200, raise an exception
        token_info = response.json() # Parse the JSON response
        access_token = token_info.get("access_token") # Get access token from the response
        if access_token:
            os.environ["VASTTRAFIK_access_TOKEN"] = access_token # Store access token in environment variable
            print("Access token hämtades framgångsrikt.")
            return access_token
        else:
            print("Access token hittades inte i svaret.")
            return None
    except requests.exceptions.RequestException as err:
        print(f"Fel vid hämtning av access token: {err}")
        return None

# Function to get stop area GID for a given location name
def get_stop_area_gid(location_name, access_token):
    LOCATION_URL = 'https://ext-api.vasttrafik.se/pr/v4/locations/by-text'
    # Set headers for the request and the parameters
    headers = { 'Authorization': f'Bearer {access_token}',  }
    params = {'q': location_name, 'limit': 1 }

    try:
        response = requests.get(LOCATION_URL, headers=headers, params=params)
        response.raise_for_status()  # If statuscode is not 200, raise an exception
        data = response.json()
        return data['results'][0]['gid'] if data['results'] else None
    except requests.exceptions.RequestException as err:
        print(f"Fel vid hämtning av stop-område GID: {err}")
        return None

# Function to fetch departures for a given stop area
def fetch_departures(stop_area_gid, access_token):
    DEPARTING_URL = f'https://ext-api.vasttrafik.se/pr/v4/stop-areas/{stop_area_gid}/departures'
   
    headers = {'Authorization': f'Bearer {access_token}' }
    params = { 'limit': 1, 'platforms': 'A' }

    try:
        response = requests.get(DEPARTING_URL, headers=headers, params=params)
        response.raise_for_status()  # If statuscode is not 200, raise an exception
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as err:
        print(f"Fel vid hämtning av avgångar: {err}")
        return None



def until_departure(time : datetime) -> str:

    # Get the current time in the same timezone
    time = datetime.fromisoformat(time)
    now = datetime.now(ZoneInfo("Europe/Stockholm"))
   
    # Calculate the difference
    difference = time - now
    if difference.total_seconds() < 0:
        return "To late"
    else:
        total_seconds = int(difference.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        # Format as MM:SS
        formatted = f"{minutes:02}:{seconds:02}"
        # Return the difference in seconds
        return formatted

# Function to print departure information
def print_departure_info(departure):
    if departure:
        planned_time = departure["plannedTime"]
        estimated_time = departure["estimatedTime"]
        estimated_time = estimated_time if estimated_time else planned_time
        print(until_departure(planned_time), "minuter kvar till avgång")
        print(until_departure(estimated_time), "minuter kvar till avgång (estimerad)")

        # print("Avgångsinformation:")
        # print("Planerad avgång",planned_time)
        # print("Estimerad avgång", estimated_time)

    else:
        print("Ingen avgångsinformation tillgänglig.")


def main():
    # Get access
    while True: 
        access_token = os.getenv("VASTTRAFIK_access_TOKEN")
        if not access_token:
            print("Ingen access token hittades i miljövariabler. Hämtar ny access token...")
            access_token = get_access_token()

        if access_token:
            # Get gid for Spaldingsgatan
            stop_area_gid = get_stop_area_gid("Spaldingsgatan", access_token)
            if stop_area_gid:
                print(f"Stop-område GID för Spaldingsgatan: {stop_area_gid}")
                # Hämta avgångar för Spaldingsgatan
                departures_data = fetch_departures(stop_area_gid, access_token)
                if departures_data and 'results' in departures_data:
                    departure = departures_data['results'][0]
                    print_departure_info(departure)

                else:
                    print("Ingen avgångsinformation tillgänglig.")
            else:
                print("Kunde inte hämta stop-område GID för Spaldingsgatan.")
        else:
            print("Access token kunde inte hämtas.")
        time.sleep(1)

if __name__ == "__main__":
    main()
