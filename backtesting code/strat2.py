from backtesting import Strategy, Backtest
import yfinance as yf
import pandas_ta as ta

def sma(close_data,period):
    return ta.sma(close_data,length=period)

def bbands(close,n):
    b=ta.bbands(close,length=n)
    return b[f'BBL_{n}_2.0'],b[f'BBU_{n}_2.0']

class bollingerband(Strategy):
    n=20
    # stop_number=0.95
    def init(self):
        # self.sma20=self.I(sma,self.data.Close.s,20)
        # self.sma50=self.I(sma,self.data.Close.s,50)
        # self.sma200=self.I(sma,self.data.Close.s,200)
        self.lower,self.upper=self.I(bbands,self.data.Close.s,self.n)


    def next(self):
        if self.lower[-1]>self.data.Close[-1] :
            self.buy()
        elif self.upper[-1]<self.data.Close[-1]  :
            self.position.close()



data=yf.download("RELIANCE.NS",start="2017-01-01",end="2023-04-30")
print(data)
data=data['2021-08-24':]
print(bbands(data["Close"],20))
bt=Backtest(data,bollingerband,cash=100000)
output=bt.run()
print(output)
print(output['_trades'])
bt.plot()

l1=list(range(5,50,2))
stats=bt.optimize(n=l1,maximize='Return [%]')
print(stats)
print(stats['_strategy'])
bt.plot()
