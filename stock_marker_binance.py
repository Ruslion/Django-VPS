import pandas as pd
from datetime import datetime, timedelta
import time

MAs=(3, 6, 12, 24, 48, 96, 192, 384)

# convert string to datetime object
UNIX_TIME_START = datetime.strptime('1970-01-01 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')

def sorting_timestamp(df):
    '''
    This function sorts dataframe by 'timeframe' column ascendingly.
    Input: df pandas dataframe
    Output: df processed pandas dataframe
    '''
    try:
        tmp  = df['timestamp']
    except KeyError as e:
        print(f'{e} field not found')
        return
        
    df.sort_values(by='timestamp') # Sorting by timestamp before iteration
    df['timestamp']=df['timestamp'].astype('datetime64[ns]')
    return df

def marking_buy_sell_actions(df, min_profit=3, drawdown = 1):
    '''
    This function marks stock price table with B - buy, S - sell, W - wait, H - hold marks.
    
    Input: df - pandas dataframe with stock price.
            float min_profit - minimum percent of profit desired. Default = 3%
            float drawdown - maximum of drawdown. Default = 5%
    
    Output: pandas dataframe with added column 'action' with the above mentioned marks.
    
    Note: input pandas dataframe should have "close", 'timestamp' columns.
    '''
    try:
        tmp  = df['timestamp']
    except KeyError as e:
        print(f'{e} field not found')
        return
    drawdown = drawdown/100
    min_profit = min_profit/100
    
    
    bottom = df['close'].iloc[0] # This variable stores local bottom price
    bottom_timestamp = df['timestamp'].iloc[0]
    peak = 0 # This variable stores local high price
    peak_timestamp = None
    buy_mode = None # To indicate buy mode and avoid excessive buy marks 
    
    
    df_marks =pd.DataFrame(df['timestamp'])
    df_marks['action'] = "" # Added new column.
    df_marks['action'] = df_marks['action'].astype('string') 
    
    # Iterating through the dataframe.
    for index, row in df.iterrows( ):
        if row['close'] > peak:
            peak = row['close']
            peak_timestamp = row['timestamp']
        if row['close'] < bottom:
            bottom = row['close']
            bottom_timestamp = row['timestamp']
        if row['close'] <= peak * (1-drawdown) and (buy_mode or buy_mode is None): # Max drawback found. Marking sell action at previous peak.
            df_marks.loc[df_marks['timestamp'] == peak_timestamp, 'action'] = 'S'
            bottom = row['close']
            peak = bottom
            bottom_timestamp = row['timestamp']
            peak_timestamp = bottom_timestamp
            buy_mode = False
            continue
        if row['close'] >= bottom * (1+min_profit) and (not buy_mode or buy_mode is None): # Min profit found. Marking buy action 
                                                                                # at previous bottom.
            df_marks.loc[df_marks['timestamp'] == bottom_timestamp, 'action'] = 'B'
            bottom = row['close']
            peak = bottom
            bottom_timestamp = row['timestamp']
            peak_timestamp = bottom_timestamp
            #print(f'Buy marked at {bottom_timestamp}' )
            buy_mode = True
    # Iteration complete.
    # Merging two dataframes together by 'timestamp' field.
    df_result = pd.merge(df, df_marks, on='timestamp')
    return df_result

def marking_adjacent_actions(df, signal_interval_tol = 5, signal_price_tol = 0.5):
    '''
    This function marks stock price table 'action' field with B - buy, S - sell marks
        of adjacent cells with actual Buy and Sell marks.
    
    Input: df - pandas dataframe with stock price.
            int signal_interval_tol - defines number of hours before and after signal when signal is valid. Default = 5 hours.
            float signal_price_tol - defines percent in price when signal is valid. Default = 0.5%
    
    Output: pandas dataframe with added column 'action' with the above mentioned marks.
    
    Note: input pandas dataframe should have "close", 'timestamp' columns.
    '''
    signal_price_tol = signal_price_tol/100
    lower_bound = 1 - signal_price_tol
    upper_bound = 1 + signal_price_tol

    df_action = df.loc[(df['action'] == 'B') | (df['action'] == 'S')]
    
    for index, row in df_action.iterrows( ):
        # Marking None action values with 'S' or 'B' if the following criteria are met.
        upper_bound_price = row['close'] * upper_bound
        lower_bound_price = row['close'] * lower_bound
        start_time = row['timestamp'] - timedelta(hours=signal_interval_tol)
        end_time = row['timestamp'] + timedelta(hours=signal_interval_tol)
        mask = ((df['timestamp']>=start_time) &
                (df['timestamp']<=end_time) &  # number of days earlier or later than signal date
               (df['close'] <= upper_bound_price) &
               (df['close'] >= lower_bound_price) & 
               (df['action'] == ""))
        df.loc[ mask, 'action'
              ] = row['action']
    return df

