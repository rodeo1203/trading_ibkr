import asyncio
from ib_insync import *
import datetime as dt
import pandas_ta as ta
import pandas as pd
import sys



ib = IB()
# util.patchAsyncio()
ib.connect("127.0.0.1", 7497, clientId=20)  # Replace with your connection details

import logging
logging.basicConfig(level=logging.INFO, filename=f'strategy_{dt.date.today()}',filemode='w',format="%(asctime)s - %(message)s")
import requests
TOKEN = '6667240866:AAGoy-IGbUsiCeQXn8_-CDLDRPlJQzIad3k'
ids = '5563890177'



import os

# Specify the path to the file you want to check
file_path = '/Users/algo trading/interactive_broker_2024' + '/order_filled_list1.csv'

# Check if the file exists
if os.path.exists(file_path):
    order_filled_dataframe=pd.read_csv('order_filled_list1.csv')
    order_filled_dataframe.set_index('time',inplace=True)
else:
    column_names = ['time','ticker','price','action','type','order_id']
    order_filled_dataframe = pd.DataFrame(columns=column_names)
    order_filled_dataframe.set_index('time',inplace=True)













tickers=['BANKNIFTY']


quantity_tickers={'BANKNIFTY':15,'NIFTY50':50}


latest_price={}
contract_objects={}
all_cont_df={}
option_live_data={}
option_contract_data={}
order_filled_list=[]
for tick in tickers:
    contract_objects[tick]=ib.qualifyContracts(Index(tick,'NSE','INR'))[0]

print(contract_objects)



def get_nearest_weekly_expiry(name='NIFTY50'):
    # c=Contract(secType='OPT',symbol=name,exchange='NSE')
    # df=util.df(ib.reqContractDetails(c))
    df=all_cont_df[name]
    df['nexpiry']=pd.to_datetime(df['realExpirationDate']).dt.date
    df=df.sort_values(by=['nexpiry'])
    df=df[df['nexpiry']>=dt.date.today()]
    input_date=df['nexpiry'].iloc[0]
    return input_date

def get_next_to_nearest_weekly_expiry(name='NIFTY50'):
    # c=Contract(secType='OPT',symbol=name,exchange='NSE')
    # df=util.df(ib.reqContractDetails(c))
    df=all_cont_df[name]
    df['nexpiry']=pd.to_datetime(df['realExpirationDate']).dt.date
    df=df.sort_values(by=['nexpiry'])
    df=df[df['nexpiry']>=dt.date.today()]
    input_date=df['nexpiry'].value_counts().sort_index().index[1]
    return input_date

def get_current_month_last_expiry(name='NIFTY50'):
    # c=Contract(secType='OPT',symbol=name,exchange='NSE')
    # df=util.df(ib.reqContractDetails(c))
    df=all_cont_df[name]
    df['nexpiry']=pd.to_datetime(df['realExpirationDate']).dt.date
    df=df.sort_values(by=['nexpiry'])
    df=df[df['nexpiry']>=dt.date.today()]
    input_date=df['nexpiry'].iloc[0]
    if input_date.month == 12:  # If December, roll over to January of the next year
        first_day_next_month = dt.date(input_date.year + 1, 1, 1)
    else:
        first_day_next_month = dt.date(input_date.year, input_date.month + 1, 1)
    d=df[first_day_next_month>df['nexpiry']]['nexpiry'].iloc[-1]
    return d

def get_next_month_first_week_expiry(name='NIFTY50'):
    # c=Contract(secType='OPT',symbol=name,exchange='NSE')
    # df=util.df(ib.reqContractDetails(c))
    df=all_cont_df[name]
    df['nexpiry']=pd.to_datetime(df['realExpirationDate']).dt.date
    df=df.sort_values(by=['nexpiry'])
    df=df[df['nexpiry']>=dt.date.today()]
    input_date=df['nexpiry'].iloc[0]
    if input_date.month == 12:  # If December, roll over to January of the next year
        first_day_next_month = dt.date(input_date.year + 1, 1, 1)
    else:
        first_day_next_month = dt.date(input_date.year, input_date.month + 1, 1)
    d=df[first_day_next_month<df['nexpiry']]['nexpiry'].iloc[0]
    return d

def get_next_month_last_week_expiry(name='NIFTY50'):
    # c=Contract(secType='OPT',symbol=name,exchange='NSE')
    # df=util.df(ib.reqContractDetails(c))
    df=all_cont_df[name]
    df['nexpiry']=pd.to_datetime(df['realExpirationDate']).dt.date
    df=df.sort_values(by=['nexpiry'])
    df=df[df['nexpiry']>=dt.date.today()]
    input_date=df['nexpiry'].iloc[0]
    if input_date.month == 12:  # If December, roll over to January of the next year
        first_day_next_month = dt.date(input_date.year + 1, 1, 1)
    else:
        first_day_next_month = dt.date(input_date.year, input_date.month + 1, 1)

    # Calculate the last day of the next month by moving to the first day of the month after and subtracting one day
    if first_day_next_month.month == 12:  # If next month is December, the month after is January of the next year
        last_day_next_month = dt.date(first_day_next_month.year + 1, 1, 1) - dt.timedelta(days=1)
    else:
        last_day_next_month = dt.date(first_day_next_month.year, first_day_next_month.month + 1, 1) - dt.timedelta(days=1)
    d=df[last_day_next_month>df['nexpiry']]['nexpiry'].iloc[-1]
    return d

