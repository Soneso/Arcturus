from stellar_sdk import Server, StrKey, TransactionBuilder
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk.exceptions import NotFoundError
from stellar_sdk.sep.stellar_uri import TransactionStellarUri
from arcturus.utils import asset_from, memo_from, APP_URL
from typing import Union
from decimal import Decimal

ASSET_CODE = 'asset_code'
ASSET_ISSUER = 'asset_issuer'
NUM_ACCOUNTS = 'num_accounts'

async def get_assets(horizon_url:str, asset_issuer_id:str, asset_code:str):
    server = Server(horizon_url=horizon_url)
    builder = server.assets()
    
    if asset_issuer_id is not None:
        builder = builder.for_issuer(asset_issuer_id)
    if asset_code is not None:
        builder = builder.for_code(asset_code)
        
    records = builder.call()["_embedded"]["records"]
    result = []
    for x in records:
        if ASSET_CODE in x and ASSET_ISSUER in x and NUM_ACCOUNTS in x:
            result.append(x[ASSET_CODE] + ':' + x[ASSET_ISSUER] + ' / ' + str(x[NUM_ACCOUNTS]) + ' trustlines')
        
    return result

async def get_details(horizon_url:str, asset_issuer_id:str, asset_code:str):
    server = Server(horizon_url=horizon_url)
    builder = server.assets().for_issuer(asset_issuer_id).for_code(asset_code)
    records = builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records

async def trust_asset(horizon_url:str,
                      network_passphrase: str, 
                      source: str,
                      asset_code: str, 
                      asset_issuer: str,
                      limit: Union[Decimal, None],
                      memo_type: Union[str, None],
                      memo: Union[str, None],
                      base_fee: Union[int, None]) :
    
    asset = asset_from(asset_code=asset_code, asset_issuer=asset_issuer)
    memo = memo_from(memo=memo, memo_type=memo_type)
    if not StrKey.is_valid_ed25519_public_key(source):
        raise ValueError("Invalid source account Id")

    server = Server(horizon_url=horizon_url)
    source_account = None
    try:
        source_account = server.load_account(account_id=source)
    except NotFoundError:
        raise ValueError("Source account not found on the stellar network")
    except Exception:
        raise ValueError("An error occured while trying to load data for the source account from stellar network")
    
    tx_base_fee = 100
    if base_fee is not None:
        tx_base_fee = base_fee
        
    tx = TransactionBuilder(source_account=source_account, network_passphrase=network_passphrase, 
                            base_fee=tx_base_fee).append_change_trust_op(asset=asset, limit=limit).build()
    
    tx_envelope = TransactionEnvelope.from_xdr(tx.to_xdr(), network_passphrase= network_passphrase)
    # xdr = tx_envelope.to_xdr()
    # print(xdr)
    tx_uri_builder = TransactionStellarUri(transaction_envelope = tx_envelope, network_passphrase = network_passphrase)
    spe7_tx_uri = tx_uri_builder.to_uri()
    tx_link = spe7_tx_uri.replace("web+stellar:", APP_URL + "/")
    return tx_link