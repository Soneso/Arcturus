from stellar_sdk import Server
from arcturus.utils import add_paging

async def for_claimant(horizon_url, claimant_id, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.claimable_balances().for_claimant(claimant_id)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records

async def for_sponsor(horizon_url, sponsor_id, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.claimable_balances().for_sponsor(sponsor_id)
    add_paging(builder, cursor, order, limit)
    records += builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records

async def claimable_balance(horizon_url, claimable_balance_id):
    server = Server(horizon_url=horizon_url)
    claimable_balances_call_builder = (
        server.claimable_balances().claimable_balance(claimable_balance_id)
    )
    claimable_balance = claimable_balances_call_builder.call()
    del claimable_balance['_links']
    return claimable_balance
