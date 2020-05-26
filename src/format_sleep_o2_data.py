# -*- coding: utf-8 -*-

""" Takes in a sleep position file and an O2 file.
Outputs a file with the data merged and cleaned.
"""

import click
import glob

import pandas as pd
import numpy as np


def read_files(files):
    """ Read in list of files and concatenate them into a dataframe 
        Arguments: files: list of string filenames
        Returns: dataframe of data
    """
    dfs = []
    for fn in files:
        df = pd.read_csv(fn)
        dfs.append(df)
    all_df = pd.concat(dfs)
    return all_df


def assign_sleep_night(df):
    """ Since nights span two dates, create a new column that assigns
        a 'sleep night' to be the date the night starts on
        Arguments: dataframe of sleep pos data
        Returns: Same dataframe with new 'sleep_night' column
    """
    df["sleep_night"] = None
    dates = np.unique(df.index.date)

    for i in range(0, len(dates)-1):
        start = pd.to_datetime("{} 17:00:00".format(dates[i]))
        if i < len(dates)-2:
            end = pd.to_datetime("{} 16:00:00".format(dates[i+1]))
            df.loc[start:end, "sleep_night"] = dates[i]
        else:
            df.loc[df.index > start, "sleep_night"] = dates[i]
    return df


def format_sleep_pos(sleep_pos_folder):
    """ Initially formats sleep position data
        Arguments: String name of folder with the data
        Returns: Datafrmae with sleep data
    """
    pattern_match_sleep_pos = sleep_pos_folder + "/SomnoPos*.csv"
    pos_files = glob.glob(pattern_match_sleep_pos)
    pos_df = read_files(pos_files)
    print("Position df lines: {}".format(pos_df.shape[0]))
    # Fills NA dates with the most recent non-NA date
    pos_df["Date"] = pos_df["Date"].fillna(method="ffill")
    # Drop any row with a NA in any row
    # This should just drop the first minute of recordings
    # TODO(kmcmanus): Probably want to solve the NAs
    pos_df = pos_df.dropna()
    pos_df["datetime"] = pd.to_datetime(pos_df["Time_of_day"] + " " + pos_df["Date"])
    pos_df.index = pos_df["datetime"]
    pos_df = pos_df.sort_index()
    pos_df = assign_sleep_night(pos_df)
    pos_df = pos_df.drop(["Timestamp", "datetime", "Time_of_day", "Date"], axis=1)
    print("Position df lines (after dropping dups and NAs): {}".format(pos_df.shape[0]))
    pos_df = pos_df.resample("5S").first()
    print("Position df lines after resampling (5S): {}".format(pos_df.shape[0]))
    return pos_df


def format_o2(o2_folder):
    """ Initially formats sleep o2 data
        Arguments: String name of folder with the data
        Returns: Datafrmae with sleep data
    """
    pattern_match_o2 = o2_folder + "/O2Ring-*OXIRecord.csv"
    o2_files = glob.glob(pattern_match_o2)
    o2_df = read_files(o2_files)
    print("SpO2 lines: {}".format(o2_df.shape[0]))

    # It looks like the last few measurements of each file are bogus
    print("Lines removed with SpO2(%) > 100: {}".format(o2_df[o2_df["SpO2(%)"] > 100].shape[0]))
    o2_df = o2_df[o2_df["SpO2(%)"] <= 100]

    o2_df["datetime"] = pd.to_datetime(o2_df["Time"], format="%H:%M:%S %b %d %Y")
    o2_df.index = o2_df["datetime"]
    o2_df = o2_df.drop(["datetime", "Time"], axis=1)
    o2_df = o2_df.sort_index()
    o2_df = o2_df.resample("5S").first()
    print("SpO2 lines after resampling (5S): {}".format(o2_df.shape[0]))
    return o2_df


@click.command()
@click.option("--sleep_pos_folder", help="File with sleep position data.",
	default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/sleep_position")
@click.option("--o2_folder", help="Folder with Wellue records",
    default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/wellvue_o2_data")
@click.option("--out_filename", help="Output filename",
	default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/formatted_data/20200526_sleep_pos_5S.csv")
def main(sleep_pos_folder, o2_folder, out_filename):
    """ hi """
    pos_df = format_sleep_pos(sleep_pos_folder)

    o2_df = format_o2(o2_folder)

    merged_df = pd.merge(pos_df, o2_df, how="outer", left_index=True, right_index=True)
    
    merged_df = assign_sleep_night(merged_df)
    merged_df.to_csv(out_filename)


if __name__ == '__main__':
    main()