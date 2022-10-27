import sys
from datetime import datetime

import requests
import pytz
import pandas as pd

locations = [
    {"name":"central_park",
     "lat_lon":{"latitude":40.7823,
                 "longitude":-87.7421}}
]

base_url = "https://api.weather.gov/points/{latitude},{longitude}"

def format_url(base_url, latitude, longitude):
    """Convert the base url into an fstring, inputing latitude and longitude
    Parameters:
    base_url (str) A url to be converted with spots for latitude and longitude
        ex: "https://api.weather.gov/points/{latitude},{longitude}"
    latitude (str or int) : a string or int that presumably is latitude
    longitude (str or int) : string or integar that presumably is longitude

    Return:  
    url (str) : String with latitude and longitude imputed 
        ex:"https://api.weather.gov/points/42.11,-87.1" """

    url = base_url.format(latitude=latitude, longitude=longitude)
    return f"{url}"


def get_url(url):
    """Query a url return response or error"""
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"There has been an error: {err}")
        return err
    return response

def wrapper(location_json):
    """Get the forecast for a given api from weather.gov
    Parameters:
        location_json (dict) : A json with latitude and longitude
            {"latitude":40.7823, "longitude":-87.7421}
    
    Returns:
        r (dict): An API response with the hourly forecast for a given latitude and longitude"""
    url = format_url(base_url, **location_json)
    
    r = get_url(url)
    
    forecast_url = r.json()["properties"]["forecastHourly"]
    
    r = get_url(forecast_url)
    
    return r
    
def weather_dataframe(raw_weather):
    """Convert a json of weather forecasts into pandas dataframe
    
    Parameters:
        raw_weather (requests response) : raw requests response
        from weather.gov api for weather forecast

    Returns:
        df (dataframe) : DataFrame created from raw_weather, with 
        number, name, icon columns removed. 'observed_time' added
        where it is the time that the dataframe was created.
        all times converted to UTC."""

    utc = pytz.timezone('UTC')
    
    now = datetime.now().astimezone(utc)
    
    df = pd.DataFrame.from_dict(raw_weather.json()['properties']['periods'])
    
    df['startTime'] = pd.to_datetime(df['startTime'], utc=True)
    
    df['endTime'] = pd.to_datetime(df['endTime'], utc=True)
    
    df['observed_time'] = now
    
    df.drop(["number", "name", "icon"], axis=1, inplace=True)
    
    return df

def weather_forecasts(location_json):
    """Wrapper function to download requests respons for a given location
    Parameters:
        location_json (dict) : a dictionary that looks like this:
            {"name":"central_park", "lat_lon":{"latitude":40.7823,
             "longitude":-87.7421}}
    
    Returns:
        df (DataFrame) : dataframe returned from weather_dataframe()"""
    raw_forecasts = wrapper(location_json['lat_lon'])
    
    df = weather_dataframe(raw_forecasts)
    
    return df
