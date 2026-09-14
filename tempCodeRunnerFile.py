from massive import RESTClient
from dotenv import load_dotenv
import os

load_dotenv()

MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")

client = RESTClient(MASSIVE_API_KEY)

## Option Contract Snapshot
# snapshot = client.get_snapshot_option(
# 	"SPY",
# 	"O:SPY280121C00750000"
# 	)

# print(snapshot)

## Option Chain Snapshot
# options_chain = []
# for o in client.list_snapshot_options_chain(
#     "SPY",
#     params={
#         "order": "asc", 
#         "limit": 10, 
#         "sort": "ticker",
# 	},
# ):
#     options_chain.append(o)

# print(options_chain)

## Specific
import os
from datetime import datetime, timedelta, timezone
from massive import RESTClient
from dotenv import load_dotenv

# load_dotenv()

# def get_target_short_put(underlying_symbol: str):
#     client = RESTClient(api_key=os.getenv("MASSIVE_API_KEY"))
    
#     # 1. Define your 30-to-60 DTE target date window
#     today = datetime.now(timezone.utc).date()
#     min_exp = today + timedelta(days=30)
#     max_exp = today + timedelta(days=60)
    
#     # 2. Query Massive's Option Chain Snapshot for puts
#     chain_params = {
#         "contract_type": "put",
#         "expiration_date.gte": min_exp.strftime("%Y-%m-%d"),
#         "expiration_date.lte": max_exp.strftime("%Y-%m-%d"),
#     }
    
#     target_contract = None
#     min_delta_diff = float("inf")
    
#     # Iterate through the options snapshot chain
#     for opt in client.list_snapshot_options_chain(underlying_symbol, params=chain_params):
#         greeks = getattr(opt, "greeks", None)
#         if not greeks or greeks.delta is None:
#             continue
            
#         # 3. Filter for contracts closest to target delta (-0.20)
#         delta_diff = abs(greeks.delta - (-0.20))
        
#         if delta_diff < min_delta_diff:
#             min_delta_diff = delta_diff
#             target_contract = opt

#     return target_contract

# print(get_target_short_put("SPY"))

today = datetime.now(timezone.utc).date()
print(today)