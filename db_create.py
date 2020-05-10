# from api.data import db_session
#
#
# # подключение к существующей бд или создание новой
# def main():
#     db_session.global_init("api/db/user_data.sqlite")
#
#
# if __name__ == '__main__':
#     main()
from fbprophet import Prophet

import yfinance as yf
a = 'AAPL,AAL,SPY,WWE,DAKT,ORA,CAMP,BREW,MSFT,TSLA,IBM'.split(',')


def load_data():
    for ticker in a:
        yf.download(ticker, start='2020-01-01').to_csv(f'static/static_data/{ticker}_daily.csv')
        print(ticker)

load_data()