
""" Takes in merged sleep position O2 file and makes
additional modifications
"""

import click

import pandas as pd
import numpy as np


def add_orient_oxy_bin(df):
    """ Bin the orientation and oxygen data """
    df["orient_bin"] = None
    df.loc[df["Orientation"] > 40, "orient_bin"] = -1  # Right
    df.loc[(df["Orientation"] > -60) &
           (df["Orientation"] <= 40), "orient_bin"] = 0  # Back
    df.loc[(df["Orientation"] > -
            361) & (df["Orientation"] <= -
                    60), "orient_bin"] = 1  # Left

    df["low_oxygen"] = 0  # Not low
    df.loc[df["SpO2(%)"] <= 88, "low_oxygen"] = 1  # Yes low oxygen
    return df


def add_timing_info(df):
    """ Add extra columns about timing that will be used for graphing """

    # This is so hacky. There has to be a better way.
    df["hour"] = None
    df.loc[:, "hour"] = [str(x) if x > 10 else "0" + str(x)
                         for x in df.index.hour]
    num_measurements_per_hour = df.groupby(
        [df.index.date, df["hour"]]).count().reset_index()
    hours_to_use_df = num_measurements_per_hour[num_measurements_per_hour["Orientation"] == 720]
    hours_to_use_str = hours_to_use_df["level_0"].astype(
        str) + " " + hours_to_use_df["hour"].astype(str)
    hours_to_use_datetime = pd.to_datetime(
        hours_to_use_str, format='%Y-%m-%d %H')

    df["complete_hour"] = 0
    df.loc[df.index.floor("H").isin(
        hours_to_use_datetime), "complete_hour"] = 1

    min_night_length = 720 * 5
    df_num = df.groupby("sleep_night")["hour"].count()
    df_num_to_use = df_num.loc[df_num >= min_night_length]

    df["complete_night"] = 0
    df.loc[df["sleep_night"].isin(df_num_to_use.index), "complete_night"] = 1

    return df


@click.command()
@click.option(
    "--in_file",
    help="File with merged sleep data (from format_sleep_o2_data.py.",
    default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/formatted_data/20200526_sleep_pos_5S.csv")
@click.option(
    "--out_file",
    help="Outfile name",
    default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/formatted_data/20200526_sleep_pos_5S_cleaned.csv")
def main(in_file, out_file):
    df = pd.read_csv(
        in_file,
        index_col='datetime',
        parse_dates=True,
        infer_datetime_format=True)

    df_subset = df.dropna()  # Drop any rows that don't have both measurements
    print(df_subset.head())
    df_subset = add_orient_oxy_bin(df_subset)
    df_subset = add_timing_info(df_subset)
    df_subset.to_csv(out_file)


if __name__ == '__main__':
    main()
