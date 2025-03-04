import asyncio
from ib_insync import *
import datetime
import pandas_ta as ta
import pandas as pd
import sys



ib = IB()
# util.patchAsyncio()
ib.connect("127.0.0.1", 7497, clientId=20)  # Replace with your connection details

import logging
logging.basicConfig(level=logging.INFO, filename=f'strategy_{datetime.date.today()}',filemode='w',format="%(asctime)s - %(message)s")
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

global macd_xover,renko_param,latest_price

tickers=['BTC','ETH']



latest_price={}
macd_xover = {}
renko_param = {}
contract_objects={}
for tick in tickers:
    contract_objects[tick]=ib.qualifyContracts(Crypto(tick,'PAXOS'))[0]

print(contract_objects)

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



def macd_xover_refresh(macd,ticker):
    global macd_xover
    if macd['MACD'].iloc[-1].squeeze()>macd['Signal'].iloc[-1].squeeze():
        macd_xover[ticker]="bullish"
    elif macd['MACD'].iloc[-1].squeeze()<macd['Signal'].iloc[-1].squeeze():
        macd_xover[ticker]="bearish"
    print("*****************************************")


def renkoOperation(ticker,last_price): 
    global renko_param           
    if renko_param[ticker]["upper_limit"] == None:
        renko_param[ticker]["upper_limit"] = float(last_price) + renko_param[ticker]["brick_size"]
        renko_param[ticker]["lower_limit"] = float(last_price) - renko_param[ticker]["brick_size"]
    if float(last_price) > renko_param[ticker]["upper_limit"]:
        gap = (float(last_price - renko_param[ticker]["upper_limit"]))//renko_param[ticker]["brick_size"]
        renko_param[ticker]["lower_limit"] = renko_param[ticker]["upper_limit"] + ((gap-1)*renko_param[ticker]["brick_size"])
        renko_param[ticker]["upper_limit"] = renko_param[ticker]["upper_limit"] + ((1+gap)*renko_param[ticker]["brick_size"])
        renko_param[ticker]["brick"] = max(1,renko_param[ticker]["brick"]+(1+gap))
    if float(last_price) < renko_param[ticker]["lower_limit"]:
        gap = (renko_param[ticker]["lower_limit"] - float(last_price))//renko_param[ticker]["brick_size"]
        renko_param[ticker]["upper_limit"] = renko_param[ticker]["lower_limit"] - ((gap-1)*renko_param[ticker]["brick_size"])
        renko_param[ticker]["lower_limit"] = renko_param[ticker]["lower_limit"] - ((1+gap)*renko_param[ticker]["brick_size"])
        renko_param[ticker]["brick"] = min(-1,renko_param[ticker]["brick"]-(1+gap))
    print(f"{ticker}: brick number = {renko_param[ticker]['brick']},last price ={last_price}, upper bound ={renko_param[ticker]['upper_limit']}, lower bound ={renko_param[ticker]['lower_limit']}")




def pending_tick_handler(t):
    global latest_price
    t=list(t)[0]
    times=t.time.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    name=t.contract.symbol 
    price=t.last if t.last else price
    latest_price[name]=price
    # print(name,times,price)
    # print(latest_price)
    renkoOperation(name,price)
    logging.info(name+str(price))

async def close_ticker_postion(name):
    p=await ib.reqPositionsAsync()
    df2=util.df(p)
    df2['ticker_name']=[cont.symbol for cont in df2['contract']]
    cont=df2[df2['ticker_name']==name].contract.iloc[0]
    quant=df2[df2['ticker_name']==name].position.iloc[0]
    quant
    if quant>0:
        #sell
        ord=MarketOrder(action='SELL',totalQuantity=quant)
        ib.placeOrder(cont,ord)
    elif quant<0:
        ord=MarketOrder(action='BUY',totalQuantity=abs(quant))
        ib.placeOrder(cont,ord)


async def close_ticker_open_orders(ticker):
    ord=ib.openTrades()

    df1=util.df(ord)
    print(df1)
    print(df1.columns)
    df1['ticker_name']=[cont.symbol for cont in df1['contract']]
    order_object=df1[df1['ticker_name']==ticker].order.iloc[0]
    print(order_object)
    ib.cancelOrder(order_object)




