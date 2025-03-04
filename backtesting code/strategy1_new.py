from backtesting import Backtest, Strategy
import pandas_ta as ta
import yfinance as yf
import time

def sma(closing_price,leng):
    return ta.sma(closing_price,leng)

def atr(h,l,c,leng):
     return ta.atr(h,l,c,leng)


class SmaCross(Strategy):
    n1 = 20
    n2 = 50
    # take_profit=1.05
    # stop_loss=0.99
    r1=14
    trailing_stop_loss = 0.03


    def init(self):
        close_data = self.data.Close.s
        self.sma20 = self.I(sma, close_data, self.n1)
        self.sma50 = self.I(sma, close_data, self.n2)
        self.atr=self.I(atr,self.data.High.s,self.data.Low.s,self.data.Close.s,self.r1)
        self.trail_price = 0

    def next(self):



        if self.sma20[-1]>self.sma50[-1] and self.sma20[-2]<self.sma50[-2]:
            if self.position.is_short or (not self.position):
                self.position.close()
                self.buy(tp=self.data.Close[-1]+self.atr[-1]*2)
                self.trail_price = self.data.Close[-1] * (1 - self.trailing_stop_loss)
                print(self.data.index[-1],self.data.Close[-1],self.atr[-1])
        if self.sma20[-1]<self.sma50[-1] and self.sma20[-2]>self.sma50[-2]:
            # if self.position.is_long or (not self.position):
                self.position.close()
                # self.sell(size=1)
        if self.position:
            if self.position.is_long:
                self.trail_price = max(self.trail_price, self.data.Close[-1] * (1 - self.trailing_stop_loss))
                if self.data.Close[-1] <= self.trail_price:
                    self.position.close()
            # else:  # For short positions
            #     self.trail_price = min(self.trail_price, self.data.Close[-1] * (1 + self.trailing_stop_loss))
            #     if self.data.Close[-1] >= self.trail_price:
            #         self.position.close()



data=yf.download('RELIANCE.NS',period='max')
data=data.loc['2018-01-01':]
print(data)
sma1=sma(data.Close,20)
print(sma1)

bt = Backtest(data, SmaCross,
              cash=3000, commission=.002,
              exclusive_orders=True)

output = bt.run()

bt.plot()



# bt.plot()
print(output)
print(output['_trades'])
output['_trades'].to_csv('trades.csv')

#what is overfitting

# l1=list(range(10,30,1))
# l2=list(range(40,60,1))
# print(l1)
# print(l2)
# t=[1.01,1.02,1.03,1.04,1.05,1.06,1.07,1.08,1.09]
# s=[0.99,0.98,0.97,0.96,0.95]


# stats=bt.optimize(take_profit=t,stop_loss=s,maximize='Return [%]')
# print(stats)
# print(stats['_strategy'])
# print(stats['_trades'])
# bt.plot()
s=[0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09]


stats=bt.optimize(trailing_stop_loss=s,maximize='Return [%]')
print(stats)
print(stats['_strategy'])
print(stats['_trades'])
bt.plot()