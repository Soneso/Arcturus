from stellar_sdk import Server

async def for_issuer(horizon_url, asset_issuer_id):
    server = Server(horizon_url=horizon_url)
    records = []
    assets_call_builder = (
    server.assets().for_issuer(asset_issuer_id).order(desc=False).limit(200)
    )
    records += assets_call_builder.call()["_embedded"]["records"]
    page_count = 0
    while page_records := assets_call_builder.next()["_embedded"]["records"]:
        records += page_records
        print(f"Page {page_count} fetched")
        print(f"data: {page_records}")
        page_count += 1 
    return records