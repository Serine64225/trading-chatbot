import yfinance as yf

apple = yf.Ticker("AAPL")

info = apple.history(period="5d")

print(info)