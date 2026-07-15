import pandas as pd


from app.constants import DEFAULT_PEERS
from app.tools.financial_data import fetch_all_financial_data
from app.analysis.metrics import calculate_all_metrics

def get_default_peers(ticker: str) -> list[str]:

    peers= DEFAULT_PEERS[ticker]

    return peers

def fetch_peer_profiles(peer_tickers: list[str]) -> list[dict]:

    profiles= []

    for ticker in peer_tickers:
        try:
            all_financial_data = fetch_all_financial_data(ticker= ticker)
            peer_profile = all_financial_data.get("company_info")
            profiles.append(peer_profile)
        except:
            print(f"Skipping {ticker}...")
    
    return profiles

def fetch_peer_metrics(peer_tickers: list[str]) -> pd.DataFrame:

    all_metrics= []
    
    for ticker in peer_tickers:
        try:
            all_financial_data = fetch_all_financial_data(ticker= ticker)
            metrics = calculate_all_metrics(
                income_statement=all_financial_data.get("income_statement"),
                cash_flow= all_financial_data.get("cash_flow"),
                balance_sheet= all_financial_data.get("balance_sheet"))

            peer_profile= all_financial_data.get("company_info")

            market_cap = peer_profile.get("marketCap")
            revenue_growth = metrics.get("revenue_growth")
            gross_margin = metrics.get("gross_margin")
            operating_margin=metrics.get("operating_margin")
            net_margin = metrics.get("net_margin")
            pe_ratio = peer_profile.get("trailingPE")
            ps_ratio = peer_profile.get("priceToSalesTrailing12Months")
            ev_to_ebitda = peer_profile.get("enterpriseToEbitda")

            #In case division by 0, or some of the terms are "None"
            try:
                fcf_yield = metrics.get("free_cash_flow") / market_cap
            except:
                fcf_yield =None

            leverage = peer_profile.get("debtToEquity")

            metrics ={
                "ticker": ticker,
                "market_cap": market_cap,
                "revenue_growth": revenue_growth,
                "gross_margin": gross_margin,
                "operating_margin": operating_margin,
                "net_margin": net_margin,
                "pe_ratio": pe_ratio,
                "ps_ratio": ps_ratio,
                "ev_to_ebitda": ev_to_ebitda,
                "fcf_yield": fcf_yield,
                "leverage": leverage
            }

            all_metrics.append(metrics)


        except:
            print(f"Skipping {ticker}...")
    
    all_metrics= pd.DataFrame(all_metrics).set_index("ticker")´
    
    return all_metrics