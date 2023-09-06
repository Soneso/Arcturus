from stellar_sdk import Server
from arcturus.utils import add_paging
from typing import Union

async def for_issuer(horizon_url:str, asset_issuer_id:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    builder = server.assets().for_issuer(asset_issuer_id)
    add_paging(builder, cursor, order, limit) 
    records = builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records