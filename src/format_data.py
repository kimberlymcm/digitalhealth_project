''' Convert raw fitbit jsons to formats more ammenable to working with '''

import argparse
import glob
import json

import pandas as pd


def create_heart_rate_df(fn):
    '''
    Returns a formatted heart rate dataframe

            Parameters:
                    fn (str): Filename of heart rate json from fitbit

            Returns:
                    df (pd.DataFrame): Dataframe with bpm, confidence and datetime
    '''
    with open(fn) as f:
        file_contents = json.load(f)
    index = pd.to_datetime([x["dateTime"] for x in file_contents])
    # Fix difference in time zone problem
    index = [x - pd.Timedelta(8, unit="h") for x in index]
    data = [[x["value"]["bpm"], x["value"]["confidence"]]
            for x in file_contents]
    df = pd.DataFrame(data, index=index, columns=["bpm", "confidence"])
    df["datetime"] = df.index
    return df


def add_fitbit_sleep_assignments(fn, df):
    '''
    Adds fitbit's inferred sleep/awake state to df

            Parameters:
                    fn (str): Filename of heart rate json from fitbit
                    df (pd.DataFrame): Dataframe with heart rate data

            Returns:
                    df (pd.DataFrame): Dataframe with bpm, confidence, datetime, and sleep state
    '''
    value_dict = {'wake': 1, 'light': 0, 'deep': -1, 'rem': -2}
    with open(fn) as f:
        fitbit_sleep = json.load(f)

    for i in range(0, len(fitbit_sleep)):
        for my_dict in fitbit_sleep[i]['levels']['data']:
            start = pd.Timestamp(my_dict['dateTime'])
            end = start + pd.Timedelta(my_dict['seconds'], unit='s')
            value_to_use = value_dict[my_dict['level']]
            df.loc[(df['datetime'] > start) & (
                df['datetime'] <= end), "fb_sleep"] = value_to_use
    fitbit_sleep['minutesAsleep']
    return(df)


def main(args):

    pattern_match_hr = args.in_dir + "/heart_rate*json"
    hr_files = glob.glob(pattern_match_hr)

    frames = [create_heart_rate_df(fn) for fn in hr_files]
    df = pd.concat(frames)
    df.sort_values(by="datetime", inplace=True)
    print('Raw rows: {}'.format(df.shape[0]))

    # Take just first reading per minute
    df = df.resample('1Min').first()
    df["datetime"] = df.index
    print('Resampled rows (1Min): {}'.format(df.shape[0]))

    df["fb_sleep"] = 1  # Missing data
    pattern_match_sleep = args.in_dir + "/sleep*json"
    sleep_files = glob.glob(pattern_match_sleep)
    print(sleep_files)

    for sleep_fn in sleep_files:
        df = add_fitbit_sleep_assignments(sleep_fn, df)
    out_fn = args.out_dir + "/20201229_hr_sleep_1min_first.csv"
    df.to_csv(out_fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in_dir",
        help="Input directory with heart rate data",
        default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/data_dump/MyFitbitData_Dec2020/KimberlyMcManus/PhysicalActivity")
    parser.add_argument(
        "--out_dir",
        help="Output directory with heart rate data",
        default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/formatted_data")
    args = parser.parse_args()
    main(args)
