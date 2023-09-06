import aiohttp

async def blocked_domains(domain:str):
    url = f"https://api.stellar.expert/explorer/directory/blocked-domains/{domain}"
    print(url)
    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url)
        return response
    
async def fetch(session, url):
    async with session.get(url, ssl=False) as response:
        return await response.json()