def get_atm_option(name,expiry,right='C'):
    t=ib.reqTickers(Index(name,'NSE','INR'))
    underlying_price=t[0].last
    # c=Contract(secType='OPT',symbol=name,exchange='NSE')
    # df=util.df(ib.reqContractDetails(c))
    df=all_cont_df[name]
    df['nexpiry']=pd.to_datetime(df['realExpirationDate']).dt.date
    df['strikes']=[i.strike for i in df['contract']]
    df['right']=[i.right for i in df['contract']]
    df=df[df['nexpiry']==expiry]
    df=df[df['right']==right]
    closest_index = (df['strikes'] - underlying_price).abs().idxmin()
    closest_number = df.loc[closest_index, 'strikes']
    closest_contract=df.loc[closest_index, 'contract']
    return closest_contract

def get_otm_option(name,expiry,right='C',points=100):
    t=ib.reqTickers(Index(name,'NSE','INR'))
    underlying_price=t[0].last
    if right=='C':
        underlying_price=underlying_price+points
    else:
        underlying_price=underlying_price-points

    # c=Contract(secType='OPT',symbol=name,exchange='NSE')
    # df=util.df(ib.reqContractDetails(c))
    df=all_cont_df[name]
    df['nexpiry']=pd.to_datetime(df['realExpirationDate']).dt.date
    df['strikes']=[i.strike for i in df['contract']]
    df['right']=[i.right for i in df['contract']]
    df=df[df['nexpiry']==expiry]
    df=df[df['right']==right]
    print(df)
    print(underlying_price)
    closest_index = (df['strikes'] - underlying_price).abs().idxmin()
    closest_number = df.loc[closest_index, 'strikes']
    closest_contract=df.loc[closest_index, 'contract']
    return closest_contract

def get_itm_option(name,expiry,right='C',points=100):
    t=ib.reqTickers(Index(name,'NSE','INR'))
    underlying_price=t[0].last
    if right=='C':
        underlying_price=underlying_price-points
    else:
        underlying_price=underlying_price+points

    # c=Contract(secType='OPT',symbol=name,exchange='NSE')
    # df=util.df(ib.reqContractDetails(c))
    df=all_cont_df[name]
    df['nexpiry']=pd.to_datetime(df['realExpirationDate']).dt.date
    df['strikes']=[i.strike for i in df['contract']]
    df['right']=[i.right for i in df['contract']]
    df=df[df['nexpiry']==expiry]
    df=df[df['right']==right]
    closest_index = (df['strikes'] - underlying_price).abs().idxmin()
    closest_number = df.loc[closest_index, 'strikes']
    closest_contract=df.loc[closest_index, 'contract']
    return closest_contract



#order handler
def order_open_handler(order):
    global order_filled_dataframe
    if order.orderStatus.status=='Filled':
        print('order filled')
        logging.info('order filled')
        name=order.contract.localSymbol
        a=[name,order.orderStatus.avgFillPrice,order.order.action,type(order.order),order.order.orderId]
        # if name not in order_filled_dataframe.ticker.to_list():
        order_filled_dataframe.loc[order.fills[0].execution.time] = a
        order_filled_dataframe.to_csv('order_filled_list.csv')
        message=order.contract.localSymbol+" "+order.order.action+"  "+str(order.orderStatus.avgFillPrice)
        logging.info(message)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ids}&parse_mode=Markdown&text={message}"
        requests.get(url).json()

#getting stock price
def get_index_price(ticker):
    t=ib.reqTickers(contract_objects[ticker])
    price=t[0].last
    return price

#closing all open orders
def close_all_orders():
    logging.info('closing all open orders')
    orders = ib.openOrders()
    for order in orders:
        logging.info(order)
        a=ib.cancelOrder(order)
        logging.info(a)
    return 1

#closing all the open positions
def close_all_position():
    positions = ib.positions()  # A list of positions, according to IB
    logging.info(positions)
    for position in positions:
        logging.info(position)
        print(position)
        n = position.contract.symbol
        contract = Contract(conId=position.contract.conId,exchange='NSE',currency='INR')
        print(contract)
        # c=ib.qualifyContracts(contract)[0]
        if position.position > 0: # Number of active Long positions
            action = 'Sell' # to offset the long positions
        elif position.position < 0: # Number of active Short positions
            action = 'Buy' # to offset the short positions
        totalQuantity = abs(position.position)
        logging.info(f'Flatten Position: {contract} {totalQuantity} {action}')
        order = MarketOrder(action=action, totalQuantity=totalQuantity)
        trade = ib.placeOrder(contract, order)
        logging.info(trade)

    return 1


print('calculation option data')
logging.info('calculation option data')
c=Contract(secType='OPT',symbol=tickers[0],exchange='NSE')
all_cont_df={}
all_cont_df[tickers[0]]=util.df(ib.reqContractDetails(c))
print(all_cont_df)

