# First run python3 authorize_fitbit.py

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

result = okk.intraday_time_series('activities/heart',
	base_date='2021-07-16', detail_level='1min',
	start_time=None, end_time=None)

print(result)
