from stellar_sdk import Server
from arcturus.utils import add_paging
from typing import Union

async def get_assets(horizon_url:str, asset_issuer_id:str, asset_code:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    builder = server.assets()
    
    if asset_issuer_id is not None:
        builder = builder.for_issuer(asset_issuer_id)
    if asset_code is not None:
        builder = builder.for_code(asset_code)
        
    add_paging(builder, cursor, order, limit) 
    records = builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records