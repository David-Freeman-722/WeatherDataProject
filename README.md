# Weather Data Project
This project extracts weather data from a free public API, transforms it, and then loads it into a Google BigQuery database table.

The ETL pipeline consists of two parts.
1. The get_historic_raw_data.py file runs one time to get the previous 4 years of data from December 9th 2021 to December 9th 2025.
2. The get_raw_data.py file runs every day using Apache Airflow to get the previous day's weather data

I have included both my data pipeline files and the Apache Airflow files in this repository.
