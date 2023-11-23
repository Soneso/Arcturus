from stellar_sdk import Server
from stellar_sdk.sep.stellar_uri import PayStellarUri
from arcturus.utils import add_paging, delete_keys_except, replace_key, memo_from, asset_from, APP_URL, db_add_signing_request, db_get_signing_request
from typing import (Union, Dict, Any, List)
import configparser

ID_KEY = 'id'
TYPE_KEY = 'type'
CREATED_AT_KEY = 'created_at'
TX_HASH_KEY = 'transaction_hash'
TX_SUCCESSFUL_KEY = 'transaction_successful'
SUCCESSFUL_KEY = 'successful'
TO_KEY = 'to'
FROM_KEY = 'from'
AMOUNT_KEY = 'amount'
ASSET_TYPE_KEY = 'asset_type'
ASSET_CODE_KEY = 'asset_code'
ASSET_ISSUER_KEY = 'asset_issuer'
STARTING_BALANCE_KEY = 'starting_balance'
FUNDER_KEY = 'funder'
ACCOUNT_KEY = 'account'
INTO_KEY = 'into'
SOURCE_AMOUNT_KEY = 'source_amount'
SOURCE_ASSET_TYPE_KEY = 'source_asset_type'
SOURCE_ASSET_CODE_KEY = 'source_asset_code'
SOURCE_ASSET_ISSUER_KEY = 'source_asset_issuer'
AMOUNT_RECEIVED_KEY = 'amount_received'
AMOUNT_SENT_KEY = 'amount_sent'

PAGIN_TOKEN_KEY = 'paging_token'

TYPE_CREATE_ACCOUNT = 'create_account'
TYPE_ACCOUNT_MERGE = 'account_merge'
TYPE_PAYMENT = 'payment'
TYPE_PATH_PAYMENT_STRICT_SEND = 'path_payment_strict_send'
TYPE_PATH_PAYMENT_STRICT_RECEIVE = 'path_payment_strict_receive'
  
KEYS_TO_KEEP = [ID_KEY, TYPE_KEY, TX_HASH_KEY, SUCCESSFUL_KEY, CREATED_AT_KEY, FROM_KEY, TO_KEY, AMOUNT_RECEIVED_KEY, AMOUNT_SENT_KEY, AMOUNT_KEY, PAGIN_TOKEN_KEY]

