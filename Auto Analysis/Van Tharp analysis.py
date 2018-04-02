
# coding: utf-8

# In[1]:


"""
This program imports a Yahoo formatted csv data file
and conducts Van Tharp style Market Analysis on the security.
"""


# In[30]:


# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
import os


# In[3]:


get_ipython().magic('matplotlib inline')


# In[67]:


def import_data():
    """
    Inputs: None
    Output: dataframe with the OHLC price history
    """
    
    print('This script requires you to be in the directory of the file that you wish to process.')
    print('Go to that directory now.')
    print('Copy to clipboard the filename that you wish to conduct the Van Tharp Analysis on .')
    file = input('Paste the full filename and extension here: ')
    
    # Import the csv file to a dataframe for analysis
    df = pd.read_csv(file, index_col='Date', parse_dates=True)
    df.sort_index(inplace=True)
    
    return df


# In[68]:


def calc_SQN100(df):
    """
    Input: dataframe with OHLC historical data
    Output: data dataframe updated with SQN100 column
    """
    
    df['Daily Pct Chg'] = df['Close'].pct_change() * 100
    df['SQN100'] = df['Daily Pct Chg'].rolling(window=100).mean() / df['Daily Pct Chg'].rolling(window=100).std() * math.sqrt(100)
    return df


# In[69]:


def calc_ATR20(df):
    """
    Input: data dataframe wth OHLC historical data
    Output: dataframe updated with ATR20
    """
    
    df['Prev Close'] = df['Close'].shift(1) # dates must be sorted ascending
    
    df['Range'] = (df['High'] - df['Low']).abs()
    df['UpGapRange'] = (df['High'] - df['Prev Close']).abs()
    df['DownGapRange'] = (df['Low'] - df['Prev Close']).abs()

    df['True Range'] = df[['Range', 'UpGapRange', 'DownGapRange']].apply(np.max, axis=0)

    df['ATR20'] = df['True Range'].rolling(20).mean()
    
    return df


# In[54]:


def calc_ATR20_pct(df):
    """
    Input: data dataframe with ATR20 column
    Output: dataframe with ATR20Pct column
    """
    df['ATR20 Pct'] = df['ATR20'] / df['Close'] * 100
    return df


# In[55]:


def calc_volatility_20day(df):
    """
    Input: data dataframe
    Output: dataframe with traditional 20'day volatility column
    """
    # Calculate 20-day annualized traditional volatility
    df['volatility'] = df['Daily Pct Chg'].rolling(20).std() * np.sqrt(20)
    return df


# In[63]:


def mkt_dir_type(SQN100):
    """
    Input: SQN100 (float)
    Output: Market Classification (str)
    """
        
        # from Super Traders:
            # strong_bull = 1.5
            # bull = 0.75
            # neutral = 0
            # bear = -0.45

    # from Position Sizing Guide:
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


# In[73]:


def mkt_dir_num(mkt_dir_type):
    """
    Input: market direction type (str)
    Output: market direction number (integer)
    """
        
    if mkt_dir_type == 'Strong Bull':
        return 2    
    elif mkt_dir_type == 'Bull':
        return 1
    elif mkt_dir_type == 'Neutral':
        return 0
    elif mkt_dir_type == 'Bear':
        return -1
    elif mkt_dir_type == 'Strong Bear':
        return -2
    else:
        return None


# In[70]:


def apply_mkt_dir_type(df):
    """
    Input: data dataframe with SQN100 column
    Output: input dataframe updated with Market Direction Type column
    """
    
    # Apply mkt_dir_type function to the DataFrame
    df['Market Direction Type'] = df['SQN100'].apply(mkt_dir_type)     
    return df


# In[74]:


def apply_mkt_dir_num(df):
    """
    Input: data dataframe with Market Direction Type column
    Output: input dataframe updated with Market Direction Num column
    """
    
    # Apply mkt_dir_num function to the DataFrame
    df['Market Direction Number'] = df['Market Direction Type'].apply(mkt_dir_num)     
    return df


# In[62]:


def mkt_vol_type(ATR20pct):
    """
    Input: ATR20pct (float)
    Output: market volatility type (str)
    """
        
    # from Position Sizing Guide
    super_volatile = 3.5
    volatile = 1.7
    normal = 0.98

    if ATR20pct > super_volatile:
        return 'Super Volatile'
    elif ((ATR20pct > volatile) and (ATR20pct <= super_volatile)):
        return 'Volatile'
    elif ((ATR20pct > normal) and (ATR20pct <= volatile)):
        return 'Normal'
    elif ATR20pct <= normal:
        return 'Quiet'
    else:
        return None


# In[72]:


def mkt_vol_num(mkt_vol_type):
    """
    Input: market volatility type (str)
    Output: market volatility type (int)
    """
    
    if mkt_vol_type == 'Quiet':
        return 0
    elif mkt_vol_type == 'Normal':
        return 1
    elif mkt_vol_type == 'Volatile':
        return 2
    elif mkt_vol_type == 'Very Volatile':
        return 3
    else:
        return None


# In[25]:


