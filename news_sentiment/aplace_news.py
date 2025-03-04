
from alpaca_trade_api import REST, Stream



key='PKC6REX07T6K0UY6M6IY'
secret='vCT1OD2npqmVejGo6nlgWFtTsp1ilXmIayllnpug'

API_KEY=key
API_SECRET=secret


import pandas as pd


news_api = REST(API_KEY, API_SECRET)
# Provide a single symbol as a string or a list of symbols
symbol = 'AAPL' 

# Start date for news retrieval
start = '2016-01-01'  

# End date for news retrieval
end = '2023-12-01'  

# Limit the number of news articles to retrieve
limit = 50000  

# Include news content
include_content = True 

# Exclude contentless news articles
exclude_contentless = True  

# API call
news_list = news_api.get_news(symbol=symbol, start=start, end=end, limit=limit, include_content=include_content, exclude_contentless=exclude_contentless)

# Dataframe to store the news article information
news = pd.DataFrame(columns=['id', 'created_at', 'updated_at', 'headline', 'content'])

# Traverse the NewsV2 object
for i in range(len(news_list)):
    
    news_df = pd.DataFrame({
        'id': news_list[i].id,
        'created_at': news_list[i].created_at,
        'updated_at': news_list[i].updated_at,
        'headline': news_list[i].headline,
        'content': news_list[i].content
    }, index=[0])  
    
    news = pd.concat([news, news_df], ignore_index=True)

# Display the news data
news.head()
print(news)
news.to_csv('news2.csv')

news.to_pickle("AAPL_news_2016Jan_2023Sep.bz2")

#what is difference between pickle and csv?
#pickle is a binary file format, csv is a text file format
#pickle is faster, csv is human readable
#pickle is python specific, csv is language agnostic