async def for_account(horizon_url:str, account_id:str, include_failed:bool, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.payments().for_account(account_id)
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for payment in records:
        if TYPE_KEY in payment and TYPE_CREATE_ACCOUNT == payment[TYPE_KEY]:
            simplify_create_account_payment(payment=payment, account_id=account_id)
        elif TYPE_KEY in payment and TYPE_ACCOUNT_MERGE == payment[TYPE_KEY]:
            simplify_account_merge_payment(payment=payment, account_id=account_id)
        elif TYPE_KEY in payment and TYPE_PAYMENT == payment[TYPE_KEY]:
            simplify_standard_payment(payment=payment, account_id=account_id)
        elif TYPE_KEY in payment and TYPE_PATH_PAYMENT_STRICT_SEND == payment[TYPE_KEY]:
            simplify_path_payment(payment=payment, account_id=account_id)
        elif TYPE_KEY in payment and TYPE_PATH_PAYMENT_STRICT_RECEIVE == payment[TYPE_KEY]:
            simplify_path_payment(payment=payment, account_id=account_id)
        
        del payment['_links']
        replace_key(payment, TX_SUCCESSFUL_KEY, SUCCESSFUL_KEY)
        delete_keys_except(payment, KEYS_TO_KEEP)
        
    payments = {}
    payments['payments'] = records
    return payments

async def get_payments(horizon_url:str, transaction_hash:str, ledger_sequence:Union[int, str], include_failed:bool, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.payments()
    if transaction_hash is not None:
        builder = builder.for_transaction(transaction_hash=transaction_hash)
    elif ledger_sequence is not None:
        builder = builder.for_ledger(sequence=ledger_sequence)
        
    if include_failed is not None and include_failed is True:
        builder.include_failed(include_failed=True)
    else:
        builder.include_failed(include_failed=False)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for payment in records:
        if TYPE_KEY in payment and TYPE_CREATE_ACCOUNT == payment[TYPE_KEY]:
            payment[FROM_KEY] = payment[FUNDER_KEY]
            payment[TO_KEY] = payment[ACCOUNT_KEY]
        elif TYPE_KEY in payment and TYPE_ACCOUNT_MERGE == payment[TYPE_KEY]:
            payment[TO_KEY] = payment[INTO_KEY]
            payment[FROM_KEY] = payment[ACCOUNT_KEY]
        elif TYPE_KEY in payment and TYPE_PAYMENT == payment[TYPE_KEY]:
            canonic_amount(payment=payment)
        elif TYPE_KEY in payment and (TYPE_PATH_PAYMENT_STRICT_SEND == payment[TYPE_KEY] 
                                      or TYPE_PATH_PAYMENT_STRICT_RECEIVE == payment[TYPE_KEY]):
            canonic_source_amount(payment=payment)
            replace_key(payment, SOURCE_AMOUNT_KEY, AMOUNT_SENT_KEY)
            canonic_amount(payment=payment)
            replace_key(payment, AMOUNT_KEY, AMOUNT_RECEIVED_KEY)
        
        del payment['_links']
        replace_key(payment, TX_SUCCESSFUL_KEY, SUCCESSFUL_KEY)
        delete_keys_except(payment, KEYS_TO_KEEP)
        
    payments = {}
    payments['payments'] = records
    return payments

def simplify_standard_payment(payment:Dict[str, Any], account_id:str):
    canonic_amount(payment=payment)
    if FROM_KEY in payment and payment[FROM_KEY] == account_id:
        replace_key(payment, AMOUNT_KEY, AMOUNT_SENT_KEY)
        del payment[FROM_KEY]
    elif TO_KEY in payment and payment[TO_KEY] == account_id:
        replace_key(payment, AMOUNT_KEY, AMOUNT_RECEIVED_KEY)
        del payment[TO_KEY]

def canonic_amount(payment:Dict[str, Any]):
    if AMOUNT_KEY in payment:
        amount = payment[AMOUNT_KEY]
        if ASSET_CODE_KEY in payment:
            amount += " " + payment[ASSET_CODE_KEY];
            del payment[ASSET_CODE_KEY]
        else:
            amount += " native"; 
        if ASSET_ISSUER_KEY in payment:
            amount += ":" + payment[ASSET_ISSUER_KEY]
            del payment[ASSET_ISSUER_KEY]
            
        payment[AMOUNT_KEY] = amount
        
def canonic_source_amount(payment:Dict[str, Any]):
    if SOURCE_AMOUNT_KEY in payment:
        amount = payment[SOURCE_AMOUNT_KEY]
        if SOURCE_ASSET_CODE_KEY in payment:
            amount += " " + payment[SOURCE_ASSET_CODE_KEY];
            del payment[SOURCE_ASSET_CODE_KEY]
        else:
            amount += " native"; 
        if SOURCE_ASSET_ISSUER_KEY in payment:
            amount += ":" + payment[SOURCE_ASSET_ISSUER_KEY]
            del payment[SOURCE_ASSET_ISSUER_KEY]
        payment[SOURCE_AMOUNT_KEY] = amount
        
def simplify_create_account_payment(payment:Dict[str, Any], account_id:str):
    if STARTING_BALANCE_KEY in payment and ACCOUNT_KEY in payment and FUNDER_KEY in payment:
        if payment[ACCOUNT_KEY] == account_id:
           payment[AMOUNT_RECEIVED_KEY] = payment[STARTING_BALANCE_KEY] + ' native'
           payment[FROM_KEY] = payment[FUNDER_KEY]
        elif payment[FUNDER_KEY] == account_id:
           payment[AMOUNT_SENT_KEY] = payment[STARTING_BALANCE_KEY] + ' native'
           payment[TO_KEY] = payment[ACCOUNT_KEY]
        
def simplify_account_merge_payment(payment:Dict[str, Any], account_id:str):
    if INTO_KEY in payment and ACCOUNT_KEY in payment:
       if payment[ACCOUNT_KEY] == account_id:
           payment[TO_KEY] = payment[INTO_KEY]
       elif payment[INTO_KEY] == account_id:
           payment[FROM_KEY] = payment[ACCOUNT_KEY]

def simplify_path_payment(payment:Dict[str, Any], account_id:str):
    if FROM_KEY in payment and payment[FROM_KEY] == account_id:
        canonic_source_amount(payment=payment)
        replace_key(payment, SOURCE_AMOUNT_KEY, AMOUNT_SENT_KEY)
        del payment[FROM_KEY]
    elif TO_KEY in payment and payment[TO_KEY] == account_id:
        canonic_amount(payment=payment)
        replace_key(payment, AMOUNT_KEY, AMOUNT_RECEIVED_KEY)
        del payment[TO_KEY]

async def send_payment(network_passphrase: str, 
                       destination: str, 
                       amount: str, 
                       asset_code: Union[str, None], 
                       asset_issuer: Union[str, None], 
                       memo_type: Union[str, None],
                       memo: Union[str, None]) -> str :
    
    pay_asset = asset_from(asset_code=asset_code, asset_issuer=asset_issuer)
    pay_memo = memo_from(memo=memo, memo_type=memo_type)
     
    config = configparser.ConfigParser()
    config.read('signing.ini')
    secret = config['signing']['secret']
     
    pay_uri_builder = PayStellarUri(destination = destination, amount = amount, asset=pay_asset, memo = pay_memo,
                                    callback = None, message = None, network_passphrase = network_passphrase,
                                    origin_domain = None, signature = None)
    
    pay_uri_builder.sign(secret)
    sep7_pay_uri = pay_uri_builder.to_uri()
    #pay_link = sep7_pay_uri.replace("web+stellar:", APP_URL + "/")
    
    # this is a workaround because ChatGPT sometimes cuts off parts of the link
    key = db_add_signing_request(sep7_pay_uri)
    pay_link = f"{APP_URL}/sign_pay/{key}"
    return pay_link