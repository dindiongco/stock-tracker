from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import base64
from io import BytesIO
from matplotlib.figure import Figure
from alpha_vantage.timeseries import TimeSeries

app = Flask(__name__)

STOCK_API_KEY = os.environ.get('av_key')
NEWS_API_KEY = os.environ.get('maux_key')
NEWS_API_URL = 'https://api.marketaux.com/v1/news/all'

ts = TimeSeries(key=STOCK_API_KEY, output_format='pandas')


def get_news(symbol):
    response = requests.get(url=NEWS_API_URL, params={
                            'symbols': symbol, 'api_token': NEWS_API_KEY})
    data = response.json()
    return data['data'][0:4]


def get_df(option, symbol):
    if option == 'monthly':
        df, meta_data = ts.get_monthly_adjusted(symbol=symbol)
    if option == 'weekly':
        df, meta_data = ts.get_weekly_adjusted(symbol=symbol)
    if option == 'daily':
        df, meta_data = ts.get_daily_adjusted(symbol=symbol)
    df.rename(
        columns={'1. open': 'open', '2. high': 'high',
                 '3. low': 'low', '4. close': 'close', '5. adjusted close': 'adjusted close', '6. volume': 'volume',
                 '7. dividend amount': 'dividend amount'},
        inplace=True, errors='raise')
    return df


def get_graph(df, stock):
    fig = Figure()
    ax = fig.subplots()

    ax.plot(df['open'], label='Open', color='skyblue', linestyle='--')
    ax.plot(df['close'], label='Close', color='crimson')
    ax.plot(df['low'], label='Low', color='green')
    ax.plot(df['high'], label='High', color='orange')
    ax.grid()
    ax.legend()
    ax.set_title(f'{stock}')

    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        stock = request.form.get('ticker')
        date_range = request.form.get('option')

        news = get_news(stock)
        data = get_df(date_range, stock)
        graph = get_graph(data, stock)
        return render_template('stock.html', stock=stock, graph=graph, news_data=news)
    return render_template('index.html')


@app.route('/<stock>')
def stock_data():
    return render_template('stock.html')

# @app.route('/weekly/<symbol>')
# def weekly(symbol):
#     df, meta_data = ts.get_weekly(symbol=symbol)
#     df.rename(
#         columns={'1. open': 'open', '2. high': 'high',
#                  '3. low': 'low', '4. close': 'close', '5. volume': 'volume'},
#         inplace=True, errors='raise')
#     fig = Figure()
#     ax = fig.subplots()
#     ax.plot(df['close'])
#     # Save it to a temporary buffer.
#     buf = BytesIO()
#     fig.savefig(buf, format="png")
#     # Embed the result in the html output.
#     data = base64.b64encode(buf.getbuffer()).decode("ascii")
#     return f"<img src='data:image/png;base64,{data}'/>"


if __name__ == '__main__':
    app.run(debug=True)
