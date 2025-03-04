
import datetime
import time
from ib_insync import *
import pandas_ta as ta
import pandas as pd
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=208)

tickers=['SBIN','KOTAKBANK']
contract_objects={}
for tick in tickers:
    print(Stock(tick,'NSE','INR'))
    contract_objects[tick]=ib.qualifyContracts(Stock(tick,'NSE','INR'))[0]
print(contract_objects)

def get_historical_data(ticker_contract):
    bars = ib.reqHistoricalData(
    ticker_contract, endDateTime='', durationStr='10 D',
    barSizeSetting='1 min', whatToShow='MIDPOINT', useRTH=True)
    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)
    df['sma1']=ta.sma(df.close,20)
    df['sma2']=ta.sma(df.close,50)
    return df

def trade_buy_stocks(ticker,closing_price,quantitys=1):
    #market order
    contract = contract_objects[ticker]
    ord=MarketOrder(action='BUY',totalQuantity=quantitys)
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    print(trade)

    #stop loss order
    ord=StopOrder(action='SELL',totalQuantity=quantitys,stopPrice=int(0.98*closing_price))
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    print(trade)

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


def close_ticker_open_orders(ticker):
    ord=ib.reqAllOpenOrders()
    df1=util.df(ord)
    df1['ticker_name']=[cont.symbol for cont in df1['contract']]
    order_object=df1[df1['ticker_name']==ticker].order.iloc[0]
    print(order_object)
    ib.cancelOrder(order_object)

def trade_sell_stocks(ticker,closing_price,quantitys=1):
    #if i have any open orders cancel all of them
    close_ticker_open_orders(ticker)
    #if i have current postion close current postion
    close_ticker_postion(ticker)



def strategy(data,ticker):
    print('inside strategy')
    print(ticker)
    print(data)
    
    buy_condition=data['sma1'].iloc[-1]>data['sma2'].iloc[-1] and data['sma1'].iloc[-2]<data['sma2'].iloc[-2]
    # buy_condition=data['sma1'].iloc[-1]>data['close'].iloc[-1]
   
    current_balance=int(float([v for v in ib.accountValues() if v.tag == 'AvailableFunds' ][0].value))
    
    if current_balance>data.close.iloc[-1]:
        if buy_condition:
            print('buy condiiton satisfied')
            trade_buy_stocks(ticker,data.close.iloc[-1])
        else :
            print('no condition satisfied')
    else:
        print('we dont have enough money')
        print('current balance is',current_balance,'stock price is ',data.close[-1])




def main_strategy_code():
    print("inside main strategy")
    pos=ib.reqPositions()
    if len(pos)==0:
        pos_df=pd.DataFrame([])
    else:
        pos_df=util.df(pos)
        pos_df['name']=[cont.symbol for cont in pos_df['contract']]
        print(pos_df.info())
        pos_df=pos_df[pos_df['position']>0]
    print(pos_df)
    ord=ib.reqAllOpenOrders()
    if len(ord)==0:
        ord_df=pd.DataFrame([])
    else:
        ord_df=util.df(ord)
        ord_df['name']=[cont.symbol for cont in ord_df['contract']]
    print(ord_df)
    for ticker in tickers:
        print('ticker name is',ticker,'################')
        ticker_contract=contract_objects[ticker]
        
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
            sell_condition=hist_df['sma1'].iloc[-1]<hist_df['sma2'].iloc[-1] and hist_df['sma1'].iloc[-2]>hist_df['sma2'].iloc[-2]
            if sell_condition:
                print('close current ticker postion')
                trade_sell_stocks(ticker,hist_df.close.iloc[-1])






main_strategy_code()



current_time=datetime.datetime.now()
print(current_time)

print(datetime.datetime.now())

#start time
start_hour,start_min=9,30
#end time
end_hour,end_min=15,15
start_time=datetime.datetime(current_time.year,current_time.month,current_time.day,start_hour,start_min)
end_time=datetime.datetime(current_time.year,current_time.month,current_time.day,end_hour,end_min)
print(start_time)
print(end_time)

while True:
    if datetime.datetime.now()>start_time:
        break
    print(datetime.datetime.now())


candle_size=60*5

while datetime.datetime.now()<end_time:
    now = datetime.datetime.now()
    print(now)
    seconds_until_next_minute = candle_size - now.second+1
    print(seconds_until_next_minute)
    # Sleep until the end of the current minute
    time.sleep(seconds_until_next_minute)

    # Run your function
    main_strategy_code()