def apply_mkt_vol_type(df):
    """
    Input: data dataframe with 'ATR20 Pct' column
    Output: data dataframe updated with Market Volatility Type column
    """
    
    df['Market Volatility Type'] = df['ATR20 Pct'].apply(mkt_vol_type)
    return df


# In[26]:


def apply_mkt_vol_num(df):
    """
    Input: data dataframe with 'Market Volatility Type' column
    Output: data dataframe updated with Market Volatility Num column
    """
    
    df['Market Volatility Num'] = df['Market Volatility Type'].apply(mkt_vol_num)
    return df


# In[28]:


def apply_full_mkt_type(df):
    """
    Input: data dataframe with Market Direction Type and Market Volatility Type columns
    Output: data dataframe updated with Market Type column
    """
    
    df['Market Type'] = df['Market Direction Type'] + ' - ' + df['Market Volatility Type']
    return df


# In[29]:


def save_analysis_file(df):
    """
    Input: data dataframe with all Van Tharp analysis complete
    Output: csv file saved to disk in original directory location with "analysis appended to beginning of filename'
    """
    
    df.to_csv('analysis_'+ file)
    return df


# # Summary table functions

# In[34]:


def mkt_type_summary_direction(df):
    """
    Input:
    Output:
    """
    
    dir_summary = df.groupby('Market Direction').mean()
    direction_summary = dir_summary[['ATR20 Pct','Daily Chg Pct','SQN100']]
    return direction_summary


# In[35]:


def mkt_type_summary_volatility(df):
    """
    Input:
    Output:
    """
    
    vol_summary = spx.groupby('Market Volatility').mean()
    volatility_summary = vol_summary[['ATR20 Pct','Daily Chg Pct','SQN100']]
    return volatility_summary


# In[37]:


def mkt_type_summary_pct_time_dir(df):
    """
    Input:
    Output:
    """
    
    mkt_dir_pct_time = spx.groupby('Market Direction').count() / spx.count() * 100
    return mkt_dir_pct_time['ATR20'].sort_values(ascending=False)


# In[38]:


def mkt_type_summary_pct_time_vol(df):
    """
    Input:
    Output:
    """
    
    mkt_vol_pct_time = spx.groupby('Market Volatility').count() / spx.count() * 100
    return mkt_vol_pct_time['ATR20'].sort_values(ascending=False)


# In[39]:


def mkt_type_summary_full(df):
    """
    Input:
    Output:
    """
    
    type_summary = spx.groupby('Market Type').mean()[['ATR20 Pct','Daily Chg Pct','SQN100']]
    return type_summary


# In[40]:


def mkt_type_summary_pct_time_full(df):
    """
    Input:
    Output:
    """
    
    mtype = spx.groupby('Market Type').count() / spx.count() * 100
    return mtype['Close'].sort_values(ascending=False)


# In[42]:


# This is example code for pulling out a dataframe of just one market type
def bear_volatile_df(df):
    """
    Input:
    Output:
    """
    
    bear_volatile = df[df['Market Type'] == 'Bear - Volatile'][['ATR20 Pct', 'Daily Chg Pct', 'SQN100', 'Market Type']]
    return bear_volatile


# # Distribution Plot functions

# In[48]:


def mkt_dir_vs_daily_pct_chg_violin(df):
    sns.violinplot(x='Market Direction',y='Daily Chg Pct', data=df);


# In[47]:


def mkt_dir_vs_atr20pct_violin(df):
    sns.violinplot(x='Market Direction',y='ATR20 Pct', data=df);


# In[49]:


def mkt_type_vs_daily_pct_chg_violin(df):
    sns.violinplot(y='Market Type', x='Daily Chg Pct', data=df, scale='count');


# In[50]:


def mkt_type_vs_atr20pct(df):
    sns.violinplot(y='Market Type', x='ATR20 Pct', data=df, width=0.8);


# # Call the functions in order

# In[ ]:


# Van Tharp analysis functions
    # import_data()
    # calc_SQN100(df)
    # calc_ATR20(df)
    # calc_ATR20_pct(df)
    # calc_volatility_20day(df)
    # mkt_dir_type(SQN100)
    # mkt_dir_num(mkt_dir_type)
    # apply_mkt_dir_type(df)
    # apply_mkt_dir_num(df)
    # mkt_vol_type(ATR20pct)
    # mkt_vol_num(mkt_vol_type)
    # apply_mkt_vol_type(df)
    # apply_mkt_vol_num(df)
    # apply_full_mkt_type(df)
    # save_analysis_file(df)

# Summary Table Functions
    # mkt_type_summary_direction(df)
    # mkt_type_summary_volatility(df)
    # mkt_type_summary_pct_time_dir(df)
    # mkt_type_summary_pct_time_vol(df)
    # mkt_type_summary_full(df)
    # mkt_type_summary_pct_time_full(df)
    # bear_volatile_df(df)
    
# Distribution Plot Functions
    # mkt_dir_vs_daily_pct_chg_violin(df)
    # mkt_dir_vs_atr20pct_violin(df)
    # mkt_type_vs_daily_pct_chg_violin(df)
    # mkt_type_vs_atr20pct(df)

