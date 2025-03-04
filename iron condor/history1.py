from ib_insync import *


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=14)


contract = Contract(secType='OPT',symbol='BANKNIFTY',lastTradeDateOrContractMonth='20240626',strike=49700,right='CALL',exchange='NSE',currency='INR')


bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='10 D',
        barSizeSetting='5 mins',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1)
print(bars)
# df = util.df(bars)
# print(df)