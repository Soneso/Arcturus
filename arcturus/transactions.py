from stellar_sdk import Server, parse_transaction_envelope_from_xdr
from arcturus.utils import add_paging
from typing import (Union, Dict, Any)

async def get_details(horizon_url:str, hash:str):
    server = Server(horizon_url=horizon_url)
    builder = server.transactions().transaction(transaction_hash=hash)
    transaction = builder.call()
    del_extra_data(transaction)    
  
    return transaction

async def get_transactions(horizon_url:str, account_id:str, ledger_sequence:str, claimable_balance_id:str,
                           liquidity_pool_id:str, include_failed:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.transactions()
    if account_id is not None:
        builder = builder.for_account(account_id=account_id)
    elif ledger_sequence is not None:
        builder = builder.for_ledger(sequence=ledger_sequence)
    elif claimable_balance_id is not None:
        builder = builder.for_claimable_balance(claimable_balance_id=claimable_balance_id)
    elif liquidity_pool_id is not None:
        builder = builder.for_liquidity_pool(liquidity_pool_id=liquidity_pool_id)
        
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
        
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for transaction in records:
       del_extra_data(transaction=transaction)
       simplify_tx(transaction=transaction)
    
            
    return records

def del_extra_data(transaction:Dict[str, Any]):
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
    if 'memo_type' in transaction and transaction['memo_type'] == 'none':
        del transaction['memo_type']
        
    return transaction

def simplify_tx(transaction:Dict[str, Any]):
    # if many transactions are returned
    if 'inner_transaction' in transaction:
        del transaction['inner_transaction']
    if 'fee_bump_transaction' in transaction:
        del transaction['fee_bump_transaction']
    if 'signatures' in transaction:
        del transaction['signatures']
    if 'max_fee' in transaction:
        del transaction['max_fee']
    if 'fee_account' in transaction:
        del transaction['fee_account']
    if 'account_muxed_id' in transaction:
        del transaction['account_muxed_id']
    if 'preconditions' in transaction:
        del transaction['preconditions']
    if 'valid_after' in transaction:
        del transaction['valid_after']
    if 'memo_type' in transaction and transaction['memo_type'] == 'text':
        if 'memo_bytes' in transaction:
            del transaction['memo_bytes']
    if 'source_account_sequence' in transaction:
        del transaction['source_account_sequence']
    if 'ledger' in transaction:
        del transaction['ledger']

    return transaction

async def submit_tx(tx_xdr:str, horizon_url:str, network_passphrase:str):
    server = Server(horizon_url=horizon_url)
    transaction = parse_transaction_envelope_from_xdr(tx_xdr, network_passphrase)
    resp = server.submit_transaction(transaction)
    if 'successful' in resp:
        res = {'successful' : resp['successful']}
        if 'hash' in resp:
            res['hash'] = resp['hash']
        return res    

    return None