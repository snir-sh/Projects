
import os
import requests

def get_address_from_coordinates_with_google_api_key(lat, lon, api_key=None):
    # Get API key from parameter or environment variable
    # To set it locally: export GOOGLE_MAPS_API_KEY="your-api-key-here"
    # To create a Google Maps API key, visit: https://console.cloud.google.com/
    if not api_key:
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        raise RuntimeError("GOOGLE_MAPS_API_KEY environment variable not set. Create a key at https://console.cloud.google.com/")
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK' and data['results']:
        return data['results'][0]['formatted_address']
    else:
        return "Address not found"

# Example usage (requires GOOGLE_MAPS_API_KEY env var to be set)
# print(get_address_from_coordinates_with_google_api_key(32.7749, 35.7749))