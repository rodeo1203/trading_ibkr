# from ib_insync import *


# ib = IB()
# ib.connect('127.0.0.1', 7497, clientId=14)


# import pandas as pd
# contract2=Crypto('BTC','PAXOS','USD')
# df = pd.DataFrame(
#     index=contract2.symbol,
#     columns=['bidSize', 'bid', 'ask', 'askSize', 'high', 'low', 'close'])

# def onPendingTickers(tickers):
#     # print(tickers)
#     t=list(tickers)[0]
#     print(t.time,t.last)

#     for t in tickers:
#         df.loc[t.contract.symbol] = (t.bidSize, t.bid, t.ask, t.askSize, t.high, t.low, t.close)
#     print(df)      


# market_data = ib.reqMktData(contract2,"",False,False)

# ib.pendingTickersEvent += onPendingTickers
# ib.sleep(20)
# ib.pendingTickersEvent -= onPendingTickers