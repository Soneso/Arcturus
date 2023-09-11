from stellar_sdk import Server, Asset
from arcturus.utils import add_paging, replace_key
from typing import (Union, Dict, Any)

async def get_liquidity_pools(horizon_url:str, account_id:str, reserves:str,
                              cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.liquidity_pools()
    
    if account_id is not None:
        builder = builder.for_account(account_id = account_id)
    if reserves is not None:
        assets = []
        str_assets = reserves.split(",")
        for asset in str_assets:
            if asset == 'native':
                assets.append(Asset.native())
            else:
                canonic = asset.split(':')
                if len(canonic) == 2:
                   assets.append(Asset(canonic[0], canonic[1])) 
        if len(assets) > 0:
            builder = builder.for_reserves(reserves = assets)
    
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for liquidity_pool in records:
        simplify_liquidity_pool(liquidity_pool=liquidity_pool)
        
    return records

async def get_details(horizon_url:str, liquidity_pool_id:str):
    server = Server(horizon_url=horizon_url)
    builder = server.liquidity_pools().liquidity_pool(liquidity_pool_id=liquidity_pool_id)
    liquidity_pool = builder.call()
    simplify_liquidity_pool(liquidity_pool=liquidity_pool)
    return liquidity_pool

def simplify_liquidity_pool(liquidity_pool:Dict[str, Any]):
    if '_links' in liquidity_pool:
        del liquidity_pool['_links']
    if 'fee_bp' in liquidity_pool:
        del liquidity_pool['fee_bp']
    if 'last_modified_ledger' in liquidity_pool:
        del liquidity_pool['last_modified_ledger']
    
    if 'reserves' in liquidity_pool:
       canonic = []
       for reserve in liquidity_pool['reserves']:
           if 'asset' in reserve and 'amount' in reserve:
               canonic.append(reserve['asset'] + ' / ' + reserve['amount'])
               
       liquidity_pool['reserves'] = canonic
    
    
    if 'last_modified_time' in liquidity_pool:
        replace_key(liquidity_pool, 'last_modified_time', 'last_modified')