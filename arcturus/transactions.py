from stellar_sdk import Server

async def get_details(horizon_url, hash):
    server = Server(horizon_url=horizon_url)
    builder = server.transactions().transaction(transaction_hash=hash)
    transaction = builder.call()
    del transaction['_links']
    return transaction