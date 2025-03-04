import random
import time
import datetime
from ib_insync import *
import pandas_ta as ta
import pandas as pd
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=10)


tickers=['SBIN','KOTAKBANK']
capital=100


ticker_contracts={}
for tick in tickers:
    ticker_contracts[tick]=Stock(tick,'NSE','INR')



def stockprice(temp):
    a=ib.reqMktData(temp)
    util.sleep(1)
    price=a.last
    ib.cancelMktData(temp)
    return price


def get_historical_data(ticker_contract):
    bars = ib.reqHistoricalData(
    ticker_contract, endDateTime='', durationStr='1 D',
    barSizeSetting='1 min', whatToShow='TRADES', useRTH=True)
    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)
    df['sma1']=ta.sma(df.close,10)
    df['sma2']=ta.sma(df.close,20)
 
    return df


def close_ticker_postion(name):

    df2=util.df(ib.reqPositions())
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


def close_ticker_open_orders(ticker):
    ord=ib.reqAllOpenOrders()
    df1=util.df(ord)
    df1['ticker_name']=[cont.symbol for cont in df1['contract']]
    order_object=df1[df1['ticker_name']==ticker].order.iloc[0]
    print(order_object)
    ib.cancelOrder(order_object)



def trade_buy_stocks(stock_name,stock_price):
    #market order
    contract = ticker_contracts[stock_name]
    contract=ib.qualifyContracts(contract)[0]
    ord=MarketOrder(action='BUY',totalQuantity=1)
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    print(trade)

    #stop loss order


    order = Order()
    order.orderId = ib.client.getReqId()
    order.action = 'SELL'
    order.orderType = "TRAIL"
    order.totalQuantity = 1
    order.trailingPercent = 2
    order.trailStopPrice = int(stock_price*0.98)
    trade=ib.placeOrder(contract, order)
    ib.sleep(1)
    

def trade_sell_stocks(stock_name,stock_price):
    #market order
    contract = ticker_contracts[stock_name]
    contract=ib.qualifyContracts(contract)[0]
    ord=MarketOrder(action='SELL',totalQuantity=1)
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    print(trade)

    #stop loss order
    order = Order()
    order.orderId = ib.client.getReqId()
    order.action = 'BUY'
    order.orderType = "TRAIL"
    order.totalQuantity = 1
    order.trailingPercent = 2
    order.trailStopPrice = int(stock_price*1.02)
    trade=ib.placeOrder(contract, order)
    ib.sleep(1)

            


def strategy(data,ticker):
    print('inside strategy')
    print(ticker)
    print(data)
    
    buy_condition=data['sma1'].iloc[-1]>data['sma2'].iloc[-1] and data['sma1'].iloc[-2]<data['sma2'].iloc[-2]
    sell_condition=data['sma1'].iloc[-1]<data['sma2'].iloc[-1] and data['sma1'].iloc[-2]>data['sma2'].iloc[-2]
    current_balance=int(float([v for v in ib.accountValues() if v.tag == 'AvailableFunds' ][0].value))
    if current_balance>data.close.iloc[-1]:
        if buy_condition:
            print('buy condiiton satisfied')
            trade_buy_stocks(ticker,data.close.iloc[-1])
        elif sell_condition:
            print('sell condition satisfied')
            trade_sell_stocks(ticker,data.close.iloc[-1])
        else :
            print('no condition satisfied')
    else:
        print('we dont have enough money')
        print('current balance is',current_balance,'stock price is ',data.close[-1])


def main():
    ord_df=util.df(ib.reqOpenOrders())
    pos_df=util.df(ib.reqPositions())
    if pos_df is not None:
        pos_df['name']=[i.symbol for i in pos_df.contract ]
    else:
            pos_df=pd.DataFrame()
            pos_df['name']=0    

    print(pos_df)
    open_order_df=util.df(ib.openTrades())
    print(open_order_df)

    for ticker in tickers:
        print('ticker name is',ticker,'################')
        ticker_contract=ticker_contracts[ticker]
        ticker_contract=ib.qualifyContracts(ticker_contract)[0]
        hist_df=get_historical_data(ticker_contract)
        print(hist_df)
        print(hist_df.close.iloc[-1])
        capital=int(float([v for v in ib.accountValues() if v.tag == 'AvailableFunds' ][0].value))
        print(capital)
        quantity=int(capital/hist_df.close.iloc[-1])
        
        print(quantity)
        if quantity==0:
            print('we dont have enough money so we cannot trade')
            continue

        if pos_df.empty:
            print('we dont have any position')
            strategy(hist_df,ticker)


        elif len(pos_df)!=0 and ticker not in pos_df['name'].tolist():
            print('we have some position but current ticker is not in position')
            strategy(hist_df,ticker)
        elif len(pos_df)!=0 and ticker in pos_df["name"].tolist():
            print('we have some position and current ticker is in position')
            print(open_order_df)
            if pos_df[pos_df["name"]==ticker]["position"].values[0] == 0:
                print('we have current ticker in position but quantity is 0')
                strategy(hist_df,ticker)

            elif pos_df[pos_df["name"]==ticker]["position"].values[0] > 0  :
                print('we have current ticker in position and is long')
                sell_condition=hist_df['sma1'].iloc[-1]<hist_df['sma2'].iloc[-1] and hist_df['sma1'].iloc[-2]>hist_df['sma2'].iloc[-2]
                current_balance=int(float([v for v in ib.accountValues() if v.tag == 'AvailableFunds' ][0].value))
                if current_balance>hist_df.close.iloc[-1]:
                    if sell_condition:
                        print('sell condition satisfied')
                        close_ticker_postion(ticker)
                        close_ticker_open_orders(ticker)
                        trade_sell_stocks(ticker,hist_df.close.iloc[-1])
          


            elif pos_df[pos_df["name"]==ticker]["position"].values[0] < 0 :
                print('we have current ticker in position and is short')
                buy_condition=hist_df['sma1'].iloc[-1]>hist_df['sma2'].iloc[-1] and hist_df['sma1'].iloc[-2]<hist_df['sma2'].iloc[-2]
                current_balance=int(float([v for v in ib.accountValues() if v.tag == 'AvailableFunds' ][0].value))
                if current_balance>hist_df.close.iloc[-1]:
                    if buy_condition:
                        print('buy condiiton satisfied')
                        close_ticker_postion(ticker)
                        close_ticker_open_orders(ticker)
                        trade_buy_stocks(ticker,hist_df.close.iloc[-1])

main()

# current_time=datetime.datetime.now()
# print(current_time)

# print(datetime.datetime.now())

# #start time
# start_hour,start_min=9,30
# #end time
# end_hour,end_min=23,30
# start_time=datetime.datetime(current_time.year,current_time.month,current_time.day,start_hour,start_min)
# end_time=datetime.datetime(current_time.year,current_time.month,current_time.day,end_hour,end_min)
# print(start_time)
# print(end_time)

# while True:
#     if datetime.datetime.now()>start_time:
#         break
#     print(datetime.datetime.now())


# candle_size=60

# while datetime.datetime.now()<end_time:
#     now = datetime.datetime.now()
#     seconds_until_next_minute = candle_size - now.second+1

#     # Sleep until the end of the current minute
#     time.sleep(seconds_until_next_minute)

#     # Run your function
#     main()