from backtesting import Backtest, Strategy
import pandas_ta as ta
import yfinance as yf

def sma(closing_price,leng):
    return ta.sma(closing_price,leng)



class SmaCross(Strategy):
    n1 = 20
    n2 = 50

    def init(self):
        close_data = self.data.Close.s
        self.sma20 = self.I(sma, close_data, self.n1)
        self.sma50 = self.I(sma, close_data, self.n2)

    def next(self):
        if self.sma20[-1]>self.sma50[-1] and self.sma20[-2]<self.sma50[-2]:
            if self.position.is_short:
                self.position.close()
            self.buy(size=1)
        if self.sma20[-1]<self.sma50[-1] and self.sma20[-2]>self.sma50[-2]:
            if self.position.is_long:
                self.position.close()
                self.sell(size=1)



data=yf.download('RELIANCE.NS',period='max')
data=data.loc['2019-01-01':]
print(data)
sma1=sma(data.Close,20)
print(sma1)

bt = Backtest(data, SmaCross,
              cash=3000, commission=.002,
              exclusive_orders=True)

output = bt.run()





# bt.plot()
print(output)
print(output['_trades'])
output['_trades'].to_csv('trades.csv')


l1=list(range(10,30,1))
l2=list(range(40,60,1))
print(l1)
print(l2)



stats=bt.optimize(n1=l1,n2=l2,maximize='Return [%]')
print(stats)
print(stats['_strategy'])
print(stats['_trades'])
bt.plot()