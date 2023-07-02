from stellar_sdk import Server

async def get_details(horizon_url, hash):
    server = Server(horizon_url=horizon_url)
    builder = server.transactions().transaction(transaction_hash=hash)
    transaction = builder.call()
    del transaction['_links']
    
    # delete data that we do not need at this time to save on context window
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