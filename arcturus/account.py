from stellar_sdk import Server

async def get_details(horizon_url, account_id):
    server = Server(horizon_url=horizon_url)
    source_account = server.load_account(account_id=account_id)
    return source_account.raw_data