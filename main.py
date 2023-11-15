import json

import quart
import quart_cors
from quart import request
import arcturus.account as account
import arcturus.assets as assets
import arcturus.claimable_balances as claimable_balances
import arcturus.payments as payments
import arcturus.transactions as transactions
import arcturus.operations as operations
import arcturus.offers as offers
import arcturus.liquidity_pools as liquidity_pools
import arcturus.orderbook as orderbook
import arcturus.trades as trades
import arcturus.domains as domains
import arcturus.scval as scval
import arcturus.soroban as soroban
import stellar_sdk.sep.stellar_toml as stellar_toml
from stellar_sdk.exceptions import NotFoundError
from stellar_sdk.sep.exceptions import StellarTomlNotFoundError

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

HORIZON_PUBLIC_URL = "https://horizon.stellar.org"
PUBLIC_NETWORK_PASSPHRASE: str = "Public Global Stellar Network ; September 2015"
HORIZON_TESTNET_URL = "https://horizon-testnet.stellar.org"
TESTNET_NETWORK_PASSPHRASE: str = "Test SDF Network ; September 2015"
HORIZON_FUTURENET_URL = "https://horizon-futurenet.stellar.org"
FUTURENET_NETWORK_PASSPHRASE: str = "Test SDF Future Network ; October 2022"
SOROBAN_RPC_FUTURENET_URL = "https://soroban-futurenet.stellar.org"
SOROBAN_RPC_TESTNET_URL = "https://soroban-testnet.stellar.org"
ACCOUNT_NOT_FOUND = "Account not found"
ASSET_NOT_FOUND = "Asset not found"
TRANSACTION_NOT_FOUND = "Transaction not found"
LEDGER_NOT_FOUND = "Ledger not found"
LIQUIDITY_POOL_NOT_FOUND = "Liquidity pool not found"
OPERATION_NOT_FOUND = "Operation not found"
OFFER_NOT_FOUND = "Offer not found"
CONTRACT_NOT_FOUND = "Contract not found"
NO_ENTRY_FOUND = "No entry found"
INVALID_ARGUMENT = "Invalid argument"
CLAIMABLE_BALANCE_NOT_FOUND = "Claimable Balance not found"
STELLAR_TOML_NOT_FOUND = "stellar.toml not found"

# we have to limit the size of the response because it counts as a part of the context window of ChatGPT
# it is now very limited but will expand dramatically in the future.
MAX_PAGING_LIMIT = 5
PAGING_LIMIT_EXCEEDED = "Paging limit too high."

@app.get("/account/details")
async def account_details():
    try:
        account_id = request.args.get('account_id')
        network = request.args.get('network')
        details = await account.get_details(horizon_url_for_network(network), account_id)
        print(f"details: {details}")
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/account/encode_muxed")
async def account_encode_muxed():
    try:
        account_id = request.args.get('account_id')
        user_id = request.args.get('user_id')
        muxed = await account.encode_muxed(account_id=account_id, user_id=user_id)
    except Exception as e:
        print("An exception occurred:", e)
        return quart.Response(response=INVALID_ARGUMENT, status=400)
    else:
        return quart.Response(response=muxed, status=200)

@app.get("/account/decode_muxed")
async def account_decode_muxed():
    try:
        muxed_account_id = request.args.get('muxed_account_id')
        data = await account.decode_muxed(muxed_account_id)
    except Exception as e:
        print("An exception occurred:", e)
        return quart.Response(response=INVALID_ARGUMENT, status=400)
    else:
        return quart.Response(response=json.dumps(data), status=200)
    
@app.get("/account/directory_info")
async def account_directory_info():
    account_id = request.args.get('account_id')
    data = await account.directory_info(account_id)
    if len(data) == 0:
        return quart.Response(response=NO_ENTRY_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(data), status=200)
    
