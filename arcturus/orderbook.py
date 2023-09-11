from stellar_sdk import Server, Asset
from arcturus.utils import canonic_asset
from typing import (Union, Dict, Any)

NATIVE = 'native'
BIDS = 'bids'
ASKS = 'asks'
PRICE_R = 'price_r'
PRICE = 'price'
AMOUNT = 'amount'
BASE = 'base'
COUNTER = 'counter'
INVALID_SELLING_ASSET = 'invalid selling asset'
INVALID_BUYING_ASSET = 'invalid buying asset'

async def orderbook(horizon_url:str, selling_asset_code:str, selling_asset_issuer:str, 
                    buying_asset_code:str, buying_asset_issuer:str):
    
    server = Server(horizon_url=horizon_url)
    
    if selling_asset_code is None:
        raise ValueError(INVALID_SELLING_ASSET)
    
    if buying_asset_code is None:
        raise ValueError(INVALID_BUYING_ASSET)
    
    selling_asset = Asset.native()
    if selling_asset_code != NATIVE:
        if selling_asset_issuer is not None:
            selling_asset = Asset(selling_asset_code, selling_asset_issuer)
        else:
            raise ValueError(INVALID_SELLING_ASSET)
    
    buying_asset = Asset.native()
    if buying_asset_code != NATIVE:
        if buying_asset_issuer is not None:
            buying_asset = Asset(buying_asset_code, buying_asset_issuer)
        else:
            raise ValueError(INVALID_BUYING_ASSET)

    builder = server.orderbook(selling=selling_asset, buying=buying_asset)
    
    records = builder.call()
    bids_simple = []
    for bid in records[BIDS]:
       bids_simple.append(bid[PRICE] + "/" + bid[AMOUNT])
       
    records[BIDS] = bids_simple
    
    if len(records[BIDS]) > 5:
        records[BIDS] = records[BIDS][:5]
    
    asks_simple = []
    for ask in records[ASKS]:
        asks_simple.append(ask[PRICE] + "/" + ask[AMOUNT])
    
    records[ASKS] = asks_simple
    
    if len(records[ASKS]) > 5:
        records[ASKS] = records[ASKS][:5]
    
    
    canonic_asset(dic=records, key= BASE)
    canonic_asset(dic=records, key= COUNTER)
    return records