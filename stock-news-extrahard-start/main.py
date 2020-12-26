import os
import requests
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
ALPHA_VANTAGE_API_KEY = os.environ["ALPHA_VANTAGE_API_KEY"]
ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query"
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
NEWS_API_URL = "http://newsapi.org/v2/top-headlines"
TWILIO_ACCT_ID = os.environ["TWILIO_ACCT_ID"]
TWILIO_AUTH_ID = os.environ["TWILIO_AUTH_ID"]

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

alpha_vantage_params = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": ALPHA_VANTAGE_API_KEY
}

stock_data = requests.get(ALPHA_VANTAGE_API_URL, alpha_vantage_params).json()
tracker_dates = list(stock_data["Time Series (Daily)"])

prev_day_close = stock_data["Time Series (Daily)"][tracker_dates[1]]["4. close"]
curr_day_close = stock_data["Time Series (Daily)"][tracker_dates[0]]["4. close"]
pct_stock_change = ((float(curr_day_close)/float(prev_day_close)) - 1) * 100

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

news_params = {
    "apiKey": NEWS_API_KEY,
    "q": "Tesla"
}

if abs(pct_stock_change) > 0:
    print("Get News - " + str('%.2f' % pct_stock_change) + "%")
    news_data = requests.get(NEWS_API_URL, news_params).json()
    all_articles = list(news_data["articles"])
    body_msg = STOCK + ": "
    if pct_stock_change > 0:
        body_msg += "🔺"
    elif pct_stock_change < 0:
        body_msg += "🔻"
    body_msg += str('%.2f' % pct_stock_change) + "%"

    loop_to = min(3, int(news_data["totalResults"]))
    article_no = 0

    while article_no < loop_to:
        i_article = all_articles[article_no]
        article_text = "\n\nHeadline: " + str(i_article["title"]) + "\nBrief: " + str(i_article["description"])
        if article_text not in body_msg:
            body_msg += article_text
        else:
            loop_to += 1
        article_no += 1

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 

    client = Client(TWILIO_ACCT_ID, TWILIO_AUTH_ID)
    message = client.messages \
        .create(
            body=body_msg,
            from_='+15015107946',
            to='+447506256864'
        )

# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
