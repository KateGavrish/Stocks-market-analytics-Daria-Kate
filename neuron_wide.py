import yfinance as yf


msft = yf.Ticker("mstf")

# get stock info
print(msft.info)