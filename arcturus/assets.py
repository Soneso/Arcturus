from stellar_sdk import Server
from arcturus.utils import add_paging

async def for_issuer(horizon_url, asset_issuer_id, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    builder = server.assets().for_issuer(asset_issuer_id)
    add_paging(builder, cursor, order, limit) 
    records = builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records