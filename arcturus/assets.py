from stellar_sdk import Server
from arcturus.utils import add_paging, delete_keys_except
from typing import Union

ASSET_CODE = 'asset_code'
ASSET_ISSUER = 'asset_issuer'
NUM_ACCOUNTS = 'num_accounts'

async def get_assets(horizon_url:str, asset_issuer_id:str, asset_code:str):
    server = Server(horizon_url=horizon_url)
    builder = server.assets()
    
    if asset_issuer_id is not None:
        builder = builder.for_issuer(asset_issuer_id)
    if asset_code is not None:
        builder = builder.for_code(asset_code)
        
    records = builder.call()["_embedded"]["records"]
    result = []
    for x in records:
        if ASSET_CODE in x and ASSET_ISSUER in x and NUM_ACCOUNTS in x:
            result.append(x[ASSET_CODE] + ':' + x[ASSET_ISSUER] + ' / ' + str(x[NUM_ACCOUNTS]))
        
    return result

async def get_details(horizon_url:str, asset_issuer_id:str, asset_code:str):
    server = Server(horizon_url=horizon_url)
    builder = server.assets().for_issuer(asset_issuer_id).for_code(asset_code)
    records = builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records