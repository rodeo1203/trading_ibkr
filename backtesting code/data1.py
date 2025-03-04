#yfinance
# import yfinance as yf
# import datetime as dt
# end=dt.datetime.now()
# start=end-dt.timedelta(days=5*366)
# name=''
# df=yf.download('GOOG',start=start,end=end)
# print(df)



#interactive

from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=44)

# contract =Option(symbol='BANKNIFTY',lastTradeDateOrContractMonth='20240229',strike=44900,right='C',exchange='NSE')
# c=ib.qualifyContracts(contract)[0]
# print(c)


c=Crypto('BTC','PAXOS')
c=ib.qualifyContracts(c)[0]
print(c)


from datetime import datetime, timedelta
import pandas as pd
df_main=pd.DataFrame()

def get_last_day_of_month(year, month):
    # Start with the first day of the next month
    next_month = datetime(year, month, 1) + timedelta(days=31)
    # Subtract days one at a time until we reach the current month
    while next_month.month == month + 1:
        next_month -= timedelta(days=1)
    return next_month,next_month.day

no_of_year=1
for y in range(2023-no_of_year,2023+1,1):
    year=y
    for m in range(1,12):
        start=datetime(year,m,1)
        end,d=get_last_day_of_month(year, m)
        print(start)
        print(end)
        bars = ib.reqHistoricalData(
            c, endDateTime=end, durationStr=f'{d} D',
            barSizeSetting='5 mins', whatToShow='MIDPOINT', useRTH=True)

        # convert to pandas dataframe (pandas needs to be installed):
        df = util.df(bars)
        df=df.set_index('date')
        print(df)
        df_main=pd.concat([df_main,df],axis=0).drop_duplicates()




print(df_main)

#change column name
df_main.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume':'Volume'
}, inplace=True)
df_main=df_main.drop(['average','barCount'],axis=1)
df_main.to_csv('data2.csv')

# from backtesting import Backtest, Strategy
# from backtesting.lib import crossover, TrailingStrategy

# from backtesting.test import SMA, GOOG
# import pandas as pd

# class SmaCross(Strategy):
#     n1 = 10
#     n2 = 20
#     trailing_stop_loss = 0.09  # 2% trailing stop loss

#     def init(self):
#         super().init()  # Call parent class init method
#         close = self.data.Close
#         self.sma1 = self.I(SMA, close, self.n1)
#         self.sma2 = self.I(SMA, close, self.n2)
#         self.trail_price = 0

#     def next(self):
#         if crossover(self.sma1, self.sma2):
#             self.buy()
            
#             self.trail_price = self.data.Close[-1] * (1 - self.trailing_stop_loss)
#         elif crossover(self.sma2, self.sma1):
#             self.sell()
#             self.trail_price = self.data.Close[-1] * (1 + self.trailing_stop_loss)

#         if self.position:
#             if self.position.is_long:
#                 self.trail_price = max(self.trail_price, self.data.Close[-1] * (1 - self.trailing_stop_loss))
#                 if self.data.Close[-1] <= self.trail_price:
#                     self.position.close()
#             else:  # For short positions
#                 self.trail_price = min(self.trail_price, self.data.Close[-1] * (1 + self.trailing_stop_loss))
#                 if self.data.Close[-1] >= self.trail_price:
#                     self.position.close()

# # Load your data
# df_main = pd.read_csv('data.csv')
# print(df_main)

# # Setup and run the backtest
# bt = Backtest(GOOG, SmaCross, cash=10000000, commission=.002, exclusive_orders=True)

# output = bt.run()
# bt.plot()
# print(output)
