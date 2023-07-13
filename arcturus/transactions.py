from stellar_sdk import Server
from arcturus.utils import add_paging

async def get_details(horizon_url, hash):
    server = Server(horizon_url=horizon_url)
    builder = server.transactions().transaction(transaction_hash=hash)
    transaction = builder.call()
    del_extra_data(transaction)    
  
    return transaction

async def for_account(horizon_url, account_id, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.transactions().for_account(account_id=account_id)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for transaction in records:
       del_extra_data(transaction)
            
    return records

async def for_ledger(horizon_url, ledger_sequence, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.transactions().for_ledger(sequence=ledger_sequence)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for transaction in records:
        del_extra_data(transaction)
            
    return records

async def for_claimable_balance(horizon_url, claimable_balance_id, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.transactions().for_claimable_balance(claimable_balance_id=claimable_balance_id)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for transaction in records:
        del_extra_data(transaction)
            
    return records

async def for_liquidity_pool(horizon_url, liquidity_pool_id, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.transactions().for_liquidity_pool(liquidity_pool_id=liquidity_pool_id)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for transaction in records:
        del_extra_data(transaction)
            
    return records

def del_extra_data(transaction):
    # delete data that we do not need at this time to save on context window
    del transaction['_links']
    del transaction['id'] # we have the hash and it is also known from request
    if 'envelope_xdr' in transaction:
        del transaction['envelope_xdr']
    if 'result_xdr' in transaction:
        del transaction['result_xdr']
    if 'result_meta_xdr' in transaction:
        del transaction['result_meta_xdr']
    if 'fee_meta_xdr' in transaction:
        del transaction['fee_meta_xdr']
    return transaction     