from stellar_sdk import Server, MuxedAccount
import aiohttp

async def get_details(horizon_url:str, account_id:str):
    server = Server(horizon_url=horizon_url)
    account = server.load_account(account_id=account_id)
    del account.raw_data['_links']
    return account.raw_data

async def encode_muxed(account_id:str, user_id:str):
    muxed = MuxedAccount(account_id=account_id, account_muxed_id=int(user_id))
    return muxed.account_muxed

async def decode_muxed(muxed_account_id:str):
    muxed = MuxedAccount.from_account(muxed_account_id)
    data = {}
    data['account_id'] = muxed.account_id
    data['user_id'] = muxed.account_muxed_id
    return data
    
async def directory_info(account_id:str):
    url = f"https://api.stellar.expert/explorer/directory/{account_id}"
    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url)
        return response
    
async def fetch(session, url):
    async with session.get(url, ssl=False) as response:
        return await response.json()