
import requests

def get_address_from_coordinates_with_google_api_key(lat, lon, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK' and data['results']:
        return data['results'][0]['formatted_address']
    else:
        return "Address not found"

print(get_address_from_coordinates_with_google_api_key(32.7749, 35.7749, "AIzaSyAbT-s8lQIuChYhNcdZ6sdNrO37a5I2rtE"))