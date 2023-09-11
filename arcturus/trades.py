from stellar_sdk import Server, Asset
from arcturus.utils import add_paging
from typing import (Union, Dict, Any)


BASE_ASSET = 'base_asset'
BASE_ASSET_TYPE = 'base_asset_type'
BASE_ASSET_CODE = 'base_asset_code'
BASE_ASSET_ISSUER = 'base_asset_issuer'
COUNTER_ASSET = 'counter_asset'
COUNTER_ASSET_TYPE = 'counter_asset_type'
COUNTER_ASSET_CODE = 'counter_asset_code'
COUNTER_ASSET_ISSUER = 'counter_asset_issuer'
NATIVE = 'native'
PRICE = 'price'
LINKS = '_links'

async def for_account(horizon_url:str, account_id:str, trade_type:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.trades().for_account(account_id=account_id)
    if trade_type is not None:
        builder = builder.for_trade_type(trade_type = trade_type)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for trade in records:
        simplify_trade(trade=trade)
        
    return records

async def for_liquidity_pool(horizon_url:str, liquidity_pool_id:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.trades().for_liquidity_pool(liquidity_pool_id=liquidity_pool_id)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for trade in records:
        simplify_trade(trade=trade)
        
    return records

async def for_offer(horizon_url:str, offer_id:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.trades().for_offer(offer_id=offer_id)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    for trade in records:
        simplify_trade(trade=trade)
        
    return records

async def all_trades(horizon_url:str, base_asset_code:str, base_asset_issuer:str,
                     counter_asset_code:str, counter_asset_issuer:str,
                     offer_id:str, trade_type:str,
                     cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.trades()

    if offer_id is not None:
        builder = builder.for_offer(offer_id = offer_id)
    elif trade_type is not None:
        builder = builder.for_trade_type(trade_type = trade_type)
    
    base_asset = None
    counter_asset = None
        
    if base_asset_code == 'native':
        base_asset = Asset.native()
    elif base_asset_code is not None and base_asset_issuer is not None:
        base_asset = Asset(base_asset_code, base_asset_issuer)
        
        
    if counter_asset_code == 'native':
        counter_asset = Asset.native()
    elif counter_asset_code is not None and counter_asset_issuer is not None:
        counter_asset =  Asset(counter_asset_code, counter_asset_issuer)
    
    if base_asset is not None and counter_asset is not None:
        builder = builder.for_asset_pair(base=base_asset, counter=counter_asset)
    
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for trade in records:
        simplify_trade(trade=trade)
        
    return records

def simplify_trade(trade:Dict[str, Any]):
    if trade[BASE_ASSET_TYPE] == NATIVE:
        trade[BASE_ASSET] = NATIVE
    else:
        trade[BASE_ASSET] = trade[BASE_ASSET_CODE] + ':' + trade[BASE_ASSET_ISSUER]
    
    del trade[BASE_ASSET_TYPE]
    if BASE_ASSET_CODE in trade:
        del trade[BASE_ASSET_CODE]
    if BASE_ASSET_ISSUER in trade:
        del trade[BASE_ASSET_ISSUER]

    if trade[COUNTER_ASSET_TYPE] == NATIVE:
        trade[COUNTER_ASSET] = NATIVE
    else:
        trade[COUNTER_ASSET] = trade[COUNTER_ASSET_CODE] + ':' + trade[COUNTER_ASSET_ISSUER]

    del trade[COUNTER_ASSET_TYPE]
    if COUNTER_ASSET_CODE in trade:
        del trade[COUNTER_ASSET_CODE]
    
    if COUNTER_ASSET_ISSUER in trade:
        del trade[COUNTER_ASSET_ISSUER]   
    
    if PRICE in trade:
        trade[PRICE] = "d=" + trade[PRICE]['d'] +"; n=" + trade[PRICE]['n']
        
    if LINKS in trade:
        del trade[LINKS]   