async def trade_buy_stocks(stock_name,stock_price):

    #market order
    contract = contract_objects[stock_name]
    ord=MarketOrder(action='BUY',totalQuantity=1)
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    print(trade)


    #trailing order
    order = Order()
    order.orderId = ib.client.getReqId()
    order.action = 'SELL'
    order.orderType = "TRAIL"
    order.totalQuantity = 1
    order.trailingPercent = 3
    order.trailStopPrice = int(stock_price*0.97)
    order.tif = 'GTC'
    trade=ib.placeOrder(contract, order)
    ib.sleep(1)



async def trade_sell_stocks(stock_name,stock_price):
    #market order
    contract = contract_objects[stock_name]
    ord=MarketOrder(action='SELL',totalQuantity=1)
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    print(trade)

    #trailing order
    order = Order()
    order.orderId = ib.client.getReqId()
    order.action = 'BUY'
    order.orderType = "TRAIL"
    order.totalQuantity = 1
    order.trailingPercent = 3
    order.trailStopPrice = int(stock_price*1.03)
    order.tif = 'GTC'
    trade=ib.placeOrder(contract, order)
    ib.sleep(1)




async def strategy(data,ticker):
    global renko_param,macd_xover,latest_price
    print('inside strategy')

    buy_condition=macd_xover[ticker] == "bullish" and renko_param[ticker]["brick"] >=2
    sell_condition=macd_xover[ticker] == "bearish" and renko_param[ticker]["brick"] <=-2
    a=await ib.accountSummaryAsync(account='DU8663685')
    current_balance=int(float([v for v in a if v.tag == 'AvailableFunds' ][0].value))
    if current_balance>latest_price[ticker]:
        if buy_condition:
            print('buy condiiton satisfied')
            await trade_buy_stocks(ticker,latest_price[ticker])
        elif sell_condition:
            print('sell condition satisfied')
            await trade_sell_stocks(ticker,latest_price[ticker])
        else :
            print('no condition satisfied')
    else:
        print('we dont have enough money')
        print('current balance is',current_balance,'stock price is ',data.close[-1])




async def request_historical_data(contract,interval,duration):
    bars =await ib.reqHistoricalDataAsync(
    contract, endDateTime='', durationStr=f'{duration} D',
    barSizeSetting=interval, whatToShow='MIDPOINT',useRTH=False,formatDate=1)
    df = util.df(bars)
    print(df)

    df['sma1']= ta.sma(df.close,10)
    df['sma2']= ta.sma(df.close,20)
    df['ema200']=ta.ema(df.close,200)
    output=ta.macd(df.close)
    df['MACD']=output[f'MACD_12_26_9']
    df['Signal']=output[f'MACDs_12_26_9']
    df['atr']=ta.atr(df.high,df.low,df.close)
    df.set_index('date',inplace=True)
    return df

