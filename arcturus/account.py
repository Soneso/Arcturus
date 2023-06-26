from stellar_sdk import Server, MuxedAccount

async def get_details(horizon_url, account_id):
    server = Server(horizon_url=horizon_url)
    account = server.load_account(account_id=account_id)
    del account.raw_data['_links']
    return account.raw_data

async def encodeMuxed(account_id, user_id):
    muxed = MuxedAccount(account_id=account_id, account_muxed_id=int(user_id))
    return muxed.account_muxed

async def decodeMuxed(muxed_account_id):
    muxed = MuxedAccount.from_account(muxed_account_id)
    data = {}
    data['account_id'] = muxed.account_id
    data['user_id'] = muxed.account_muxed_id
    return data