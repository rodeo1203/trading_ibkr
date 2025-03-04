
import datetime
import time
from ib_insync import *

import pandas as pd
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=96)

tickers=['SBIN','KOTAKBANK']
capital=100



def main_strategy_code():
    print("hello")
    # pos=ib.reqPositions()
    # if len(pos)==0:
    #     pos_df=pd.DataFrame([])
    # else:
    #     pos_df=util.df(pos)
    # print(pos_df)
    # ord=ib.reqAllOpenOrders()
    # if len(ord)==0:
    #     ord_df=pd.DataFrame([])
    # else:
    #     ord_df=util.df(ord)
    # print(ord_df)
    


current_time=datetime.datetime.now()
print(current_time)

print(datetime.datetime.now())

#start time
start_hour,start_min=16,6
#end time
end_hour,end_min=16,7
start_time=datetime.datetime(current_time.year,current_time.month,current_time.day,start_hour,start_min)
end_time=datetime.datetime(current_time.year,current_time.month,current_time.day,end_hour,end_min)
print(start_time)
print(end_time)

while True:
    if datetime.datetime.now()>start_time:
        break
    print(datetime.datetime.now())


candle_size=10


while datetime.datetime.now()<end_time:
    now = datetime.datetime.now()
    print(now)

    seconds_until_next_minute = candle_size 
    print(seconds_until_next_minute)
    # Sleep until the end of the current minute
    time.sleep(seconds_until_next_minute)

    # Run your function
    main_strategy_code()