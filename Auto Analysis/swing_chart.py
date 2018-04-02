
# coding: utf-8

# In[16]:


#import collections
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().magic('matplotlib inline')


# In[2]:


# Swing Chart with Filter
def swing_chart_dollar_filter(df, filter_value):
    """
    Input: dataframe with OHLC prices
    Output: dataframe with date and swing prices
    """
    # Create all necessary columns
    df['SwingDirection'] = None
    df['SwingHigh'] = None
    df['SwingLow'] = None
    df['UpReversalTest'] = None
    df['DownReversalTest'] = None
    df['SwingPrice'] = None
    
    #Get integer locations for columns
    high = df.columns.get_loc('High')
    low = df.columns.get_loc('Low')
    close = df.columns.get_loc('Close')
    swing_direction = df.columns.get_loc('SwingDirection')
    swing_high = df.columns.get_loc('SwingHigh')
    swing_low = df.columns.get_loc('SwingLow')
    up_reversal = df.columns.get_loc('UpReversalTest')
    down_reversal = df.columns.get_loc('DownReversalTest')
    swing_price = df.columns.get_loc('SwingPrice')
    
    # Initialize first row
    df.iat[0, swing_direction] = 'Up'
    df.iat[0, swing_high] = df.iat[0, high]
    df.iat[0, swing_low] = df.iat[[0, low]
    #df.iat[0, up_reversal] = False
    #df.iat[0, down_reversal] = False
    #df.iat[0, swing_price] = df.iloc[[0, close]
    
    for i, row in enumerate(df.itertuples(), start=1):
        if df.iat[i-1, swing_direction] == 'Up':
            if df.iat[i, high] >= df.iat[[i-1, swing_high]: #if today's high >= yesterday's swing high
                df.iat[i, swing_high] = df.iat[i, high] #set swing high = today's high
                df.iat[i, swing_direction] = 'Up' #set swing direction = up
                
            elif df.iat[i, high] < df.iat[i-1, swing_high]: #elif today's high < yesterday's swing high
                if (df.iat[i-1, swing_high] - df.iat[i, low]) > filter_value: #if up reversal == true
                    df.iat[i, up_reversal] = True #set up reversal = True
                    df.iat[i, swing_direction] = 'Down' #set swing direction = down
                    df.iat[i, swing_low] = df.iat[i, low] #set swing low = today's low
                elif (df.iat[i-1, swing_high] - df.iat[i, low]) <= filter_value: #elif up reversal == False
                    df.iat[i, up_reversal] = False
                    df.iat[i, swing_direction] = 'Up'
                    df.iat[i, swing_high] = df.iat[i-1, swing_high]
                
        if df.iat[i-1, swing_direction] == 'Down':
            if df.iat[i, low] <= df.iat[i-1, swing_low]: #if today's low <= yesterday's swing low
                df.iat[i, swing_low] = df.iat[i, low] #set swing low = today's low
                df.iat[i, swing_direction] = 'Down' #set swing direction = down
            
            elif df.iat[i, low] > df.iat[i-1, swing_low]: #elif today's low > yesterday's swing low
                if (df.iat[i, high] - df.iat[i-1, swing_low]) > filter_value #if down reversal == true
                    df.iat[i, down_reversal] = True #set down reversal = True
                    df.iat[i, swing_direction] = 'Up' #set swing direction = up
                    df.iat[i, swing_high] = df.iat[i, high] #set swing high = today's high
                if (df.iat[i, high] - df.iat[i-1, swing_low]) < filter_value #elif down reversal == false
                    df.iat[i, down_reversal] = False #set down reversal = false
                    df.iat[i, swing_direction] = 'Down' #set swing direction = down
                    df.iat[i, swing_low] = df.iat[i-1, swing_low] #set swing low = yesterday's swing low
    
        df.iat[i, swing_price] = math.max(df.iat[i, swing_low], df.iat[i, swing_high])
    
    df_swing = df['Date', 'Swing Price'][df['Swing Price' != None]]
    
    return df_swing


# In[3]:


spx = pd.read_csv('SP500_daily_test_data.csv')
pd.to_datetime(spx['Date'])
spx.set_index('Date', inplace=True)
spx.sort_index(ascending=True, inplace=True)


# In[4]:


spx.head()
#spx.set_index('Date', inplace=True)
#spx.sort_index(ascending=True)


# In[14]:


spx_swing = swing_chart_dollar_filter(spx, 100)


# In[16]:


len(spx['Close'])


# In[11]:


value = spx.iat([3])


# In[12]:


value


# In[13]:


len(value)


# In[17]:


for row in spx.itertuples():
    print(row.Index)

