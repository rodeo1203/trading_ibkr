from ib_insync import *


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=14)

contract1=Crypto('BTC','PAXOS','USD')
while True:
    data=ib.reqTickers(contract1)
    print(data[0].time,data[0].last)

#quote