@app.get("/assets")
async def get_assets():
    try:
        issuer_account_id = request.args.get('issuer_account_id')
        asset_code = request.args.get('asset_code')
        network = request.args.get('network')
        records = await assets.get_assets(horizon_url_for_network(network), issuer_account_id, asset_code)
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/asset/details")
async def asset_details():
    try:
        issuer_account_id = request.args.get('issuer_account_id')
        asset_code = request.args.get('asset_code')
        network = request.args.get('network')
        records = await assets.get_details(horizon_url_for_network(network), issuer_account_id, asset_code)
    except NotFoundError:
        return quart.Response(response=ASSET_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.post("/asset/trust")
async def trust_asset():
    try:
        request = await quart.request.get_json(force=True)
        if "network" not in request:
            raise Exception("missing network parameter")
        if "source_account" not in request:
            raise Exception("missing source_account parameter")
        if "asset_code" not in request:
            raise Exception("missing asset_code parameter")
        if "asset_issuer" not in request:
            raise Exception("missing asset_issuer parameter")
        
        network = request["network"]
        horizon_url = horizon_url_for_network(network=network)
        passphrase = passphrase_for_network(network=network)
        source_account = request["source_account"]
        asset_code = request["asset_code"]
        asset_issuer = request["asset_issuer"]
            
        memo_type = None
        if "memo_type" in request:
            memo_type = request["memo_type"]
        memo = None
        if "memo" in request:
            memo = request["memo"]
            
        limit = None
        if "limit" in request:
            limit = request["limit"]
            
        base_fee = None
        if "base_fee" in request:
            base_fee = request["base_fee"]
        
        res = await assets.trust_asset(horizon_url=horizon_url, network_passphrase=passphrase, source=source_account, asset_code=asset_code, asset_issuer=asset_issuer, limit=limit, memo_type=memo_type, memo=memo, base_fee=base_fee)
        if res is not None:
            return quart.Response(response=res, status=200)
        raise Exception("an unknown error occured while preparing the trust asset transaction")
    except Exception as e:
        return quart.Response(response=str(e), status=400)
    
@app.get("/claimable_balances")
async def get_claimable_balances():
    try:
        claimant_account_id = request.args.get('claimant_account_id')
        sponsor_account_id = request.args.get('sponsor_account_id')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        
        if limit is None:
            limit = 2
        
        if int(limit) > 2:
            return quart.Response(response=PAGING_LIMIT_EXCEEDED, status=400)
        records = await claimable_balances.get_claimable_balances(horizon_url_for_network(network), claimant_account_id, sponsor_account_id, cursor, order, limit)
            
    except NotFoundError:
        return quart.Response(response=ACCOUNT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/claimable_balances/claimable_balance")
async def claimable_balance():
    try:
        claimable_balance_id = request.args.get('claimable_balance_id')
        network = request.args.get('network')
        details = await claimable_balances.claimable_balance(horizon_url_for_network(network), claimable_balance_id)
    except NotFoundError:
        return quart.Response(response=CLAIMABLE_BALANCE_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/stellar_toml/<string:domain>")
async def get_stellar_toml(domain):
    try:
        details = stellar_toml.fetch_stellar_toml(domain)
    except StellarTomlNotFoundError:
        return quart.Response(response=STELLAR_TOML_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/payments")
async def get_payments():
    try:
        account_id = request.args.get('account_id')
        transaction_hash = request.args.get('transaction_hash')
        ledger_sequence = request.args.get('ledger_sequence')
        include_failed = request.args.get('include_failed')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        
        if limit is None:
            limit = MAX_PAGING_LIMIT
        if int(limit) > MAX_PAGING_LIMIT:
            return quart.Response(response=PAGING_LIMIT_EXCEEDED, status=400)
        records = []
        
        if account_id is not None:
            records = await payments.for_account(horizon_url=horizon_url_for_network(network), account_id=account_id, 
                                                 include_failed=include_failed,cursor=cursor, order=order, limit=limit)
        else:
            records = await payments.get_payments(horizon_url=horizon_url_for_network(network),transaction_hash=transaction_hash,
                                                  ledger_sequence=ledger_sequence, include_failed=include_failed, 
                                                  cursor=cursor, order=order, limit=limit)
    except NotFoundError as nfe:
        return quart.Response(response=nfe.message, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)
    
@app.get("/payment/details")
async def payment_details():
    return await op_details(request=request)

@app.post("/payment/send")
async def send_payment():
    try:
        request = await quart.request.get_json(force=True)
        if "network" not in request:
            raise Exception("missing network parameter")
        if "destination_account" not in request:
            raise Exception("missing destination_account parameter")
        if "amount" not in request:
            raise Exception("missing amount parameter")
        
        network = request["network"]
        destination_account = request["destination_account"]
        amount = request["amount"]
        passphrase = passphrase_for_network(network=network)
            
        memo_type = None
        if "memo_type" in request:
            memo_type = request["memo_type"]
        memo = None
        if "memo" in request:
            memo = request["memo"]
            
        asset_code = "native"
        if "asset_code" in request:
            asset_code = request["asset_code"]
        
        asset_issuer = None
        if "asset_issuer" in request:
            asset_issuer = request["asset_issuer"]
        
        res = await payments.send_payment(network_passphrase=passphrase,destination=destination_account, 
                                          amount=amount, asset_code=asset_code, asset_issuer=asset_issuer,
                                          memo_type=memo_type, memo=memo)
        if res is not None:
            return quart.Response(response=res, status=200)
        raise Exception("an unknown error occured while preparing the payment")
    except Exception as e:
        return quart.Response(response=str(e), status=400)

@app.get("/transaction/details")
async def transaction_details():
    try:
        t_id = request.args.get('hash')
        network = request.args.get('network')
        details = await transactions.get_details(horizon_url_for_network(network), t_id)
    except NotFoundError:
        return quart.Response(response=TRANSACTION_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/transactions")
async def get_transactions():
    try:
        account_id = request.args.get('account_id')
        liquidity_pool_id = request.args.get('liquidity_pool_id')
        ledger_sequence = request.args.get('ledger_sequence')
        claimable_balance_id = request.args.get('claimable_balance_id')
        network = request.args.get('network')
        include_failed = request.args.get('include_failed')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        if limit is None:
            limit = MAX_PAGING_LIMIT
        if int(limit) > MAX_PAGING_LIMIT:
            return quart.Response(response=PAGING_LIMIT_EXCEEDED, status=400)
        records = await transactions.get_transactions(horizon_url=horizon_url_for_network(network), account_id=account_id,
                                                      liquidity_pool_id=liquidity_pool_id, ledger_sequence=ledger_sequence,
                                                      claimable_balance_id=claimable_balance_id, include_failed=include_failed,
                                                      cursor=cursor, order=order, limit=limit)
    except NotFoundError as nfe:
        return quart.Response(response=nfe.message, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.post("/transaction/submit_tx_xdr")
async def submit_tx_xdr():
    try:
        request = await quart.request.get_json(force=True)
        if "network" not in request:
            raise Exception("missing network parameter")
        if "xdr" not in request:
            raise Exception("missing xdr parameter")
        network = request["network"]
        xdr = request["xdr"]
        passphrase = passphrase_for_network(network=network)
        horizon_url = horizon_url_for_network(network)
        res = await transactions.submit_tx(tx_xdr=xdr, horizon_url=horizon_url, network_passphrase=passphrase)
        if res is not None:
            return quart.Response(response=json.dumps(res), status=200)
        raise Exception("an unknown error occured while submitting the transaction")
    except Exception as e:
        return quart.Response(response=str(e), status=400)

@app.get("/operations")
async def get_operations():
    try:
        account_id = request.args.get('account_id')
        liquidity_pool_id = request.args.get('liquidity_pool_id')
        ledger_sequence = request.args.get('ledger_sequence')
        claimable_balance_id = request.args.get('claimable_balance_id')
        transaction_hash = request.args.get('transaction_hash')
        include_failed = request.args.get('include_failed')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        if limit is None:
            limit = MAX_PAGING_LIMIT
        if int(limit) > MAX_PAGING_LIMIT:
            return quart.Response(response=PAGING_LIMIT_EXCEEDED, status=400)
        records = []
        
        records = await operations.get_operations(horizon_url = horizon_url_for_network(network), account_id = account_id,
                                                  ledger_sequence = ledger_sequence, liquidity_pool_id = liquidity_pool_id,
                                                  claimable_balance_id = claimable_balance_id, transaction_hash = transaction_hash,
                                                  include_failed = include_failed, cursor = cursor, order = order, limit = limit)
    except NotFoundError as nfe:
        return quart.Response(response=nfe.message, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/operation/details")
async def operation_details():
    return await op_details(request=request)

@app.get("/offers")
async def get_offers():
    try:
        account_id = request.args.get('account_id')
        seller_id = request.args.get('seller_id')
        sponsor_id = request.args.get('sponsor_id')
        selling_asset_code = request.args.get('selling_asset_code')
        selling_asset_issuer = request.args.get('selling_asset_issuer')
        buying_asset_code = request.args.get('buying_asset_code')
        buying_asset_issuer = request.args.get('buying_asset_issuer')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        
        if limit is None:
            limit = 3
        if int(limit) > 3:
            return quart.Response(response=PAGING_LIMIT_EXCEEDED, status=400)
        
        records = []
        if account_id is not None:
            records = await offers.for_account(horizon_url_for_network(network), account_id, cursor, order, limit)
        else:
            records = await offers.all_offers(horizon_url_for_network(network), seller_id = seller_id, sponsor_id= sponsor_id,
                                              selling_asset_code = selling_asset_code, selling_asset_issuer= selling_asset_issuer,
                                              buying_asset_code = buying_asset_code, buying_asset_issuer= buying_asset_issuer,
                                              cursor=cursor, order=order, limit=limit)
    except Exception as e:
        return quart.Response(response=str(e), status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/offer/details")
async def offer_details():
    try:
        offer_id = request.args.get('offer_id')
        network = request.args.get('network')
        details = await offers.get_details(horizon_url_for_network(network), offer_id)
    except NotFoundError:
        return quart.Response(response=OFFER_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/orderbook")
async def get_orderbook():
    try:
        selling_asset_code = request.args.get('selling_asset_code')
        selling_asset_issuer = request.args.get('selling_asset_issuer')
        buying_asset_code = request.args.get('buying_asset_code')
        buying_asset_issuer = request.args.get('buying_asset_issuer')
        network = request.args.get('network')
        entries = await orderbook.orderbook(horizon_url_for_network(network),selling_asset_code = selling_asset_code, 
                                            selling_asset_issuer= selling_asset_issuer, buying_asset_code = buying_asset_code, 
                                            buying_asset_issuer= buying_asset_issuer)
    except Exception as e:
        return quart.Response(response=str(e), status=404)
    else:
        return quart.Response(response=json.dumps(entries), status=200)

@app.get("/trades")
async def get_trades():
    try:
        base_asset_code = request.args.get('base_asset_code')
        base_asset_issuer = request.args.get('base_asset_issuer')
        counter_asset_code = request.args.get('counter_asset_code')
        counter_asset_issuer = request.args.get('counter_asset_issuer')
        account_id = request.args.get('account_id')
        offer_id = request.args.get('offer_id')
        liquidity_pool_id = request.args.get('liquidity_pool_id')
        trade_type = request.args.get('trade_type')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        
        if limit is None:
            limit = 3
        if int(limit) > 3:
            return quart.Response(response=PAGING_LIMIT_EXCEEDED, status=400)
    
        if account_id is not None:
            records = await trades.for_account(horizon_url=horizon_url_for_network(network),account_id=account_id, 
                                               trade_type=trade_type, cursor=cursor, order=order, limit=limit)
        elif liquidity_pool_id is not None:
            records = await trades.for_liquidity_pool(horizon_url=horizon_url_for_network(network),liquidity_pool_id=liquidity_pool_id,
                                                      cursor=cursor, order=order, limit=limit)
        elif offer_id is not None and base_asset_code is None and counter_asset_code is None:
            records = await trades.for_offer(horizon_url=horizon_url_for_network(network),offer_id=offer_id,
                                                      cursor=cursor, order=order, limit=limit)
        else:
            records = await trades.all_trades(horizon_url=horizon_url_for_network(network),base_asset_code=base_asset_code, base_asset_issuer=base_asset_issuer,
                                              counter_asset_code=counter_asset_code, counter_asset_issuer=counter_asset_issuer,offer_id=offer_id, trade_type=trade_type,
                                              cursor=cursor, order=order, limit=limit)
    except Exception as e:
        return quart.Response(response=str(e), status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/liquidity_pools")
async def get_liquidity_pools():
    try:
        account_id = request.args.get('account_id')
        reserves = request.args.get('reserves')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        order = request.args.get('order')
        limit = request.args.get('limit')
        
        if limit is None:
            limit = MAX_PAGING_LIMIT
        if int(limit) > MAX_PAGING_LIMIT:
            return quart.Response(response=PAGING_LIMIT_EXCEEDED, status=400)
        
        records = await liquidity_pools.get_liquidity_pools(horizon_url=horizon_url_for_network(network), account_id=account_id, 
                                                            reserves=reserves, cursor=cursor, order=order, limit=limit)
            
    except Exception as e:
        return quart.Response(response=str(e), status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/liquidity_pool/details")
async def liquidity_pool_details():
    try:
        liquidity_pool_id = request.args.get('liquidity_pool_id')
        network = request.args.get('network')
        details = await liquidity_pools.get_details(horizon_url=horizon_url_for_network(network), 
                                                    liquidity_pool_id=liquidity_pool_id)
    except NotFoundError:
        return quart.Response(response=LIQUIDITY_POOL_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)
    
@app.get("/blocked_domains/<string:domain>")
async def get_blocked_domains(domain):
    details = await domains.blocked_domains(domain)
    return quart.Response(response=json.dumps(details), status=200)

@app.get("/scval/decode")
async def scval_decode():
    try:
        base64_xdr = request.args.get('encoded_scval')
        data = scval.decode_scval(base64_xdr=base64_xdr)
    except Exception as e:
        print("An exception occurred:", e)
        return quart.Response(response=INVALID_ARGUMENT, status=400)
    else:
        return quart.Response(response=json.dumps(data), status=200)
    
@app.get("/scval/xdr_for")
async def scval_xdr_for():
    try:
        scval_type = request.args.get('type')
        value = request.args.get('value')
        data = scval.xdr_for(scval_type, value)
    except Exception as e:
        print("An exception occurred:", e)
        return quart.Response(response=INVALID_ARGUMENT, status=400)
    else:
        return quart.Response(response=data, status=200)

@app.get("/soroban/get_latest_ledger")
async def soroban_get_latest_ledger():
    network = request.args.get('network')
    data = await soroban.get_latest_ledger(soroban_rpc_url_for_network(network))
    return quart.Response(response=json.dumps(data), status=200)

@app.get("/soroban/contract_events")
async def soroban_contract_events():
    try:
        contract_id = request.args.get('contract_id')
        start_ledger = request.args.get('start_ledger')
        network = request.args.get('network')
        cursor = request.args.get('cursor')
        limit = request.args.get('limit')
        if int(limit) > 10:
            return quart.Response(response=PAGING_LIMIT_EXCEEDED, status=400)
        records = await soroban.contract_events(soroban_rpc_url_for_network(network), start_ledger, contract_id, cursor, limit)
    except NotFoundError:
        return quart.Response(response=CONTRACT_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(records), status=200)

@app.get("/soroban/contract_data")
async def soroban_contract_data():
    try:
        contract_id = request.args.get('contract_id')
        key = request.args.get('key')
        durability = request.args.get('durability')
        network = request.args.get('network')
        result = await soroban.contract_data(soroban_rpc_url_for_network(network), contract_id, key, durability)
        if result == None:
            return quart.Response(response=NO_ENTRY_FOUND, status=404)
        else:
            return quart.Response(response=json.dumps(result), status=200)
    except Exception:
        return quart.Response(response=NO_ENTRY_FOUND, status=404)    

@app.get("/soroban/contract_code")
async def soroban_contract_code():
    try:
        contract_id = request.args.get('contract_id')
        wasm_id = request.args.get('wasm_id')
        network = request.args.get('network')
        result = None
        if wasm_id is not None:
            result = await soroban.contract_code_for_wasm_id(soroban_rpc_url_for_network(network), wasm_id)
        elif contract_id is not None:
            result = await soroban.contract_code_for_contract_id(soroban_rpc_url_for_network(network), contract_id=contract_id)
        
        if result == None:
            return quart.Response(response=NO_ENTRY_FOUND, status=404)
        else:
            return quart.Response(response=json.dumps(result), status=200)
    except Exception:
        return quart.Response(response=NO_ENTRY_FOUND, status=404)

@app.get("/soroban/contract_meta")
async def soroban_contract_meta():
    try:

        contract_id = request.args.get('contract_id')
        wasm_id = request.args.get('wasm_id')
        network = request.args.get('network')
        result = await soroban.contract_meta(soroban_rpc_url_for_network(network), wasm_id=wasm_id, contract_id=contract_id)
        
        if result == None:
            return quart.Response(response=NO_ENTRY_FOUND, status=404)
        else:
            return quart.Response(response=json.dumps(result), status=200)
    except Exception:
        return quart.Response(response=NO_ENTRY_FOUND, status=404)
    
@app.get("/soroban/get_transaction_status")
async def get_soroban_transaction_status():
    transaction_hash = request.args.get('transaction_id')
    network = request.args.get('network')
    result = await soroban.transaction_status(soroban_rpc_url_for_network(network), transaction_hash=transaction_hash)
    return quart.Response(response=result, status=200)
    
@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/arcturus-pp.html")
async def arcturus_pp():
    filename = 'arcturus-pp.html'
    return await quart.send_file(filename, mimetype='text/html')

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
                 'openapi/path/stellar_toml.yaml',
                 'openapi/path/claimable_balances.yaml',
                 'openapi/path/payments.yaml',
                 'openapi/path/transactions.yaml',
                 'openapi/path/operations.yaml',
                 'openapi/path/domains.yaml',
                 'openapi/path/offers.yaml',
                 'openapi/path/orderbook.yaml',
                 'openapi/path/scval.yaml',
                 'openapi/path/soroban.yaml',
                 'openapi/path/trades.yaml',
                 'openapi/path/liquidity_pools.yaml',
                 'openapi/components/accounts.yaml',
                 'openapi/components/assets.yaml',
                 'openapi/components/stellar_toml.yaml',
                 'openapi/components/claimable_balances.yaml',
                 'openapi/components/payments.yaml',
                 'openapi/components/transactions.yaml',
                 'openapi/components/operations.yaml',
                 'openapi/components/domains.yaml',
                 'openapi/components/offers.yaml',
                 'openapi/components/orderbook.yaml',
                 'openapi/components/scval.yaml', 
                 'openapi/components/soroban.yaml',
                 'openapi/components/trades.yaml',
                 'openapi/components/liquidity_pools.yaml']
    combined_text = combine_files(file_list)
    print(combined_text)
    return quart.Response(combined_text, mimetype="text/yaml")

def horizon_url_for_network(network:str):
    if network == 'public':
        return HORIZON_PUBLIC_URL
    if network == 'testnet':
        return HORIZON_TESTNET_URL
    if network == 'futurenet':
        return HORIZON_FUTURENET_URL
    return network

def passphrase_for_network(network:str):
    if network == 'public':
        return PUBLIC_NETWORK_PASSPHRASE
    if network == 'testnet':
        return TESTNET_NETWORK_PASSPHRASE
    if network == 'futurenet':
        return FUTURENET_NETWORK_PASSPHRASE
    return PUBLIC_NETWORK_PASSPHRASE

def soroban_rpc_url_for_network(network:str):
    if network == 'testnet':
        return SOROBAN_RPC_TESTNET_URL
    return SOROBAN_RPC_FUTURENET_URL

def combine_files(file_list):
    combined_text = ''
    for file_name in file_list:
        with open(file_name, 'r') as file:
            file_text = file.read()
            combined_text += file_text + "\n"

    return combined_text

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

async def op_details(request):
    try:
        o_id = request.args.get('id')
        network = request.args.get('network')
        details = await operations.get_details(horizon_url_for_network(network), o_id)
        print(f"details: {details}")
    except NotFoundError:
        return quart.Response(response=OPERATION_NOT_FOUND, status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)
    
if __name__ == "__main__":
    main()
