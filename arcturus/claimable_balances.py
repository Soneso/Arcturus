from stellar_sdk import Server, StrKey, TransactionBuilder
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk.exceptions import NotFoundError
from stellar_sdk.sep.stellar_uri import TransactionStellarUri
from arcturus.utils import add_paging, memo_from, db_add_signing_request
from typing import Union
import configparser
from arcturus.constants import APP_URL

async def get_claimable_balances(horizon_url:str, claimant_id:str, sponsor_id:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.claimable_balances()
    if claimant_id is not None:
        builder.for_claimant(claimant_id)
    if sponsor_id is not None:
        builder.for_sponsor(sponsor_id)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    for x in records:
        del x['_links']
    return records

async def claimable_balance(horizon_url:str, claimable_balance_id:str):
    server = Server(horizon_url=horizon_url)
    claimable_balances_call_builder = (
        server.claimable_balances().claimable_balance(claimable_balance_id)
    )
    claimable_balance = claimable_balances_call_builder.call()
    del claimable_balance['_links']
    return claimable_balance

async def claim_claimable_balance(horizon_url:str,
                                  network_passphrase: str,
                                  source: str,
                                  claimable_balance_id: str,
                                  memo: Union[str, None],
                                  memo_type: Union[str, None],
                                  base_fee: Union[int, None]) -> str :
    
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
    
    tx_builder = TransactionBuilder(source_account=source_account, network_passphrase=network_passphrase, 
                            base_fee=tx_base_fee).append_claim_claimable_balance_op(balance_id=claimable_balance_id)
    if memo is not None:
        tx_builder.add_memo(memo)
        
    tx = tx_builder.build()
    
    tx_envelope = TransactionEnvelope.from_xdr(tx.to_xdr(), network_passphrase= network_passphrase)
    config = configparser.ConfigParser()
    config.read('signing.ini')
    secret = config['signing']['secret']
    tx_uri_builder = TransactionStellarUri(transaction_envelope = tx_envelope, network_passphrase = network_passphrase)
    tx_uri_builder.sign(secret)
    sep7_tx_uri = tx_uri_builder.to_uri()
    key = db_add_signing_request(sep7_tx_uri)
    tx_link = f"{APP_URL}/sign_tx/{key}"
    return tx_link