'''
Takes in data that has already been formatted in format_data.py,
& runs Baum Welch algorithm to infer parameters
'''

from baum_welch_alg import BaumWelch
import sys
import argparse

import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp

# This code is available at:
# https://github.com/kimberlymcm/algorithm_practice/blob/master/weather_data_explorations/src/baum_welch_alg.py
sys.path.append(
    "/Users/kmcmanus/Documents/classes/algorithm_practice/weather_data_explorations/src")


def run_random_start(args, observations):
    ''' Run Baum Welch from different starting vals '''

    num_steps = len(observations)

    tfd = tfp.distributions
    initial_distribution = tfd.Categorical(probs=[0.66, 0.33])

    trans_start = np.random.uniform(low=0.9, high=0.99, size=2)
    transition_distribution = tfd.Categorical(probs=[[trans_start[0], 1 - trans_start[0]],
                                                     [1 - trans_start[1], trans_start[1]]])
    observ_mean_start_one = np.random.randint(low=55, high=67, size=1)
    observ_mean_start_two = np.random.randint(low=75, high=90, size=1)
    observ_stdev_start = np.random.randint(low=2, high=10, size=2)

    observation_distribution = tfd.Normal(loc=[float(observ_mean_start_one[0]),
                                               float(observ_mean_start_two[0])],
                                          scale=[float(observ_stdev_start[0]),
                                                 float(observ_stdev_start[1])])

    logdir = "{}/run_t_{}_{}_obmean_{}_{}_obstd_{}_{}".format(args.out_dir,
                                                              trans_start[0],
                                                              trans_start[1],
                                                              observ_mean_start_one,
                                                              observ_mean_start_two,
                                                              observ_stdev_start[0],
                                                              observ_stdev_start[1])

    model = BaumWelch(initial_distribution=initial_distribution,
                      observation_distribution=observation_distribution,
                      transition_distribution=transition_distribution,
                      num_steps=num_steps,
                      epsilon=0.5,
                      maxStep=50,
                      log_dir=logdir)

    initial_dist, trans_dist, observ_dist = model.run_baum_welch_em(
        observations)


def main(args):

    df = pd.read_csv(args.in_file, index_col=0)
    print("Num rows: {}".format(df.shape[0]))
    df = df[~df['bpm'].isnull()]  # Drop minutes where there wasn't a reading
    print("Num rows after dropping null bpm: {}".format(df.shape[0]))

    # Limit to about 2 weeks of data
    observations = tf.constant(
        df['bpm'][0:20160], dtype=tf.float32, name='observation_sequence')

    for i in range(0, 20):
        run_random_start(args, observations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in_file",
        help="Input directory with heart rate data",
        default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/formatted_data/20200308_hr_sleep_1min_first.csv")
    parser.add_argument(
        "--out_dir",
        help="Output directory with heart rate data",
        default="/Users/kmcmanus/Documents/classes/digitalhealth_project/data/hmm_tf_logs")
    args = parser.parse_args()
    main(args)
