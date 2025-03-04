from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

contract = Stock('Reliance', 'NSE')
print(contract)


contract1 = Stock('AAPL', 'NYSE')
print(contract1)

contract2= Crypto('BTC','PAXOS')
print(contract2)

contract3= Index('NIFTY50','NSE')
print(contract3)

contract4= Future('NIFTY50','20240229','NSE')
print(contract4)

contract5= Option('NIFTY50','20240229',21700,'C','NSE')
print(contract5)

bars = ib.reqHistoricalData(
    contract2, endDateTime='', durationStr='30 D',
    barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)

# convert to pandas dataframe (pandas needs to be installed):
df = util.df(bars)
print(df)