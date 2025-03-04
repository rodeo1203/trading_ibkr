from backtesting import Backtest, Strategy
from backtesting.lib import crossover, TrailingStrategy

from backtesting.test import SMA, GOOG
import pandas as pd

class SmaCross(Strategy):
    n1 = 10
    n2 = 20
    trailing_stop_loss = 0.02  # 2% trailing stop loss

    def init(self):
        super().init()  # Call parent class init method
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)
        self.trail_price = 0

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
            self.trail_price = self.data.Close[-1] * (1 - self.trailing_stop_loss)
        elif crossover(self.sma2, self.sma1):
            self.sell()
            self.trail_price = self.data.Close[-1] * (1 + self.trailing_stop_loss)

        if self.position:
            if self.position.is_long:
                self.trail_price = max(self.trail_price, self.data.Close[-1] * (1 - self.trailing_stop_loss))
                if self.data.Close[-1] <= self.trail_price:
                    self.position.close()
            else:  # For short positions
                self.trail_price = min(self.trail_price, self.data.Close[-1] * (1 + self.trailing_stop_loss))
                if self.data.Close[-1] >= self.trail_price:
                    self.position.close()

# Load your data
df_main = pd.read_csv('data.csv')
print(df_main)

# Setup and run the backtest
bt = Backtest(GOOG, SmaCross, cash=10000000, commission=.002, exclusive_orders=True)

output = bt.run()
bt.plot()
print(output)


s=[0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.10,0.11,0.12,0.13]


stats=bt.optimize(trailing_stop_loss=s,maximize='Return [%]')
print(stats)
print(stats['_strategy'])
print(stats['_trades'])
bt.plot()
