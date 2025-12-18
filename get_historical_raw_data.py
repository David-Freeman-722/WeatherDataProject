import requests
import json
import pandas as pd
import datetime
import time
import sys
import os
import logging
import pytz
from google.cloud import bigquery
from dotenv import load_dotenv

# GOAL: Get the last 4 years of weather data into Google BigQuery

# CAUTION!!! RUN ONLY 1 TIME TO GET THE DATA INTO GBQ AS GBQ TABLES DO NOT ENFORCE KEY RESTRAINTS

SLEEP_TIME = 3
SESSION = requests.Session()

# Gets weather data for Cleveland TN over the past three months and uploads it to GBQ
def main():
    cleveland_lattitude = 35.1595
    cleveland_longitude = -84.8766
    city = "Cleveland"
    zip_code = "37312"
    state = "TN"
    country = "United States"
    location_info = {"city": city, "zip": zip_code, "state": state, "country": country}
    start_date = datetime.date(1991, 6, 7)
    end_date = datetime.date(1999, 12, 31)
    current_date = start_date

    # Runs pipeline to gradually insert historical data into my database
    while current_date <= end_date:
        # Runs ETL for every 28 days to gradually insert data into the database
        if end_date - current_date < datetime.timedelta(days=28):
            batch_end_date = end_date
        else:
            batch_end_date = current_date + datetime.timedelta(days=28)
        
        # Requests weather data from OpenMeteo
        current_weather = get_current_weather_data(cleveland_lattitude, cleveland_longitude, current_date, batch_end_date)

        # Sets current date to the end date plus one
        current_date = batch_end_date + datetime.timedelta(days=1)

        # Writes json data to json file on local computer
        with open('current_weather.json', 'w') as file:
            json.dump(obj=current_weather, fp=file, indent=4)

        # Gets weather data formatted as a list of dictionaries
        weather_data_by_day = extract_weather_data(current_weather, location_info)
        weather_df = pd.DataFrame(weather_data_by_day)

        # Download weather data as a csv
        csv_file_name = "weather_data.csv"
        weather_df.to_csv(csv_file_name, index=False, header=False)

        # BigQuery client
        # Loads environment variables
        load_dotenv('credentials.env')
        project = os.getenv("PROJECT_ID")
        dataset = os.getenv("DATASET_ID")
        table = os.getenv("TABLE_ID")
        full_table_id = f"{project}.{dataset}.{table}"
        load_csv_data_into_gbq(csv_file_name, full_table_id)

        # Sleep 3 seconds to avoid timing out api requests
        time.sleep(SLEEP_TIME)
    
def get_current_weather_data(latitude, longitude, start_date, end_date):
    # API to get current weather for Cleveland, TN 
    cleveland_tn_api_link = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&daily=weather_code,temperature_2m_mean,temperature_2m_max,temperature_2m_min,sunset,sunrise,precipitation_sum,rain_sum,snowfall_sum,precipitation_hours,wind_speed_10m_max,shortwave_radiation_sum&timezone=America%2FNew_York&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
    cleveland_tn_current_weather_response = SESSION.get(url=cleveland_tn_api_link, timeout=(5, 120))
    # print(cleveland_tn_current_weather_response)
    # print(cleveland_tn_current_weather_response.content)
    # breakpoint()
    cleveland_tn_current_weather_content = cleveland_tn_current_weather_response.json()
    logger.info("Previous 4 years of weather data retreived.")
    return cleveland_tn_current_weather_content

def extract_weather_data(current_weather, location_info):
    city = location_info["city"]
    state = location_info["state"]
    zip_code = location_info["zip"]
    country = location_info["country"]
    # Loops through current weather and corrleates data for each day
    daily_weather_data = current_weather["daily"]
    daily_weather_code = daily_weather_data["weather_code"]
    daily_time = daily_weather_data["time"]
    daily_temp_max = daily_weather_data["temperature_2m_max"]
    daily_temp_min = daily_weather_data["temperature_2m_min"]
    daily_temp_mean = daily_weather_data["temperature_2m_mean"]
    daily_precip = daily_weather_data["precipitation_sum"]
    daily_sunrise = daily_weather_data["sunrise"]
    daily_sunset = daily_weather_data["sunset"]
    daily_rain_sum = daily_weather_data["rain_sum"]
    daily_snowfall_sum = daily_weather_data["snowfall_sum"]
    daily_windspeed_max = daily_weather_data["wind_speed_10m_max"]
    daily_shortwave_rad = daily_weather_data["shortwave_radiation_sum"]
    daily_precip_hours = daily_weather_data["precipitation_hours"]
    load_dtime = datetime.datetime.now()
    logger.info(f"Processing {len(daily_time)} rows of weather data...")
    weather_data_by_day = [] # List of dictionaries with every day's data inside of it
    for i in range(len(daily_weather_data["time"])):
        weather_data_by_day.append({"date": daily_time[i],
                                    "weather_code": daily_weather_code[i], 
                                    "mean_temp": daily_temp_mean[i],
                                    "max_temp": daily_temp_max[i], 
                                    "min_temp": daily_temp_min[i], 
                                    "precip": daily_precip[i], 
                                    "rain_sum": daily_rain_sum[i],
                                    "snowfall_sum": daily_snowfall_sum[i],
                                    "windspeed_max": daily_windspeed_max[i],
                                    "shortwave_radiation": daily_shortwave_rad[i],
                                    "precip_hours": daily_precip_hours[i],
                                    "city": city,
                                    "zip_code": zip_code, 
                                    "state": state, 
                                    "country": country,
                                    "sunrise": daily_sunrise[i].split("T")[1] + ":00",
                                    "sunset": daily_sunset[i].split("T")[1] + ":00",
                                    "SYS_SRC_LOAD_DT": load_dtime},
                                    )
    
    logger.info(f"Finished processing {len(daily_time)} rows of weather data.")
    return weather_data_by_day

# Load data into the destination table
def load_csv_data_into_gbq(csv_filename, full_table_id):
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE_DATA,
        skip_leading_rows=1,
        autodetect=True,
        field_delimiter=","
    )
    logger.info("Loading data into GBQ...")
    with open(csv_filename, "rb") as file:
        job = client.load_table_from_file(
            file,
            full_table_id,
            job_config
        )
    
    # Runs job to load table with data from csv file
    job.result()
    logger.info("Finished loading data into GBQ.")
    

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',

        # Specify the handler to send logs to the console
        handlers=[
            # This handler sends logs to sys.stdout (Standard Output/Console)
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    main()