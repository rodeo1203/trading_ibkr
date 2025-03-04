

from backtesting import Strategy, Backtest
import yfinance as yf
import pandas_ta as ta
from backtesting.lib import resample_apply
import time
def ema(close_data,period=9):
    return ta.ema(close_data,length=period)

# def macd(close_data,period):
#     # output= ta.bbands(close_data,length=period)
#     output=ta.macd(close_data)
#     # return output[f'BBL_{period}_2.0'],output[f'BBU_{period}_2.0']
#     return output[f'MACD_12_26_9'],output[f'MACDs_12_26_9']

def supertrend1(high_data,low_data,close_data):
    o=ta.supertrend(high_data,low_data,close_data,length=10)
    return o['SUPERTd_10_3.0']
def supertrend2(high_data,low_data,close_data):
    o=ta.supertrend(high_data,low_data,close_data,length=10)
    return o['SUPERT_10_3.0']



class supertrend(Strategy):
    
    n1=9
    def init(self):
        self.super1=self.I(supertrend1,self.data.High.s,self.data.Low.s,self.data.Close.s)
        
        
        self.ema_hour=self.I(ema,self.data.Close.s,self.n1)
        # self.sma = resample_apply(
        #     'D', SMA, self.data.Close, 10, plot=False)
        self.daily_ema = resample_apply('D', ema,self.data.Close.s,self.n1)

    def next(self):
        print(self.data.index[-1],self.data.Close[-1],self.super1[-1],self.ema_hour[-1],self.daily_ema[-1])


        if self.super1[-1]>0 and self.data.Close[-1]> self.daily_ema[-1]:
            self.buy()

            # if self.position.is_short:
            #     self.position.close()
            #     self.buy()



            # elif not self.position:  
            #     self.buy()


        elif self.super1[-1]<0 and self.data.Close[-1]<self.daily_ema[-1]:
            self.position.close()
            # self.sell()



        

data=yf.download("^NSEBANK",interval='60m',start='2023-01-01',end='2024-02-24')
print(data)
print(supertrend2(data["High"],data["Low"],data["Close"]))
bt=Backtest(data,supertrend,cash=100000)
output=bt.run()
print(output)
print(output['_trades'].to_csv('trades.csv'))
bt.plot()

stats=bt.optimize(n1=range(10, 210, 10),maximize='Return [%]')
print(stats)
print(stats['_strategy'])
bt.plot()
