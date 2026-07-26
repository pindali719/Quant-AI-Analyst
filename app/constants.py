DEFAULT_PEERS = {
    "NVDA": ["AMD", "INTC", "AVGO", "QCOM", "TSM", "ASML"],
    "AAPL": ["MSFT", "GOOGL", "META", "AMZN"],
}

NONE_INPUT = 0


SCORING_WEIGHTS = {
    "growth": 0.30,
    "profitability": 0.25,
    "valuation": 0.20,
    "balance_sheet": 0.15,
    "risk": 0.10,
}

YAHOO_SECTOR_KEYS = {
    "basic-materials",
    "communication-services",
    "consumer-cyclical",
    "consumer-defensive",
    "energy",
    "financial-services",
    "healthcare",
    "industrials",
    "real-estate",
    "technology",
    "utilities",
}