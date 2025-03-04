from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
import pandas as pd

class ORBStrategy(Strategy):
    def init(self):
        
        self.orb_high = None
        self.orb_low = None
        self.trade=0


    def next(self):
        if len(self.data) < 2:
            return
        else:
            if self.data.index[-1].time() == pd.Timestamp('10:00').time():
                df=self.data.df
                d=self.data.index[-1]
                d=pd.to_datetime(d.date())
                df=df[df.index>d]
                self.orb_high = df.High.max()
                self.orb_low = df.Low.min()
                self.trade=0

        
            if not self.position and self.orb_high and self.orb_low:
                print('inside condition')
                if (self.data.Close[-1] > self.orb_high) and self.trade==0:
                    self.buy()
                    self.trade=1
                elif (self.data.Close[-1] < self.orb_low) and self.trade==0:
                    self.sell()
                    self.trade=1
            elif self.position:
                # Close position by the end of the day
                if self.data.index[-1].time() == pd.Timestamp('15:20').time():
                    self.position.close()
                print(self.position)

def fetch_data(symbol):
    data = pd.read_csv('data2.csv').head(1000)
   
    print(data)
    data = data.dropna()
    data['date'] = pd.to_datetime('date').tz_convert('UTC').tz_localize(None)
    data=data.set_index('date')
    print(data)
    data = data.between_time('09:30', '16:00')  # Focus on regular trading hours
    return data

# List of stock symbols to backtest
stocks = ['MSFT', 'GOOGL']

results = {}
for stock in stocks:
    data = fetch_data(stock)
    print(data)
    bt = Backtest(data, ORBStrategy, cash=10_000, commission=.002)
    stats = bt.run()
    results[stock] = stats
    bt.plot()

# Output the results
for stock, stats in results.items():
    print(f"{stock}:")
    print(stats)
