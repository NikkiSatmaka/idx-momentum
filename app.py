#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pytz
import logging
import numpy as np
import pandas as pd

from datetime import datetime
from pathlib import Path
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format=" %(asctime)s - %(levelname)s - %(message)s",
)
warnings.filterwarnings("ignore")

# Create a custom logger
logger = logging.getLogger(__name__)

# csvDir = Path.home().joinpath(r'Documents\data-ab\idx_exported_csv')
csvDir = Path.home().joinpath('.var/app/com.usebottles.bottles/data/bottles/bottles/amibroker/drive_c/data-ab/idx_exported_csv')


def load_data(path):
    """
    Input: Directory of csv timeseries files.
    Output: Dictionary where the key is the ticker
        and the value is a pandas dataframe of the OHLC time series
    """
    csv_loc = Path(path)    # csv folder Path, make sure it's a Path object

    # IDX stock's tickers always have 4 characters
    files = list(csv_loc.glob('????.csv'))

    data_idx = {}
    for file in files:
        data_idx[file.stem] = pd.read_csv(file,
                                        index_col=0,
                                        parse_dates=True)
        data_idx[file.stem] = data_idx[file.stem].tz_localize(tz='Asia/Jakarta')

    return data_idx


def momentum_score(timeseries):
    """
    Input:  Price time series.
    Output: Annualized exponential regression slope, 
            multiplied by the R2
    """
    # Make a list of consecutive numbers
    x = np.arange(len(timeseries)) 
    # Get logs
    log_ts = np.log(timeseries) 
    # Calculate regression values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_ts)
    # Annualize percent
    annualized_slope = (np.power(np.exp(slope), 252) - 1) * 100
    #Adjust for fitness
    score = annualized_slope * (r_value ** 2)
    return score


def volatility(timeseries, period=24):
    """
    Input:  Price time series, Look back period
    Output: Standard deviation of the percent change
    """
    return timeseries.pct_change().rolling(period).std().iloc[-1]


def filter_stocks(path, momentum_window, vola_window, ma_period_fast, ma_period_slow):
    """
    Input: Path to the csv files
    momentum_window: How many (series) candles back for momentum calculation?
    vola_window: How many (series) candles+1 back for std dev calculation?
    ma_period_fast: How many (series) candles back for EWMA fast calculation?
    ma_period_slow: How many (series) candles back for EWMA slow calculation?

    Output: Tuple of 2 pandas
    1. Passed stocks
    2. Eliminated stocks
    """
    data = load_data(path)

    # Create an empty DataFrame to store Momentum stocks
    momentum_cols = [
        'ticker',
        'score',
        'vola',
        'inv_vola',
        'ma_fast',
        'ma_slow',
        'median_vol'
    ]
    momentum_df = pd.DataFrame(columns=momentum_cols)

    # Create an empty DataFrame to store Eliminated stocks
    eliminated_cols = ['ticker', 'score', 'vola', 'reason']
    eliminated_df = pd.DataFrame(columns=eliminated_cols)

    # Loop the dictionary and calculate the momentum_score, then append it to pandas
    for ticker, timeseries in data.items():
        momentum_series = timeseries['Close'].iloc[-momentum_window:]
        score = momentum_score(momentum_series)
        vola_series = timeseries['Close']
        vola = volatility(vola_series, vola_window) * 16
        with np.errstate(divide='ignore'):
            inv_vola = 1 / vola
        median_volume = timeseries['Volume'].rolling(vola_window).median().iloc[-1]
        ma_fast = timeseries['Close'].rolling(ma_period_fast).mean().iloc[-1]
        ma_slow = timeseries['Close'].rolling(ma_period_slow).mean().iloc[-1]

        # ewma = timeseries['Close'].ewm(span=ewma_period).mean().iloc[-1]

        # Prepare elimination of stocks
        eliminate = False

        # Need the stocks to exist at least 3 years prior (756 trading days)
        if len(timeseries) < 756:
            eliminate = True
            reason = 'umur belum 3 tahun'
        
        # If median volume falls below 100k in the stocks, drop it 
        elif median_volume < 100000:
            eliminate = True
            reason = 'median volume di bawah 100k'
            
        # If it has been suspended (daily vol == 0) more than once, drop it
        elif timeseries['Volume'].iloc[-momentum_window:].tolist().count(0) > 1:
            eliminate = True
            reason = 'pernah disuspend lebih dari 1x'

        else:
            pass

        # Adding to the DataFrame
        if eliminate:
            # Concat the new eliminated stock to the eliminated_df
            eliminate_new = [ticker, score, vola, reason]
            eliminate_new = pd.DataFrame([eliminate_new], columns=eliminated_cols)
            eliminated_df = pd.concat([eliminated_df, eliminate_new])

        else:
            # Concat the new momentum stock to the momentum_df
            momentum_new = [ticker, score, vola, inv_vola, ma_fast, ma_slow, median_volume]
            momentum_new = pd.DataFrame([momentum_new], columns=momentum_cols)
            momentum_df = pd.concat([momentum_df, momentum_new])
    
    momentum_df = momentum_df.reset_index(drop=True)
    eliminated_df = eliminated_df.reset_index(drop=True)

    return momentum_df, eliminated_df


## Run the function
if __name__ == "__main__":
    momentum_df, eliminated_df = filter_stocks(csvDir, 96, 24, 32, 128)

    logger.info(f'Ada {len(momentum_df)} saham lolos')
    logger.info(f'Ada {len(eliminated_df)} saham tereliminasi')

    print(momentum_df.sort_values('score', ascending=False)[:50])
    print(eliminated_df.sort_values('score', ascending=False)[:10])

    # Copy the DataFrame to clipboard
    momentum_df.sort_values('score', ascending=False)[:50].to_clipboard()

