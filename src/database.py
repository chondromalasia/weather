import sqlite3
from sqlite3 import Error 
import sys

import pandas as pd

import src.scraper as scraper
import src.utils as utils

def sql_connection():
    try:
        db_path = utils.root_path / "data" / "data.db"
        conn = sqlite3.connect(str(db_path))
        return conn
    except Error:
        print(Error)

def database_init():

    conn = sql_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS forecasts
    (ID INT PRIMARY KEY,
    CITY TEXT NOT NULL,
    FORECAST_DATE TEXT NOT NULL,
    TIME_OF_FORECAST TEXT NOT NULL,
    PLATFORM TEXT NOT NULL,
    TEMPERATURE INTEGER NOT NULL);""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS observed_temp
    (ID INT PRIMARY KEY,
    CITY TEXT NOT NULL,
    DATE TEXT NOT NULL,
    TEMPERATURE INTEGER NOT NULL);""")

    conn.commit()

    conn.close()

def write_rows(rows):

    conn = sql_connection()
    cursor = conn.cursor()

    insert_query = """INSERT INTO forecasts
               (CITY, FORECAST_DATE, TIME_OF_FORECAST, PLATFORM, TEMPERATURE)
               VALUES (?, ?, ?, ?, ?)"""

    cursor.executemany(insert_query, rows)

    conn.commit()

    conn.close()

### Daily Highs Zone

def prep_to_write(df, city, start_date):
    
    df["city"] = city
    df["date"] = df.index
    to_write = df[["city", "date", "temp_int"]].values.tolist()
    
    final_to_return = []
    for row in to_write:
        date = row[1].split("T")[0]
        if date > start_date:
            final_to_return.append([row[0], date, row[2]])
    
    return final_to_return


def write_high_temps(to_write):
    
    conn = sql_connection()
    cursor = conn.cursor()
    
    insert_query = """INSERT INTO observed_temp
               (CITY, DATE, TEMPERATURE)
               VALUES (?, ?, ?)"""
    
    cursor.executemany(insert_query, to_write)
    
    conn.commit()
    conn.close()

def most_recent_high_date(city):

    conn = sql_connection()
    cursor = conn.cursor()

    query = """SELECT date(DATE) FROM observed_temp
    WHERE CITY=?
    ORDER BY date(DATE) desc
    LIMIT 1;"""

    cursor.execute(query, (city,))

    start_date = cursor.fetchall()[0][0]

    conn.close()

    return(start_date)

def forecasts_and_observations():
    """Get every forecast and observation"""

    conn = sql_connection()

    query = """SELECT forecasts.CITY, 
            date(FORECAST_DATE) as forecast_date, 
            PLATFORM, 
            forecasts.TEMPERATURE as forecast_temperature,
            date(DATE) as observed_date,
            observed_temp.TEMPERATURE as observed_temperature
            FROM forecasts
            LEFT JOIN observed_temp
            ON forecasts.city = observed_temp.city
            AND date(forecasts.forecast_date) = date(observed_temp.date);
            """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

    