expiry=get_nearest_weekly_expiry(tickers[0])
print(expiry)
call_option=get_otm_option(tickers[0],expiry,right='C',points=100)
contract_objects[call_option.localSymbol]=call_option
put_option=get_otm_option(tickers[0],expiry,right='P',points=100)
contract_objects[put_option.localSymbol]=put_option
print(call_option,put_option)

print(contract_objects)
#updating option_live_data dictionary
for i,j  in contract_objects.items():
    quantity=all_cont_df
    option_live_data[i]={'traded':0,'stoplossobject':0,'lastprice':0,'stopprice':0,'hist_data_flag':0,'right':i[-2],'profit_constant':0,'stop_loss_constant':0,'first_time':True,'stop_order_filled':0,'price_during_trade':0}

print(option_live_data)
logging.info(option_live_data)





hours=10
minutes=0
start_time=dt.datetime(hour=hours,minute=minutes,second=1,year=2023,month=1,day=1).time()
before_start_time=dt.datetime(hour=hours,minute=minutes-2,second=40,year=2023,month=1,day=1).time()
end_time=dt.datetime(hour=15,minute=25,second=1,year=2023,month=1,day=1).time()
after_end_time=dt.datetime(hour=15,minute=25,second=10,year=2023,month=1,day=1).time()
trades=open('trades.csv','w')   



#buying all the options at market price
def buystocks(name,price):
    global option_live_data
    last_price=price
    logging.info('buying stocks'+ name +'at '+str(last_price))
    if option_live_data[name]['traded']==0:
        c=contract_objects[name]
        q=15
        parent = Order(orderId=ib.client.getReqId(),action='SELL',orderType='LMT',totalQuantity=q,lmtPrice=price,transmit = False)
        stopLoss = Order()
        stopLoss.orderId = ib.client.getReqId()
        stopLoss.action = "SELL" if parent.action == "BUY" else "BUY"
        stopLoss.orderType = "TRAIL"
        stopLoss.totalQuantity = parent.totalQuantity
        stopLoss.trailingPercent = 25
        stopLoss.trailStopPrice = int(last_price*1.25)
        stopLoss.parentId = parent.orderId
        stopLoss.transmit = True


        ords=[parent, stopLoss]

        for o in ords:
            trade=ib.placeOrder(c, o)
            print(trade)


        print("buying stocks$$$$$$$")
        option_live_data[name]['traded']  =1
        option_live_data[name]['stopprice']=int(last_price*1.30)
        option_live_data[name]['stoplossobject']=stopLoss 
        option_live_data[name]['price_during_trade']=last_price
        logging.info(c)
        logging.info(parent)
        logging.info(stopLoss)
        logging.info('buying stocks completed ')
    print(option_live_data)
    logging.info(option_live_data)


flag=0
#real time data handler
first_time=True
def pending_tick_handler(t):
    global option_live_data
    global flag
    global order_filled_list
    t=list(t)[0]
    times=t.time.replace(tzinfo=dt.timezone.utc).astimezone(tz=None)
    name=t.contract.localSymbol 
    oi=t.callOpenInterest+t.putOpenInterest if t.callOpenInterest+t.putOpenInterest else 0
    volume=t.volume if t.volume else 0
    iv=t.modelGreeks.impliedVol if t.modelGreeks.impliedVol else 0
    delta=t.modelGreeks.delta if t.modelGreeks.delta else 0 
    price=t.last if t.last else 0
    gamma=t.modelGreeks.gamma if t.modelGreeks.gamma else 0
    vega=t.modelGreeks.vega if t.modelGreeks.vega else 0
    theta=t.modelGreeks.theta if t.modelGreeks.theta else 0
    logging.info([name,price,oi,volume,iv,delta,price,gamma,vega,theta])
    print([name,price,oi,volume,iv,delta,price,gamma,vega,theta])

    option_live_data[name]['lastprice']=price
    print(option_live_data)
    #check if stop order is filled:
    # if option_live_data[name]['traded']==1 :
    #     if order_filled_list:
    #         for i in order_filled_list:
    #             if option_live_data[name]['stoplossobject'].orderId==i[-1]:
    #                 option_live_data[name]['stop_order_filled']=1





    now_minute = dt.datetime.now().minute
    #buying stock at 9:30
    if dt.datetime.now().time()>start_time and option_live_data[name]['traded']==0:  #and name not in [i.localSymbol for i in util.df(ib.positions()).contract]: 
        if price is not None:
            logging.info('buy stocks')
            buystocks(name,price)




    #closing all position at 3:30  
    if dt.datetime.now().time()>end_time and  flag==0:
        flag=close_all_position()
        close_all_orders()
        logging.info('sell stocks')



    if dt.datetime.now().time()>=after_end_time:
        trades.close()
        ib.disconnect()
        sys.exit()










for i,j  in option_live_data.items():
    cont=contract_objects[i]
    print(cont)
    market_data=ib.reqMktData(cont, "100, 101, 104", False, False)
    ib.sleep(2)  
    ib.pendingTickersEvent += pending_tick_handler
    ib.openOrderEvent += order_open_handler



ib.run()

