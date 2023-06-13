import json

import quart
import quart_cors
from quart import request
import arcturus.account as account
import arcturus.assets as assets
import arcturus.claimable_balances as claimable_balances
from stellar_sdk.exceptions import NotFoundError

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

HORIZON_URL = "https://horizon-testnet.stellar.org"
ACCOUNT_NOT_FOUND = "Account not found"
CLAIMABLE_BALANCE_NOT_FOUND = "Claimable Balance not found"

@app.get("/account/details/<string:account_id>")
async def get_account_details(account_id):
    try:
        details = await account.get_details(HORIZON_URL, account_id)
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/assets/for_issuer/<string:issuer_account_id>")
async def get_assets_for_issuer(issuer_account_id):
    try:
        records = await assets.for_issuer(HORIZON_URL, issuer_account_id)
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/claimable_balances/for_claimant/<string:claimant_account_id>")
async def get_claimable_balances_for_claimant(claimant_account_id):
    print("test: get claimable balances for claimant")
    try:
        records = await claimable_balances.for_claimant(HORIZON_URL, claimant_account_id)
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)
    
@app.get("/claimable_balances/for_sponsor/<string:sponsor_account_id>")
async def get_claimable_balances_for_sponsor(sponsor_account_id):
    print("test: get claimable balances for sponsor")
    try:
        records = await claimable_balances.for_sponsor(HORIZON_URL, sponsor_account_id)
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/claimable_balances/claimable_balance/<string:claimable_balance_id>")
async def get_claimable_balance(claimable_balance_id):
    print("test: get claimable balance for id")
    try:
        records = await claimable_balances.claimable_balance(HORIZON_URL, claimable_balance_id)
    except NotFoundError:
        return quart.Response(response=CLAIMABLE_BALANCE_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)
    
@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
