"""
This program imports a Yahoo formatted csv data file
and conducts Van Tharp style Market Analysis on the security.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
import os


def van_tharp_analysis():
    print('This script requires you to be in the directory of the file that you wish to process. \n Go to that directory now.')
    print('Copy to clipboard the filename that you wish to conduct the Van Tharp Analysis on .')
    file = input('Paste the full filename and extension here: ')
    
    analysis_file = file + '-analysis.csv'
    analysis_file_path = os.path.join('./Output', analysis_file)
    # df.to_csv(analysis_file_path)  <-- move this to the end of the file
    
    
    # Import the csv file to a dataframe for analysis
    df = pd.read_csv(file, index_col='Date', parse_dates=True)
    df.sort_index(inplace=True)

    # Calclulate SQN100
    df['Daily Pct Chg'] = df['Close'].pct_change() * 100
    df['SQN100'] = df['Daily Pct Chg'].rolling(window=100).mean() / df['Daily Pct Chg'].rolling(window=100).std() * math.sqrt(100)

    # Calculate Average True Range Percent
    df['Prev Close'] = df['Close'].shift(1) # assumes dates are sorted ascending
    
    df['Range'] = (df['High'] - df['Low']).abs()
    df['UpGapRange'] = (df['High'] - df['Prev Close']).abs()
    df['DownGapRange'] = (df['Low'] - df['Prev Close']).abs()

    df['True Range'] = df[['Range', 'UpGapRange', 'DownGapRange']].apply(np.max, axis=0)

    df['ATR20'] = df['True Range'].rolling(20).mean()

    df['ATR20 Pct'] = df['ATR20'] / df['Close'] * 100

    # Calculate 20-day annualized traditional volatility
    df['volatility'] = df['Daily Pct Chg'].rolling(20).std() * np.sqrt(20)

    # Plot frequency distribution of SQN100
    df['SQN100'].hist(grid=True, bins=100)

    # Create function to define Market Type
    def mkt_dir_type(SQN100):
        
        # from Super Traders
        #strong_bull = 1.5
        #bull = 0.75
        #neutral = 0
        #bear = -0.45

        # from Position Sizing Guide
        strong_bull = 1.47
        bull = 0.7
        neutral = 0
        bear = -0.7

        if SQN100 > strong_bull:
            return 'Strong Bull'
            
        elif ((SQN100 > bull) and (SQN100 <= strong_bull)):
            return 'Bull'
            
        elif ((SQN100 > neutral) and (SQN100 <= bull)):
            return 'Neutral'
            
        elif ((SQN100 > bear) and (SQN100 <= neutral)):
            return 'Bear'
            
        elif SQN100 <= bear:
            return 'Strong Bear'
            
        else:
            return None
    
    # Apply above function
    df['Market Direction Type', dtype='Category'] = df['SQN100'].apply(mkt_dir_type)     
    
    def mkt_dir_num(direction):
        # from Super Traders
        #strong_bull = 1.5
        #bull = 0.75
        #neutral = 0
        #bear = -0.45

        # from Position Sizing Guide
        strong_bull = 1.47
        bull = 0.7
        neutral = 0
        bear = -0.7
        
         if direction == 'Strong Bull':
            return 2
            
        elif direction == 'Bull':
            return 1
            
        elif direction == 'Neutral':
            return 0
            
        elif direction == 'Bear':
            return -1
            
        elif direction == 'Strong Bear':
            return -2
            
        else:
            return None
        
    # Create function to define Market Volatility Type
    def market_vol_type(ATR20pct):
        df['ATR20% 20MA'] = df['ATR20 Pct'].rolling(20).mean()
        df['ATR20% Std Dev'] = df['ATR20 Pct'].rolling(20).std()

        df['ATR20%: 3 std dev level'] = df['ATR20% 20MA'] + (3 * df['ATR20% Std Dev'])
        
        df['ATR20%: 0.5 std dev level'] = df['ATR20% 20MA'] + (0.5 * df['ATR20% Std Dev'])
        
        df['ATR20%: -0.5 std dev level'] = df['ATR20% 20MA'] + (-0.5 * df['ATR20% Std Dev'])
        

        super_volatile = df['ATR20%: 3 std dev level']
        volatile = df['ATR20%: 0.5 std dev level']
        normal = df['ATR20%: -0.5 std dev level']

        df['Market Volatility Type'] = None
        df['Market Volatility Type Number'] = None

        if ATR20pct > super_volatile:
            df['Market Volatility Type'] = 'Super Volatile'
            df['Market Volatility Type Number'] = 4
        elif ATR20pct > volatile and ATR20pct <= super_volatile:
            df['Market Volatility Type'] = 'Volatile'
            df['Market Volatility Type Number'] = 3
        elif ATR20pct > normal and ATR20pct <= volatile:
            df['Market Volatility Type'] = 'Normal'
            df['Market Volatility Type Number'] = 2
        elif ATR20pct <= normal:
            df['Market Volatility Type'] = 'Quiet'
            df['Market Volatility Type Number'] = 1
        else:
            df['Market Volatility Type'] = None
            df['Market Volatility Type Number'] = None
