**Demo Momentum code**

#Import all required libraries
import yfinance as yf
import pandas as pd
from datetime import timedelta
from datetime import date

from google.colab import drive
drive.mount('/content/drive')

#Read ticker data from Google drive
tickers = pd.read_csv('/content/drive/My Drive/Momentum/ind_niftytotalmarket_list.csv')

tickers['NSSymbol'] = tickers['Symbol']+".NS"

tickers

tickers = ['TATAMOTORS.NS','POLYCAB.NS']
start_date = date.today()-timedelta(weeks=52)
end_date = date.today()-timedelta(weeks=4)

stock_data = []

for ticker in tickers:
    raw_data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    raw_data['Symbol'] = ticker
    stock_data.append(raw_data)

stock_data = pd.concat(stock_data)

stock_data.reset_index(inplace=True)

stock_data

# Calculate week start date
stock_data['WeekStartDate'] = stock_data['Date'] - pd.to_timedelta(stock_data['Date'].dt.dayofweek, unit='D')

# Calculate week day number
stock_data['WeekDayNumber'] = stock_data['Date'].dt.weekday

# Group by 'Date' and 'WeekStartDate', and select the maximum 'WeekDayNumber' within each group
grouped_df = stock_data.groupby(['Symbol','WeekStartDate'])['WeekDayNumber'].max().reset_index()

#Merge to get the close for max week day number
friday_close_data = pd.merge(stock_data, grouped_df, on=['Symbol', 'WeekStartDate', 'WeekDayNumber'], how='inner')

friday_close_data

# Calculate the stock price four weeks ago for each date
friday_close_data['FourWeeksAgo'] = friday_close_data['WeekStartDate'] - pd.DateOffset(weeks=4)

# Perform a join operation to get the stock price four weeks ago
momentum_data = friday_close_data.merge(friday_close_data[['WeekStartDate','Symbol', 'Close']], left_on=['Symbol','FourWeeksAgo'], right_on=['Symbol','WeekStartDate'],
                                              suffixes=('', '_FourWeeksAgo'), how='left')

# Calculate the momentum for every week
momentum_data['Momentum'] = 1+((momentum_data['Close'] - momentum_data['Close_FourWeeksAgo']) /
                                            momentum_data['Close_FourWeeksAgo'])

mom_by_ticker = momentum_data.groupby(['Symbol'])['Momentum'].agg('prod')
mom_by_ticker = mom_by_ticker-1

mom_by_ticker = mom_by_ticker.reset_index()

mom_by_ticker

# Calculate the stock price four weeks ago for each date
friday_close_data['OneWeekAgo'] = friday_close_data['WeekStartDate'] - pd.DateOffset(weeks=1)

# Perform a join operation to get the stock price four weeks ago
momentum_data = friday_close_data.merge(friday_close_data[['WeekStartDate','Symbol', 'Close']], left_on=['Symbol','OneWeekAgo'], right_on=['Symbol','WeekStartDate'],
                                              suffixes=('', '_OneWeekAgo'), how='left')

# Calculate the smoothness for every week
momentum_data['Smoothness'] = momentum_data['Close'] - momentum_data['Close_OneWeekAgo']

momentum_data

#Get smoothness by ticker
smo_by_ticker = momentum_data.groupby('Symbol').agg(
    Smoothness=('Smoothness', lambda x: (x > 0).sum() / (len(x)-1))
)

smo_by_ticker

#Combine both momentum and smoothness datasets
momentum_smooth_by_ticker = mom_by_ticker.merge(smo_by_ticker, on='Symbol', how='inner')

momentum_smooth_by_ticker

momentum_smooth_by_ticker.to_excel('/content/drive/MyDrive/Momentum/momentum_smooth_by_ticker.xlsx', index=False)
