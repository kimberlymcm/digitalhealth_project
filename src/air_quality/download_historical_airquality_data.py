import requests
import pandas as pd

# Practice
parameters = {"country": "US", "limit": 10000, "city": "MONO"}
response = requests.get("https://api.openaq.org/v1/locations",
    params=parameters)
print(response)
json_to_use = response.json()
df = pd.json_normalize(json_to_use["results"])


parameters = {
    "location": "San Francisco",
    "limit": 10000,
    "date_from": "2020-01-01",
    "include_fields": "sourceName",
    "parameter": "pm25",
}

response = requests.get("https://api.openaq.org/v1/measurements",
    params=parameters)
print(response)
json_to_use = response.json()

df = pd.json_normalize(json_to_use["results"])
df.drop(["coordinates.longitude", "coordinates.latitude", "country", "city"],
    axis=1, inplace=True)
df.to_csv("/Users/kmcmanus/Documents/classes/digitalhealth_project/data/air_quality/air_quality_data_pm25_20210110_sf.csv",
    index=False)

parameters = {
    "location": "Mammoth Lakes",
    "limit": 10000,
    "date_from": "2020-01-01",
    "include_fields": "sourceName",
    "parameter": "pm25",
}

response = requests.get("https://api.openaq.org/v1/measurements",
    params=parameters)
print(response)
json_to_use = response.json()

df = pd.json_normalize(json_to_use["results"])
df.drop(["coordinates.longitude", "coordinates.latitude", "country", "city"],
    axis=1, inplace=True)
df.to_csv("/Users/kmcmanus/Documents/classes/digitalhealth_project/data/air_quality/air_quality_data_pm25_20210110_mono.csv",
    index=False)