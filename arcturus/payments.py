from stellar_sdk import Server
from arcturus.utils import add_paging

async def for_account(horizon_url, account_id, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.payments().for_account(account_id)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records