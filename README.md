# Weather Data Project
This project extracts weather data from a free public API, transforms it, and then loads it into a Google BigQuery database table.
This data is used to create the looker report linked below to show changes in weather patterns in Cleveland, TN over time.
It is also used to create a machine learning model that will attempt to predict the tomorrow's temperature using historical data.

The ETL pipeline consists of two parts.
1. The get_historic_raw_data.py file runs one time to get the previous 80 years of data from January 1st 1940 to December 16th 2025. The current date inside of the get_historic_raw_data.py is for a previous run retrieving data for the 1990s. I had to do this because the OpenMeteo API only allows users to make 10000 API calls every day which required me to run this pipeline over the course of a few days to get all 80 years of data.
2. The get_raw_data.py file runs every day using Apache Airflow to get the previous day's weather data. As long as my machine is running, this Data Pipeline works without a hitch.

I have included both my data pipeline files and the Apache Airflow files in this repository.
