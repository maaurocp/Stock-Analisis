from data import get_info, get_financials, get_history
import numpy as np
from data import get_history


def analyze_company(ticker):
    info = get_info(ticker)
    fin = get_financials(ticker)

    result = {}

    result["name"] = info.get("shortName")
    result["price"] = info.get("currentPrice")
    result["pe"] = info.get("trailingPE")
    result["market_cap"] = info.get("marketCap")
    result["roe"] = info.get("returnOnEquity") * 100 if info.get("returnOnEquity") else None
    result["margin"] = info.get("profitMargins") * 100 if info.get("profitMargins") else None
    result["debt"] = info.get("totalDebt")
    result["cash"] = info.get("totalCash")
    result["free_cashflow"] = get_3y_free_cashflow(ticker)
    # ===== NIVEL 1 METRICS =====

    fcf = result["free_cashflow"]
    mc = result["market_cap"]
    debt = result["debt"]

    # FCF TTM
    fcf_ttm = fcf.get("TTM") if fcf else None

    # FCF Yield
    if fcf_ttm and mc:
        result["fcf_yield"] = (fcf_ttm / mc) * 100
    else:
        result["fcf_yield"] = None

    # Debt / FCF
    if debt and fcf_ttm and fcf_ttm != 0:
        result["debt_fcf"] = debt / fcf_ttm
    else:
        result["debt_fcf"] = None

    # Revenue Growth YoY (2024 vs 2023)
    income = fin["income"]
    r24=None

    try:
        rev = income.loc["Total Revenue"]
        r24 = rev.iloc[0]
        r23 = rev.iloc[1]
        result["revenue_growth"] = ((r24 - r23) / r23) * 100
    except:
        result["revenue_growth"] = None

    # FCF Margin (TTM vs last revenue)
    try:
        result["fcf_margin"] = (fcf_ttm / r24) * 100 if fcf_ttm and r24 else None
    except:
        result["fcf_margin"] = None

    result["returns"] = calculate_returns(ticker)
    result["sharpe"] = calculate_sharpe(ticker)


    result["financials"] = fin

    result["history"] = get_history(ticker, period="1mo")


    return result

def calculate_returns(ticker):
    hist = get_history(ticker, period="1mo")

    if hist.empty:
        return None

    closes = hist["Close"]

    last = closes.iloc[-1]

    # Hoy (último cierre vs cierre anterior)
    if len(closes) >= 2:
        today = (last - closes.iloc[-2]) / closes.iloc[-2]
    else:
        today = 0

    # Semana (5 días trading aprox)
    if len(closes) >= 6:
        week = (last - closes.iloc[-6]) / closes.iloc[-6]
    else:
        week = (last - closes.iloc[0]) / closes.iloc[0]

    # Mes (primer dato del periodo)
    month = (last - closes.iloc[0]) / closes.iloc[0]

    return {
        "today": today * 100,
        "week": week * 100,
        "month": month * 100
    }

def calculate_sharpe(ticker, risk_free_rate=0.03):
    hist = get_history(ticker, period="6mo")

    if hist.empty or len(hist) < 30:
        return None

    closes = hist["Close"]

    returns = closes.pct_change().dropna()

    mean_return = returns.mean()
    volatility = returns.std()

    # convertir risk free anual a diario (252 días de mercado)
    rf_daily = risk_free_rate / 252

    sharpe = (mean_return - rf_daily) / volatility

    # anualizar
    sharpe_annual = sharpe * np.sqrt(252)

    return sharpe_annual

def get_3y_free_cashflow(ticker):
    fin = get_financials(ticker)
    cf = fin["cashflow"]

    if cf is None or cf.empty:
        return None

    try:
        # FCF directo o calculado
        if "Free Cash Flow" in cf.index:
            fcf = cf.loc["Free Cash Flow"]
        else:
            op = cf.loc["Total Cash From Operating Activities"]
            capex = cf.loc["Capital Expenditures"]
            fcf = op + capex

        result = {}

        # TTM = suma de últimos 4 trimestres
        if len(fcf) >= 4 and hasattr(fcf.index[0], "quarter"):
            result["TTM"] = fcf.iloc[:4].sum()
        else:
            result["TTM"] = fcf.iloc[0]

        # años históricos
        wanted_years = [2024, 2023, 2022]

        for col in fcf.index:
            year = col.year
            if year in wanted_years:
                result[str(year)] = fcf[col]

        return result if result else None

    except:
        return None
