from stellar_sdk import Server

async def for_claimant(horizon_url, claimant_id):
    server = Server(horizon_url=horizon_url)
    records = []
    claimable_balances_call_builder = (
    server.claimable_balances().for_claimant(claimant_id).order(desc=False).limit(200)
    )
    records += claimable_balances_call_builder.call()["_embedded"]["records"]
    page_count = 0
    while page_records := claimable_balances_call_builder.next()["_embedded"]["records"]:
        records += page_records
        print(f"Page {page_count} fetched")
        print(f"data: {page_records}")
        page_count += 1 
    return records

async def for_sponsor(horizon_url, sponsor_id):
    server = Server(horizon_url=horizon_url)
    records = []
    claimable_balances_call_builder = (
    server.claimable_balances().for_sponsor(sponsor_id).order(desc=False).limit(200)
    )
    records += claimable_balances_call_builder.call()["_embedded"]["records"]
    page_count = 0
    while page_records := claimable_balances_call_builder.next()["_embedded"]["records"]:
        records += page_records
        print(f"Page {page_count} fetched")
        print(f"data: {page_records}")
        page_count += 1 
    return records

async def claimable_balance(horizon_url, claimable_balance_id):
    server = Server(horizon_url=horizon_url)
    claimable_balances_call_builder = (
        server.claimable_balances().claimable_balance(claimable_balance_id)
    )
    claimable_balance = claimable_balances_call_builder.call()
    return claimable_balance