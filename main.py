import requests
import os
import datetime
from twilio.rest import Client

STOCK = "CRSP"
COMPANY_NAME = "Crispr Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

AV_API_KEY = os.environ.get("AV_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
ACCOUNT_SID = os.environ.get("TWL_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWL_AUTH_TOKEN")
TWILIO_NUMBER = '11111111'
RECIPIENT_NUMBER = '2222222'

today_date = datetime.date.today()
yesterday_date = today_date - datetime.timedelta(days=1)

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
stock_data_parameters = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": AV_API_KEY,
}

stock_price_response = requests.get(
    STOCK_ENDPOINT, params=stock_data_parameters)
stock_price_data = stock_price_response.json()["Time Series (Daily)"]
open_price = float(stock_price_data[str(today_date)]["1. open"])
close_price = float(stock_price_data[str(yesterday_date)]["4. close"])
price_change_percent = round(
    ((open_price - close_price) / close_price) * 100, 2)

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
news_parameters = {
    "q": COMPANY_NAME,
    "from": str(today_date),
    "sortBy": "popularity",
    "apiKey": NEWS_API_KEY
}

news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
news_data = news_response.json()["articles"]
top_news_articles = news_data[:3]


def send_stock_info():
    if price_change_percent >= 0:
        header = f"{STOCK}: 📈 {price_change_percent}%"
    else:
        header = f"{STOCK}: 📉 {abs(price_change_percent)}%"

    message = f"{header} \n"

    for article in top_news_articles:
        title = article["title"]
        brief = article["content"].split("[")[0]
        news_url = article["url"]
        message += f"\nHeadline: {title} \nBrief: {brief} \nLink: {news_url} \n"

    return message


if abs(price_change_percent) >= 5:
    client = Client(ACCOUNT_SID(), AUTH_TOKEN)
    message = client.messages \
        .create(
            body=send_stock_info(),
            from_=TWILIO_NUMBER,
            to=RECIPIENT_NUMBER
            )
