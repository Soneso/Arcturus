from stellar_sdk import Server
from arcturus.utils import add_paging
from typing import Union

async def get_claimable_balances(horizon_url:str, claimant_id:str, sponsor_id:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.claimable_balances()
    if claimant_id is not None:
        builder.for_claimant(claimant_id)
    if sponsor_id is not None:
        builder.for_sponsor(sponsor_id)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records

async def claimable_balance(horizon_url:str, claimable_balance_id:str):
    server = Server(horizon_url=horizon_url)
    claimable_balances_call_builder = (
        server.claimable_balances().claimable_balance(claimable_balance_id)
    )
    claimable_balance = claimable_balances_call_builder.call()
    del claimable_balance['_links']
    return claimable_balance