def marking_hold_wait_actions(df):
    '''
    This function marks stock price table with H - Hold, W - Wait marks.
    
    Input: df - pandas dataframe with stock price.
    
    Output: pandas dataframe with proccessed 'action' column.
    
    Note: input pandas dataframe should have "action", 'timestamp' columns.
    '''
    min_data_action = df.loc[df['action'] != "" ,'timestamp'].min() # Finding date with earliest action.
    
    if type(min_data_action) != pd._libs.tslibs.nattype.NaTType:
        buy_mode=df.loc[df['timestamp']==min_data_action, 'action'].iloc[0]
    else:
        buy_mode = None
    
    if buy_mode == 'B':
        buy_mode = True
    elif buy_mode == 'S':
        buy_mode = False
    
    
        
    df_action = df[['action', 'timestamp']]
    for index, row in df_action.iterrows():
        if row['action'] == "": # Empty action found
            if buy_mode:
                df.loc[index, 'action'] = 'H' # Latest action in the timestamps is BUY thus we assign Hold
                continue
            if not buy_mode:
                df.loc[index, 'action'] = 'W' # Latest action in the timestamps is SELL thus we assign Wait
                continue
                
        if row['action'] == 'B':
            buy_mode = True
            continue
        if row['action'] == 'S':
            buy_mode = False
            continue
    return df

def adding_MAs(df, col_label, MAs=MAs):
    '''
    This function adds different moving averages to the dataframe.

    Input: df - pandas dataframe with stock data.
            col_lable - the name of the column to calculate the MAs for.
    Output: df - process dataframe
    '''
    for period in MAs:
        df['MA'+ str(period) +'_' + col_label]=df[col_label].rolling(period).mean()
    
    return df

def adding_ratio(df, col_label, MAs=MAs):
    '''
    This function adds different ratios of col_label with moving averages to the dataframe.

    Input: df - pandas dataframe with stock data.
            col_lable - the name of the column to calculate the ratios for.
    Output: df - process dataframe
    '''
    for period in MAs:
        df['RATIO_'+ col_label + '_and_MA' + str(period)] = df[col_label] / df['MA'+ str(period) +'_' + col_label]

    return df

def renaming_cols(df, prefix, columns_to_exlude=[]):


    '''
    This function rename columns by adding prefix to them.

    Input: df - pandas dataframe.
            prefix - prefix to be added to the column name
            columns_to_exlude - list of strings, columns to exclude from renaming.
    Output: df - process dataframe
    '''
    cols = df.columns.tolist()
    cols_new = {}
    for item in cols:
        if item not in columns_to_exlude:
            cols_new[item]=prefix+item
        else:
            cols_new[item]=item
    df.rename(columns =cols_new, inplace=True)
    return df

def import_stock_data(symbol, interval,  startTime=None, endTime=None, limit=500):

    '''
    This function retrive data from the third party API service and return as pandas dataframe.
    Input: ticker as string.
            output_size as string. Can be only two values 'full' or 'compact'
            data_type as string. Can be only one of the two values 'csv' or 'json'
    Output: pandas dataframe with the stock's data.
    '''
    
    url = 'https://api3.binance.com/api/v3/klines?symbol=' + \
        symbol + '&interval='+ \
        interval
    if startTime != None:
        url=url + '&startTime=' + str(startTime)
    
    if endTime != None:
        url=url + '&endTime=' + str(endTime)

    url = url + '&limit=' + str(limit)

    i = 5
    df = pd.read_json(url)
    while len(df)==0:
        time.sleep(i)
        df = pd.read_json(url)
        i=i*2
        if i > 300:
            i=300
        print('i = ', i)
        

    df[0]= df[0].apply (lambda x: UNIX_TIME_START + timedelta(milliseconds=x))
    return df

def volume_by_close(df):
    '''Created column which is volume multiplied by adjusted close price
    Input: pandas dataframe
    Output: pandas dataframe
    '''
    df['volume_by_close'] = df['volume']* df['close']
    return df

def rsi(df, col_label, MAs=MAs):
    '''
    This function adds different RSI values to the dataframe based on the list of periods.

    '''
    for period in MAs:
        delta = df[col_label].diff()
        delta = delta[1:]
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        AVG_Gain = up.rolling(period).mean()
        AVG_Loss = abs(down.rolling(period).mean())
        RS = AVG_Gain/AVG_Loss
        df['RSI_'+ str(period)] = 100.0 - (100.0 / (1.0 + RS))
    return df