async def strategy_code():
    # Your custom code here
    global tickers,renko_param,macd_xover,contract_objects
    print("inside main strategy")
    logging.info("inside main strategy")
    pos=await ib.reqPositionsAsync()
    print(pos)
    if len(pos)==0:
        pos_df=pd.DataFrame([])
    else:
        pos_df=util.df(pos)
        pos_df['name']=[cont.symbol for cont in pos_df['contract']]
        pos_df=pos_df[pos_df['position']>0]
    print(pos_df)
    logging.info(pos_df)
    ord=await ib.reqOpenOrdersAsync()
    if len(ord)==0:
        ord_df=pd.DataFrame([])
    else:
        ord_df=util.df(ord)
        print(ord_df)
    print(ord_df)
    logging.info(ord_df)

    for ticker in tickers:
        print('ticker name is',ticker,'################')
        ticker_contract=contract_objects[ticker]

        hist_df=await request_historical_data(ticker_contract,'15 mins',20)
        print(hist_df)
        logging.info(hist_df)
        a=await ib.accountSummaryAsync(account='DU8663685')
        logging.info(a)
        capital=int(float([v for v in a if v.tag == 'AvailableFunds' ][0].value))
        print(capital)
        logging.info(capital)
        quantity=int(capital/hist_df.close.iloc[-1])
        print(quantity)
        logging.info(quantity)
        logging.info('i got capital and quantituy')
        macd_xover_refresh(hist_df,ticker)
        logging.info('macd xover refresh')
        logging.info(macd_xover)
        logging.info(renko_param)
        print('renko parameter',renko_param[ticker])
        print('latest price',latest_price[ticker])
        t=util.df(ib.openTrades())
        logging.info(t)
        print('open trades',t)
        a=await ib.reqAllOpenOrdersAsync()
        t=util.df(a)
        logging.info(t)
        print('open open order',t)

        if quantity==0:
            print('we dont have enough money so we cannot trade')
            continue

        if pos_df.empty:
            print('we dont have any position')
            await strategy(hist_df,ticker)


        elif len(pos_df)!=0 and ticker not in pos_df['name'].tolist():
            print('we have some position but current ticker is not in position')
            await strategy(hist_df,ticker)
        elif len(pos_df)!=0 and ticker in pos_df["name"].tolist():
            print('we have some position and current ticker is in position')

            if pos_df[pos_df["name"]==ticker]["position"].values[0] == 0:
                print('we have current ticker in position but quantity is 0')
                await strategy(hist_df,ticker)

            elif pos_df[pos_df["name"]==ticker]["position"].values[0] > 0  :
                print('we have current ticker in position and is long')
                sell_condition=macd_xover[ticker] == "bearish" and renko_param[ticker]["brick"] <=-2
                a=await ib.accountSummaryAsync(account='DU8663685')
                current_balance=int(float([v for v in a if v.tag == 'AvailableFunds' ][0].value))

                if current_balance>hist_df.close.iloc[-1]:
                    if sell_condition:
                        print('sell condition satisfied')
                        await close_ticker_postion(ticker)
                        await close_ticker_open_orders(ticker)
                        await trade_sell_stocks(ticker,hist_df.close.iloc[-1])



            elif pos_df[pos_df["name"]==ticker]["position"].values[0] < 0 :
                print('we have current ticker in position and is short')
                buy_condition=buy_condition=macd_xover[ticker] == "bullish" and renko_param[ticker]["brick"] >=2
                a=await ib.accountSummaryAsync(account='DU8663685')
                current_balance=int(float([v for v in a if v.tag == 'AvailableFunds' ][0].value))
                if current_balance>hist_df.close.iloc[-1]:
                    if buy_condition:
                        print('buy condiiton satisfied')
                        await close_ticker_postion(ticker)
                        await close_ticker_open_orders(ticker)
                        await trade_buy_stocks(ticker,hist_df.close.iloc[-1])

            else:
                print('trail condition not met')



def start():
    for ticker in tickers:
        cont=contract_objects[ticker]
        bars =ib.reqHistoricalData(cont, endDateTime='', durationStr=f'15 D',
        barSizeSetting='5 mins', whatToShow='MIDPOINT',useRTH=False,formatDate=1)
        df = util.df(bars)
        print(df)
        df['atr']=ta.atr(df.high,df.low,df.close)
        renko_param[ticker] = {"brick_size":round(df.atr.iloc[-1].squeeze(),2),"upper_limit":None, "lower_limit":None,"brick":0}
        macd_xover[ticker] = None
        latest_price[ticker]=df.close.iloc[-1]
    print(macd_xover ,renko_param ) 





current_time=datetime.datetime.now()
#start time
start_hour,start_min=9,30
#end time
end_hour,end_min=15,30
current_time=datetime.datetime.now()
start_time=datetime.datetime(current_time.year,current_time.month,current_time.day,start_hour,start_min)
end_time=datetime.datetime(current_time.year,current_time.month,current_time.day,end_hour,end_min)
print(start_time)
print(end_time)


while True:
    if datetime.datetime.now()>start_time:
        break
    print(datetime.datetime.now())


start()

for tick in tickers:
    contract=contract_objects[tick]
    market_data=ib.reqMktData(contract, "", False, False)
    ib.pendingTickersEvent += pending_tick_handler
ib.newOrderEvent += order_open_handler
ib.orderStatusEvent += order_open_handler
ib.cancelOrderEvent += order_open_handler

candle_size=60

async def main():
    while datetime.datetime.now()<end_time:
        now = datetime.datetime.now()
        seconds_until_next_minute = candle_size - now.second+1
        print(seconds_until_next_minute)
        # Sleep until the end of the current minute
        await asyncio.sleep(seconds_until_next_minute)

        # Run your function
        await strategy_code()



ib.run(main())
