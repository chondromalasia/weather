from time import sleep
from datetime import date, timedelta, datetime
import configparser
import requests
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

import sys
sys.path.append("..")

import src.utils as utils

options = webdriver.FirefoxOptions()
options.headless = True

today = str(date.today())
now = str(datetime.now())
tomorrow = str(datetime.now() + timedelta(days=1))

city_to_stid = {
    "NYC":"knyc",
    "CHI":"kmdw"
}

synoptic_base_url = "https://api.synopticdata.com/v2/stations/timeseries?"

days_of_week = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
)


def degree_cleaner(to_clean):
    if "\n" in to_clean:
        to_clean = to_clean.split("\n")[0]
    if to_clean[len(to_clean)-1] == "°":
        return to_clean[:-1]
    else:
        return to_clean

def nws_cleaner(to_clean):
    return to_clean.split(' ')[1]


def TWC_scraper(driver, city, tomorrow, now):
    
    print("TWC" + city)

    if city == 'NYC':
        url = "https://weather.com/weather/tenday/l/10035:4:US"
    elif city == 'CHI':
        url = "https://weather.com/en-MH/weather/tenday/l/47895a57832fa42b0f27ccd62ba1cace382d58779e776bf5a066b1f42d6cc5a1"

    driver.get(url)
    sleep(3)
    
    # if it's already on fahrenheit, this times out
    try:
        WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="WxuHeaderLargeScreen-header-9944ec87-e4d4-4f18-b23e-ce4a3fd8a3ba"]/header/div/div[2]/div[2]/button'))).click()
        WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="UnitSelectorTabs-tab_0"]'))).click()
    except:
        print('should already be fahrenheit')
        pass
        
    k = driver.find_elements(By.XPATH, "/html/body/div[1]/main/div[2]/main/div[1]/section/div[2]/details[2]/summary/div/div/div[1]/span[1]")

    temp = degree_cleaner(k[0].text)

    
    return [city, tomorrow, now, "TWC", temp]


def accuweather_scraper(driver, city, tomorrow, now):

    if city == 'NYC':
        url = "https://www.accuweather.com/en/us/central-park/10028/daily-weather-forecast/2627448?day=2"
    elif city == 'CHI':
        url = 'https://www.accuweather.com/en/us/chicago-midway-international-airport/60638/daily-weather-forecast/10008_poi?day=2'
        
    while True:
    # Accuweather NYC
        try:
            driver.get(url)

            print("Accuweather" + city)
            # rather than check ads, just retry it?
            WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, "//*[name()='svg' and @class='hamburger-button icon-hamburger']"))).click()
            WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, "//*[name()='svg' and @class='icon-settings']"))).click()
            drop = Select(driver.find_element(By.ID, "unit"))
            # I ran into an ad here
            drop.select_by_value("F")

            driver.back()

            temp_text = driver.find_element(By.XPATH, "/html/body/div/div[5]/div[1]/div[1]/div[2]/div[1]/div[1]")
            temp = degree_cleaner(temp_text.text)

            break
        except:
            # if there's an ad, we just do it again
            pass
    return [city, tomorrow, now, "Accuweather", temp]

def NWS_scraper(driver, city, tomorrow, now):
    
    print('NWS' + city)
    
    if city == 'NYC':
        url = "https://forecast.weather.gov/MapClick.php?lat=40.7823&lon=-73.9654"
    elif city == 'CHI':
        url = "https://forecast.weather.gov/MapClick.php?lat=41.7868&lon=-87.7455"
        
    while True:
        try:
            driver.get(url)

            second_pos_head = driver.find_element(By.XPATH, '//*[@id="seven-day-forecast-list"]/li[2]/div/p[1]')
            
            if second_pos_head.text not in days_of_week:
                woop = driver.find_element(By.XPATH, '//*[@id="seven-day-forecast-list"]/li[3]/div/p[4]')
            else:
                woop = driver.find_element(By.XPATH, '//*[@id="seven-day-forecast-list"]/li[2]/div/p[4]')

            temp = nws_cleaner(woop.text)
            
            break
            
        except:
            pass
    
    return [city, tomorrow, now, "NWS", temp]


def foreca_scraper(driver, city, tomorrow, now):
    print('foreca' + city)
    
    while True:
        try:
            if city == 'NYC':
                url = "https://www.foreca.com/106301678/New-York-City-Central-Park-New-York"
            elif city == "CHI":
                url = "https://www.foreca.com/104887472/Chicago-Midway-International-Airport-Chicago-IL"

            driver.get(url)
            WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//*[@id="drawerToggle"]'))).click()

            WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, '//*[@class="title" and text()="F°"]'))).click()
            driver.refresh()

            temp = driver.find_element(By.XPATH, '//*[@id="pageContent"]/div/section[2]/div/div[1]/div[2]/a/p[2]/span[2]')
            temp = degree_cleaner(temp.text)

            return [city, tomorrow, now, "foreca", temp]
        except:
            pass

def to_write_printer(to_write):
    for i in to_write:
        if i[0] == 'NYC':
            print(i)
            
    print('\n')
    for j in to_write:
        if j[0] == 'CHI':
            print(j)


def scrape_websites():
    to_write = []
    driver = webdriver.Firefox(executable_path="/home/heath/bin/geckodriver", options=options)
    driver.implicitly_wait(15)


    # super janky but I don't know any other way tomake it think it's fahrenheit
    TWC_scraper(driver, "CHI", tomorrow, now)
    to_write.append(TWC_scraper(driver, "CHI", tomorrow, now))
    to_write.append(TWC_scraper(driver, "NYC", tomorrow, now))
    to_write.append(accuweather_scraper(driver, "NYC", tomorrow, now))
    to_write.append(accuweather_scraper(driver, "CHI", tomorrow, now))
    to_write.append(NWS_scraper(driver, "NYC", tomorrow, now))
    to_write.append(NWS_scraper(driver, "CHI", tomorrow, now))   
    to_write.append(foreca_scraper(driver, "NYC", tomorrow, now))
    to_write.append(foreca_scraper(driver, "CHI", tomorrow, now))

    driver.close()

    return to_write


### Daily Highs Zone

def format_date(date):
    """YYYY-MM-DD -> YYYYMMDD0001"""
    
    date_now = date.replace("-", "")
    
    return date_now + "0001"


def get_token():
    config = configparser.ConfigParser()
    config_path = utils.root_path / "config"
    config.read(str(config_path))
    return config["synoptic"]["token"]

def format_url(city, start, end):
    """
    Parameters:
    city - string: either 'NYC' or 'CHI'
    start - a date in format YYYY-MM-DD
    end - string: either 'today' or date in format YYYY-MM-DD"""
    
    stid = city_to_stid[city]
    
    start = format_date(start)
    
    if end == 'today':
        end =  datetime.now().strftime("%Y%m%d%H%M")
    else:
        end = format_date(end)
        
    token = get_token()
    
    final_url = f"{synoptic_base_url}&stid={stid}&start={start}&units=temp|F&end={end}&showemptystations=1&token={token}"
    
    return final_url

def date_dataframe(final_url):
    r = requests.get(final_url)
    if not r.ok:
        print("Error")
        return
    
    r_json = r.json()
    
    date_time = r_json["STATION"][0]["OBSERVATIONS"]['date_time']
    highs = r_json["STATION"][0]["OBSERVATIONS"]['air_temp_high_24_hour_set_1']
    k = pd.Series(highs, index=date_time).dropna()
    df = k.to_frame()
    df = df.shift(-1).dropna()
    df.columns = ["temp_float"]
    df["temp_int"] = df["temp_float"].round().astype(int)
    return df
