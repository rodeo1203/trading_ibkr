from ib_insync import *


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=14)




def pending_tick(t):
    t=list(t)[0]
    print(t.contract.symbol,t.time,t.last)

contract2=Crypto('BTC','PAXOS','USD')
market_data=ib.reqMktData(contract2, "", False, False)
contract2=Crypto('ETH','PAXOS','USD')
market_data=ib.reqMktData(contract2, "", False, False)
ib.pendingTickersEvent += pending_tick
# ib.sleep(20)
# ib.pendingTickersEvent -= pending_tick
ib.run()


# {Ticker(contract=Crypto(symbol='BTC', exchange='PAXOS', currency='USD'), time=datetime.datetime(2024, 6, 9, 14, 19, 21, 316602, tzinfo=datetime.timezone.utc), minTick=0.25, bid=69518.25, bidSize=0.06465302, ask=69518.5, askSize=0.57919892, last=69518.25, lastSize=7.24e-06, prevBidSize=0.0399348, prevAskSize=0.56289828, prevLast=69518.5, prevLastSize=5.279e-05, volume=14.0, high=69756.0, low=69300.75, close=69230.25, halted=0.0)}
# {Ticker(contract=Crypto(symbol='BTC', exchange='PAXOS', currency='USD'), time=datetime.datetime(2024, 6, 9, 14, 19, 21, 316858, tzinfo=datetime.timezone.utc), minTick=0.25, bid=69518.25, bidSize=0.06465302, ask=69518.5, askSize=0.57919892, last=69518.25, lastSize=4.955e-05, prevBidSize=0.0399348, prevAskSize=0.56289828, prevLast=69518.5, prevLastSize=7.24e-06, volume=14.0, high=69756.0, low=69300.75, close=69230.25, halted=0.0, ticks=[TickData(time=datetime.datetime(2024, 6, 9, 14, 19, 21, 316858, tzinfo=datetime.timezone.utc), tickType=5, price=69518.25, size=4.955e-05)])}
