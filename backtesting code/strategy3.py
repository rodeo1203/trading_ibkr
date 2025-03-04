from backtesting import Strategy, Backtest
import yfinance as yf
import pandas_ta as ta


def ema(close_data,period):
    return ta.ema(close_data,length=period)


def macd(close_data,period):
    # output= ta.bbands(close_data,length=period)
    output=ta.macd(close_data)
    # return output[f'BBL_{period}_2.0'],output[f'BBU_{period}_2.0']
    return output[f'MACD_12_26_9'],output[f'MACDs_12_26_9']

class macd_s(Strategy):
    
    n1=200
    def init(self):
        self.macd,self.macds=self.I(macd,self.data.Close.s,50)
        self.ema200=self.I(ema,self.data.Close.s,self.n1)


    def next(self):
        if self.macd[-2]<self.macds[-2] and self.macd[-1]>self.macds[-1] and self.ema200[-1]<self.data.Close[-1]:
            if self.position.is_short:
                self.position.close()
                self.buy()
            elif not self.position:  
                self.buy()
        elif self.ema200[-1]>self.data.Close[-1]:
            self.position.close()
            # self.sell()
        

data=yf.download("^NSEI",start="2017-01-01",end="2023-04-30")
print(data)
print(macd(data["Close"],200))
bt=Backtest(data,macd_s,cash=100000)
output=bt.run()
print(output)
print(output['_trades'].to_csv('trades.csv'))
bt.plot()

# stats=bt.optimize(adx1=[3, 8, 1], sma20_1=[15, 25, 2],sma200_1=[150, 250, 10]
#                   )
stats=bt.optimize(n1=range(10, 210, 10),maximize='Return [%]')
print(stats)
print(stats['_strategy'])
bt.plot()
