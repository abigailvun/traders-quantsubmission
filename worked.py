import os
from dotenv import load_dotenv
from massive import RESTClient
from datetime import datetime, timedelta, timezone
from fredapi import Fred
import numpy as np
import pandas as pd
from scipy.stats import norm
import yfinance as yf

load_dotenv()

HIGH_LIQUIDITY_UNIVERSE = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA']

CLIENT = RESTClient(api_key=os.getenv("MASSIVE_API_KEY"))
FRED = Fred(api_key=os.getenv("FRED_API_KEY"))

def _parse_date(d):
    if isinstance(d, pd.Timestamp):
        return d.date()
    elif isinstance(d, str):
        return datetime.strptime(d, "%Y-%m-%d").date()
    return d

def get_target_option(ticker, simulation_date):
    
    # today = datetime.now(timezone.utc).date()
    simulation_date = _parse_date(simulation_date)
    min_dte = simulation_date + timedelta(days=30)
    max_dte = simulation_date + timedelta(days=60)

    target_option = None
    min_delta_diff = float("inf")

    for o in CLIENT.list_snapshot_options_chain(
        underlying_asset=ticker,
        params={
            "expiration_date.gte": min_dte.strftime("%Y-%m-%d"),
            "expiration_date.lte": max_dte.strftime("%Y-%m-%d"),
            "contract_type": "put",
        },
    ):
        greeks = getattr(o, "greeks", None)
        if not greeks or greeks.delta is None:
            continue

        delta_diff = abs(greeks.delta - (-0.20))
        if delta_diff < min_delta_diff:
            min_delta_diff = delta_diff
            target_option = o

    underlying_asset = getattr(target_option, "underlying_asset", None)
    details = getattr(target_option, "details", None)
    last_quote = getattr(target_option, "last_quote", None)

    if last_quote is None:
        return {
                "ticker": underlying_asset.ticker,
                "stock_price": underlying_asset.price,
                "strike_price": details.strike_price,
                "expiration_date": details.expiration_date,
                "implied_volatility": target_option.implied_volatility,
                "mid_price": target_option.fair_market_value,
                "bid_price": None,
                "ask_price": None,
                "shares_per_contract": details.shares_per_contract,
            }

    return {
        "ticker": underlying_asset.ticker,
        "stock_price": underlying_asset.price,
        "strike_price": details.strike_price,
        "expiration_date": details.expiration_date,
        "implied_volatility": target_option.implied_volatility,
        "mid_price": last_quote.midpoint,
        "bid_price": last_quote.bid,
        "ask_price": last_quote.ask,
        "shares_per_contract": details.shares_per_contract,
    }

def get_sofr_rate(simulation_date):
    sofr_data = FRED.get_series(series_id="SOFR", observation_start='2022-12-01')

    if simulation_date:
        simulation_date = _parse_date(simulation_date)
        date_str = simulation_date.strftime("%Y-%m-%d")
        rate_percent = sofr_data.asof(date_str)
    else:
        rate_percent = sofr_data.iloc[-1]

    return float(rate_percent)/100.0

def get_time_to_expiration(target_option, simulation_date):
    simulation_date = _parse_date(simulation_date)
    expiration_date = _parse_date(target_option["expiration_date"])

    time_to_expiration = (expiration_date - simulation_date).days

    return time_to_expiration

def put_delta_calculation(target_option, simulation_date):
    # target_option = get_target_option(ticker)
    time_to_expiration = get_time_to_expiration(target_option, simulation_date)

    S = target_option["stock_price"] #current stock price
    K = target_option["strike_price"] #strike price
    T = time_to_expiration/365 
    r = get_sofr_rate(simulation_date)
    sigma = target_option["implied_volatility"]

    if T <= 0 or sigma <= 0:
        return -1.0 if S < K else 0.0

    d1 = (np.log(S/K) + (r + 0.5*(sigma**2))*T) / (sigma*np.sqrt(T))

    return norm.cdf(d1) - 1.0

def entry_execution_calculation(target_option, slippage_rate=0.01):
    bid_price = target_option["bid_price"]
    mid_price = target_option["mid_price"]
    shares_per_contract = target_option["shares_per_contract"]

    if bid_price is None:
        bid_price = mid_price * (1.0 - slippage_rate)

    gross_cash_inflow = mid_price * shares_per_contract
    net_cash_inflow =  bid_price * shares_per_contract
    spread_cost = (mid_price - bid_price) * shares_per_contract

    return {
        "gross_cash_inflow": gross_cash_inflow,
        "net_cash_inflow": net_cash_inflow,
        "spread_cost": spread_cost,
    }

def delta_hedge_setup(target_option, simulation_date):
    put_delta = put_delta_calculation(target_option, simulation_date)
    shares_per_contract = target_option["shares_per_contract"]

    shares_to_short = -(put_delta * shares_per_contract)

    return shares_to_short

def run_single_trade_backtest(target_option, simulation_date):
    simulation_date_datetime = _parse_date(simulation_date)

    ## 1. Entry Execution
    execution = entry_execution_calculation(target_option)
    net_cash_inflow = execution["net_cash_inflow"] #Cash collected from selling option

    print(f"[{simulation_date}] SOLD PUT | Strike Price: {target_option["strike_price"]} | Net Cash Inflow: ${net_cash_inflow:.2f}")

    ## 2. Fetch Historical Stock Prices
    expiration_date = target_option["expiration_date"]
    ticker = target_option["ticker"]
    historical_stock_prices = yf.download(tickers=ticker, start=simulation_date, end=expiration_date, progress=False)['Close']
    if isinstance(historical_stock_prices, pd.DataFrame):
        historical_stock_prices = historical_stock_prices.iloc[:,0]

    ## 3. Initial Stock Hedge Setup
    initial_shares_to_short = delta_hedge_setup(target_option, simulation_date)
    entry_stock_price = historical_stock_prices.iloc[0]

    net_cash_inflow += initial_shares_to_short * entry_stock_price
    print(f"Hedge: Short {abs(initial_shares_to_short):.2f} shares at ${entry_stock_price:.2f}")
    current_shares_to_short = initial_shares_to_short

    ## 4. Daily Rebalancing: Loop through every trading day after entry until expiration
    for date_index, stock_price in historical_stock_prices.iloc[1:].items():
        next_day_date = _parse_date(date_index)
        target_option["stock_price"] = float(stock_price)

        next_shares_to_short = delta_hedge_setup(target_option, next_day_date)
        short_shares_difference = next_shares_to_short - current_shares_to_short

        if abs(short_shares_difference) > 0.01:
            net_cash_inflow -= short_shares_difference * stock_price
            current_shares_to_short = next_shares_to_short

    ## 5. Trade Exit & Final P&L Accounting at Expiration
    final_stock_price = float(historical_stock_prices.iloc[-1])
    strike_price = target_option["strike_price"]
    shares_per_contract = target_option["shares_per_contract"]

    option_loss = max(0.0, strike_price - final_stock_price) * shares_per_contract
    net_cash_inflow -= option_loss

    stock_buyback_cost = current_shares_to_short * final_stock_price
    net_cash_inflow -= stock_buyback_cost

    print(f"[{expiration_date}] EXPIRED | Final Stock: ${final_stock_price:.2f} | Final Strategy Cash P&L: ${net_cash_inflow:.2f}\n")
    return net_cash_inflow

simulation_date = datetime.now(timezone.utc).date()
simulation_date_str = simulation_date.strftime("%Y-%m-%d")
target_option = get_target_option("SPY", simulation_date_str)
run_single_trade_backtest(target_option, simulation_date_str)