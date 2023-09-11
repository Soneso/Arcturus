from stellar_sdk import Server
from arcturus.utils import add_paging, delete_keys_except
from typing import Union

KEYS_TO_KEEP = ['id', 'paging_token', 'type', 'transaction_hash', 'transaction_successful', 'source_account', 'created_at']
    
async def get_operations(horizon_url:str, account_id:str, ledger_sequence:str, liquidity_pool_id:str, 
                         claimable_balance_id:str, transaction_hash:str, include_failed:bool, 
                         cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.operations()
    if account_id is not None:
        builder = builder.for_account(account_id=account_id)
    elif ledger_sequence is not None:
        builder = builder.for_ledger(sequence=ledger_sequence)
    elif liquidity_pool_id is not None:
        builder = builder.for_liquidity_pool(liquidity_pool_id=liquidity_pool_id)
    elif claimable_balance_id is not None:
        builder = builder.for_claimable_balance(claimable_balance_id=claimable_balance_id)
    elif transaction_hash is not None:
        builder = builder.for_transaction(transaction_hash=transaction_hash)
        
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for x in records:
        delete_keys_except(x, KEYS_TO_KEEP)
        
    return records
        
async def get_details(horizon_url:str, operation_id:str):
    server = Server(horizon_url=horizon_url)
    builder = server.operations().operation(operation_id=operation_id)
    operation = builder.call()
    del operation['_links']
    del operation['type_i']
    if operation['type'] == 'set_options':
        if 'set_flags' in operation:
            del operation['set_flags']
        if 'clear_flags' in operation:
            del operation['clear_flags']
    type_key = operation['type'] + '_details'
    return {type_key: operation}