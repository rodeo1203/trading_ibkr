import pandas as pd
# df=pd.read_csv('sample.csv')
# df['Datetime']=pd.to_datetime(df['Datetime'])
# print(df)
# df=df.set_index('Datetime')
# print(df)

# d=pd.to_datetime('2024-02-09')
# print(d)
# print(df[df.index>d])
# import yfinance as yf
# data=yf.download('MSFT',period='max',interval='1m')
# print(data)


import pandas as pd
sdata=pd.read_csv('data.csv').head(1000)
sdata=sdata.dropna()
sdata['date']=pd.to_datetime(sdata['date'])
print(sdata)
print(sdata.info())
# sdata['date']=(sdata['date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata'))
sdata['date'] = sdata['date'].dt.tz_localize(None)
print(sdata)







# #to slice time from all days
# data=data.between_time('09:40', '15:55')
# print(data)

# #to slice using string 
# data1=data.loc['2024-02-18 09:43:00':'2024-02-20 15:52:00']
# print(data1)