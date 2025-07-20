# -*- coding: utf-8 -*-
import requests
import smtplib
import datetime
import matplotlib.pyplot as plt
import re
import random
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from textblob import TextBlob
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

load_dotenv()  # Loads variables from .env

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

# Dynamically load portfolios from .env
PORTFOLIOS = {}
for i in range(1, 10):  # Supports up to 9 users, increase if needed
    name = os.getenv(f"PORTFOLIO{i}_NAME")
    amount = os.getenv(f"PORTFOLIO{i}_AMOUNT")
    email = os.getenv(f"PORTFOLIO{i}_EMAIL")
    if name and amount and email:
        PORTFOLIOS[name] = {
            "amount": float(amount),
            "email": email
        }

def get_xrp_data():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'ripple',
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_24hr_vol': 'true',
        'include_market_cap': 'true'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['ripple']

def get_xrp_24h_prices():
    url = 'https://api.coingecko.com/api/v3/coins/ripple/market_chart'
    params = {'vs_currency': 'usd', 'days': 1}
    response = requests.get(url, params=params)
    data = response.json()
    if 'prices' not in data:
        print("Error fetching price data:", data)
        return [], []
    prices = data['prices']
    times = [point[0] for point in prices]
    price_values = [point[1] for point in prices]
    return times, price_values

def plot_xrp_24h_chart(times, prices, filename='xrp_24h.png'):
    # Convert timestamps to hours:minutes
    times_fmt = [datetime.datetime.fromtimestamp(t/1000).strftime('%H:%M') for t in times]
    plt.figure(figsize=(10, 4))
    plt.plot(times_fmt, prices, color='blue')
    plt.title('XRP Price - Last 24 Hours')
    plt.xlabel('Time (UTC)')
    plt.ylabel('Price (USD)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Show fewer x-ticks for clarity
    plt.xticks(times_fmt[::len(times_fmt)//8])
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(filename)
    plt.close()

def get_xrp_news(api_key, limit=3):
    url = "https://cryptopanic.com/api/v1/posts/"
    params = {
        "auth_token": api_key,
        "currencies": "XRP",
        "public": "true"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"CryptoPanic API error: {response.status_code}")
        print("Response text:", response.text)
        return []
    try:
        data = response.json()
    except Exception as e:
        print("Error decoding JSON from CryptoPanic:", e)
        print("Response text:", response.text)
        return []
    headlines = []
    if "results" in data:
        for post in data["results"][:limit]:
            title = post.get("title", "No title")
            link = post.get("url", "#")
            if title and link:
                headlines.append(f'• <a href="{link}">{title}</a><br><br>')
    return headlines

def extract_titles(headlines):
    return [re.sub('<[^<]+?>', '', h) for h in headlines]

def analyze_sentiment(headlines):
    if not headlines:
        return "No news to analyze."
    # Join all headlines into one string for overall sentiment
    text = " ".join(headlines)
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def get_random_fun():
    try:
        response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
        data = response.json()
        return data.get("text", "Crypto tip: Always keep your private keys safe!")
    except Exception:
        return "Crypto tip: Always keep your private keys safe!"

def job():
    xrp_data = get_xrp_data()
    times, prices = get_xrp_24h_prices()
    if not times or not prices:
        print("Could not fetch 24h price data. Skipping chart/email.")
        return
    plot_xrp_24h_chart(times, prices)

    # Get news and analyze sentiment
    news_headlines = get_xrp_news(CRYPTOPANIC_API_KEY)
    news_html = "".join(news_headlines) if news_headlines else "No recent XRP news found."

    # Extract titles for sentiment analysis
    titles = extract_titles(news_headlines)
    sentiment = analyze_sentiment(titles)

    # Pick a random fun extra
    fun_extra = get_random_fun()

    # Send emails to each person
    for name, info in PORTFOLIOS.items():
        if info["amount"] > 0 and info["email"]:
            send_email(xrp_data, info["email"], name, info["amount"],
                       news_html=news_html, sentiment=sentiment, fun_extra=fun_extra)
            print(f"Sent XRP update to {name} at {info['email']}")

def send_email(xrp_data, recipient_email, name, amount, chart_filename='xrp_24h.png', news_html="", sentiment="", fun_extra=""):
    price = xrp_data['usd']
    change_24h = xrp_data.get('usd_24h_change', 0)
    volume_24h = xrp_data.get('usd_24h_vol', 0)
    market_cap = xrp_data.get('usd_market_cap', 0)
    value = amount * price

    change_symbol = "+" if change_24h >= 0 else ""

    subject = "XRP Price Update"
    html_body = f"""<html>
    <body>
    <h2>XRP Portfolio & Market Info</h2>
    <b>Portfolio Value:</b><br>
    {name}: {amount:,.5f} XRP ≈ ${value:,.2f} (approximate values)<br><br>
    <b>Current Price:</b> ${price:.4f}<br><br>
    <b>Market Stats:</b><br>
    24h Change: {change_symbol}{change_24h:.2f}%<br>
    24h Volume: ${volume_24h:,.0f}<br>
    Market Cap: ${market_cap:,.0f}<br><br>
    <b>Latest XRP News:</b><br>
    {news_html}
    <b>News Sentiment:</b> {sentiment}<br><br>
    <b>24-Hour XRP Price Chart:</b><br>
    <img src="cid:chart"><br>
    <hr>
    <b>Random Fun Fact:</b> {fun_extra}<br>
    <br>
    <i>Sent by our favorite XRP Bot</i>
    </body>
    </html>
    """

    msg = MIMEMultipart('related')
    msg['From'] = EMAIL_USER
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    with open(chart_filename, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<chart>')
        img.add_header('Content-Disposition', 'inline', filename=chart_filename)
        msg.attach(img)

    with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, recipient_email, msg.as_string())

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'cron', hour=6, minute=0)
    scheduler.add_job(job, 'cron', hour=18, minute=0)
    print("XRP price bot started. Will send updates at 6am and 6pm daily via Email.")
    job()  # Send one immediately on start
    scheduler.start()