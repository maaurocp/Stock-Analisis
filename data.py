import yfinance as yf


def get_ticker(ticker):
    return yf.Ticker(ticker)


def get_info(ticker):
    t = get_ticker(ticker)
    return t.info


def get_financials(ticker):
    t = get_ticker(ticker)

    return {
        "cashflow": t.cashflow,
        "balance": t.balance_sheet,
        "income": t.financials
    }

def get_history(ticker, period="1mo", interval="1d"):
    t = yf.Ticker(ticker)
    return t.history(period=period, interval=interval)