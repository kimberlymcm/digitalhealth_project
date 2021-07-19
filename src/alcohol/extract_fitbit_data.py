# First run python3 authorize_fitbit.py
import pandas as pd
import json
import time

# Get secrets
with open("/Users/kmcmanus/Documents/classes/digitalhealth_project/data/keys/fitbit_credentials.txt") as fp:
    lines = fp.readlines()
    client_id = lines[0].strip()
    client_secret = lines[1].strip()

with open("/Users/kmcmanus/Documents/classes/digitalhealth_project/data/keys/temp_creds.txt") as fp:
    lines = fp.readlines()
    access_token = lines[0].strip()
    refresh_token = lines[1].strip()
    expires_at = float(lines[2].strip())

from api import Fitbit
okk = Fitbit(client_id=client_id, client_secret=client_secret,
	access_token=access_token,
	refresh_token=refresh_token,
	expires_at=expires_at)


dates = pd.date_range(start='2021-03-08', end='2021-06-09')
final_df = pd.DataFrame(columns = ['time', 'value', 'date'])
for date in dates:
	result = okk.intraday_time_series('activities/heart',
		base_date=date, detail_level='1min',
		start_time=None, end_time=None)

	df_nested_list = pd.json_normalize(result['activities-heart-intraday'], record_path =['dataset'])
	df_nested_list["date"] = date
	final_df.append(df_nested_list)
	time.sleep(3)


final_df.to_csv("/Users/kmcmanus/Documents/classes/digitalhealth_project/data/alcohol/hr_data_20210308_20210609_1min.csv")
