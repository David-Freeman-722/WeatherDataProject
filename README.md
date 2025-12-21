# Weather Data Project
This project extracts weather data from a free public API, transforms it, and then loads it into a Google BigQuery database table.
This data is used to create the looker report linked below to show changes in weather patterns in Cleveland, TN over time.
It is also used to create a machine learning model that will attempt to predict the tomorrow's temperature using historical data.

The ETL pipeline consists of two parts.
1. The get_historic_raw_data.py file runs one time to get the previous 80 years of data from January 1st 1940 to December 16th 2025. The current date inside of the get_historic_raw_data.py is for a previous run retrieving data for the 1940s. I had to do this because the OpenMeteo API only allows users to make 10000 API calls every day which required me to run this pipeline over the course of a few days to get all 80 years of data.
2. The get_raw_data.py file runs every day using Apache Airflow to get the previous day's weather data.
3. The weather_dag.py file is an Apache Airflow python DAG that orchestrates running the get_raw_data.py file on a daily basis.


I have included both my data pipeline files and the Apache Airflow files in this repository.

Below is a link to my looker project that shows visualizations of the data collected through my pipeline.

https://lookerstudio.google.com/reporting/cbb9543d-2d96-4999-bc2a-884aa408e6d3
