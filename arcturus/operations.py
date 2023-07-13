from stellar_sdk import Server
from arcturus.utils import add_paging

KEYS_TO_KEEP = ['id', 'paging_token', 'type', 'transaction_hash', 'transaction_successful', 'source_account', 'created_at']
    
async def for_account(horizon_url, account_id, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.operations().for_account(account_id=account_id)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for x in records:
        delete_keys_except(x, KEYS_TO_KEEP)
        
    return records

async def for_ledger(horizon_url, ledger_sequence, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.operations().for_ledger(sequence=ledger_sequence)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for x in records:
        delete_keys_except(x, KEYS_TO_KEEP)
        
    return records

async def for_liquidity_pool(horizon_url, liquidity_pool_id, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.operations().for_liquidity_pool(liquidity_pool_id=liquidity_pool_id)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for x in records:
        delete_keys_except(x, KEYS_TO_KEEP)
        
    return records

async def for_claimable_balance(horizon_url, claimable_balance_id, include_failed, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.operations().for_claimable_balance(claimable_balance_id=claimable_balance_id)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for x in records:
        delete_keys_except(x, KEYS_TO_KEEP)
        
    return records

async def for_transaction(horizon_url, transaction_hash, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.operations().for_transaction(transaction_hash=transaction_hash)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for x in records:
        delete_keys_except(x, KEYS_TO_KEEP)
        
    return records

def delete_keys_except(dictionary, keys_to_keep):
    keys_to_delete = [key for key in dictionary.keys() if key not in keys_to_keep]
    for key in keys_to_delete:
        del dictionary[key]
        
async def get_details(horizon_url, operation_id):
    server = Server(horizon_url=horizon_url)
    builder = server.operations().operation(operation_id=operation_id)
    operation = builder.call()
    del operation['_links']
    if operation['type'] == 'set_options':
        if 'set_flags' in operation:
            del operation['set_flags']
        if 'clear_flags' in operation:
            del operation['clear_flags']
        
    return operation