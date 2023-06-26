import json

import quart
import quart_cors
from quart import request
import arcturus.account as account
import arcturus.assets as assets
import arcturus.claimable_balances as claimable_balances
import arcturus.payments as payments
import arcturus.transactions as transactions
import stellar_sdk.sep.stellar_toml as stellar_toml
from stellar_sdk.exceptions import NotFoundError
from stellar_sdk.sep.exceptions import StellarTomlNotFoundError

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

HORIZON_PUBLIC_URL = "https://horizon.stellar.org"
HORIZON_TESTNET_URL = "https://horizon-testnet.stellar.org"
HORIZON_FUTURENET_URL = "https://horizon-futurenet.stellar.org"
ACCOUNT_NOT_FOUND = "Account not found"
INVALID_ARGUMENT = "Invalid argument"
CLAIMABLE_BALANCE_NOT_FOUND = "Claimable Balance not found"
STELLAR_TOML_NOT_FOUND = "stellar.toml not found"

@app.get("/account/details")
async def account_details():
    try:
        account_id = request.args.get('account_id')
        network = request.args.get('network')
        details = await account.get_details(horizon_url_for_network(network), account_id)
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/account/encode_muxed")
async def account_encode_muxed():
    try:
        account_id = request.args.get('account_id')
        user_id = request.args.get('user_id')
        print(f"encode {account_id} : {user_id}")
        muxed = await account.encodeMuxed(account_id=account_id, user_id=user_id)
    except Exception as e:
        print("An exception occurred:", e)
        return quart.Response(response=INVALID_ARGUMENT, status=400)
    else:
        return quart.Response(response=muxed, status=200)

@app.get("/account/decode_muxed")
async def account_decode_muxed():
    try:
        muxed_account_id = request.args.get('muxed_account_id')
        data = await account.decodeMuxed(muxed_account_id)
    except Exception as e:
        print("An exception occurred:", e)
        return quart.Response(response=INVALID_ARGUMENT, status=400)
    else:
        return quart.Response(response=json.dumps(data), status=200)
    
@app.get("/assets/for_issuer")
async def assets_for_issuer():
    try:
        issuer_account_id = request.args.get('issuer_account_id')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        records = await assets.for_issuer(horizon_url_for_network(network), issuer_account_id, cursor, order, limit)
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/claimable_balances/for_claimant")
async def claimable_balances_for_claimant():
    print("test: get claimable balances for claimant")
    try:
        claimant_account_id = request.args.get('claimant_account_id')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        records = await claimable_balances.for_claimant(horizon_url_for_network(network), claimant_account_id, cursor, order, limit)
        print(f"records: {records}")
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)
    
@app.get("/claimable_balances/for_sponsor")
async def claimable_balances_for_sponsor():
    print("test: get claimable balances for sponsor")
    try:
        sponsor_account_id = request.args.get('sponsor_account_id')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        records = await claimable_balances.for_sponsor(horizon_url_for_network(network), sponsor_account_id, cursor, order, limit)
        print(f"records: {records}")
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/claimable_balances/claimable_balance")
async def claimable_balance():
    print("test: get claimable balance for id")
    try:
        claimable_balance_id = request.args.get('claimable_balance_id')
        network = request.args.get('network')
        records = await claimable_balances.claimable_balance(horizon_url_for_network(network), claimable_balance_id)
    except NotFoundError:
        return quart.Response(response=CLAIMABLE_BALANCE_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/stellar_toml/<string:domain>")
async def get_stellar_toml(domain):
    print("test: get stellar toml")
    try:
        details = stellar_toml.fetch_stellar_toml(domain)
    except StellarTomlNotFoundError:
        return quart.Response(response=STELLAR_TOML_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/payments/for_account")
async def payments_for_account():
    print("test: get payments for account")
    try:
        account_id = request.args.get('account_id')
        include_failed = request.args.get('include_failed')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        records = await payments.for_account(horizon_url_for_network(network), account_id, include_failed, cursor, order, limit)
        print(f"records: {records}")
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)
    
@app.get("/transaction/details")
async def transaction_details():
    try:
        t_id = request.args.get('hash')
        network = request.args.get('network')
        details = await transactions.get_details(horizon_url_for_network(network), t_id)
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)
    
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
    file_list = ['openapi/info.yaml', 
                 'openapi/path/accounts.yaml',
                 'openapi/path/assets.yaml',
                 'openapi/path/claimable_balances.yaml',
                 'openapi/path/stellar_toml.yaml', 
                 'openapi/path/payments.yaml',
                 'openapi/path/transactions.yaml', 
                 'openapi/components/accounts.yaml',
                 'openapi/components/assets.yaml',
                 'openapi/components/claimable_balances.yaml',
                 'openapi/components/stellar_toml.yaml',
                 'openapi/components/payments.yaml',
                 'openapi/components/transactions.yaml']
    combined_text = combine_files(file_list)
    return quart.Response(combined_text, mimetype="text/yaml")

def horizon_url_for_network(network):
    if network == 'public':
        return HORIZON_PUBLIC_URL
    if network == 'testnet':
        return HORIZON_TESTNET_URL
    if network == 'futurenet':
        return HORIZON_FUTURENET_URL
    return network

def combine_files(file_list):
    combined_text = ''
    for file_name in file_list:
        with open(file_name, 'r') as file:
            file_text = file.read()
            combined_text += file_text + "\n"

    return combined_text

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
