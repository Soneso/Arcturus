from stellar_sdk import Server
from arcturus.utils import add_paging

KEYS_TO_KEEP = ['id', 'paging_token', 'type', 'transaction_hash', 'transaction_successful', 'source_account', 'created_at']
    
async def for_account(horizon_url, account_id, cursor, order, limit):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.operations().for_account(account_id=account_id)
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