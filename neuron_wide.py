import pandas as pd
from fbprophet import Prophet
import yfinance as yf

msft = yf.Ticker("BTC-USD")
hist = msft.history(period='max', interval='1d', prepost=True)
trend_df = pd.DataFrame(hist)
print(trend_df.iloc[:, 0:4].keys())
# predictions = 60
#
# train_df = trend_df[:-predictions]
# train_df.reset_index(inplace=True)
# train_df.rename(columns={'Date': 'ds', 'Close': 'y', 'High': 'yhat_upper', 'Low': 'yhat_lower'}, inplace=True)
#
# m = Prophet(changepoint_prior_scale=0.1)
# m.fit(train_df)
# future = m.make_future_dataframe(periods=predictions)
# forecast_test = m.predict(future)
#
#
# predict_df = trend_df.copy()
# predict_df.reset_index(inplace=True)
# predict_df.rename(columns={'Date': 'ds', 'Close': 'y', 'High': 'yhat_upper', 'Low': 'yhat_lower'}, inplace=True)
# m = Prophet(changepoint_prior_scale=0.1)
# m.fit(predict_df)
# future = m.make_future_dataframe(periods=120)
# forecast = m.predict(future)
