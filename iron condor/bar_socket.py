from ib_insync import *


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=14)


def onBarUpdate(bars, hasNewBar):
    print(bars)
    print(hasNewBar)

contract2=Crypto('BTC','PAXOS','USD')
bars = ib.reqRealTimeBars(contract2, 5, 'TRADES', False)
bars.updateEvent += onBarUpdate

# ib.sleep(30)
# ib.cancelRealTimeBars(bars)
ib.run()