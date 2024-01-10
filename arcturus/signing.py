
import quart
from typing import Union, Dict
from arcturus.constants import PUBLIC_NETWORK_PASSPHRASE, TESTNET_NETWORK_PASSPHRASE, FUTURENET_NETWORK_PASSPHRASE, HORIZON_PUBLIC_URL, HORIZON_TESTNET_URL, HORIZON_FUTURENET_URL, SOROBAN_RPC_TESTNET_URL, SOROBAN_RPC_FUTURENET_URL
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk.sep.txrep import to_txrep
from stellar_sdk.keypair import Keypair
from stellar_sdk.exceptions import BadSignatureError, PrepareTransactionException
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban_server import SorobanServer
from urllib import parse
import base64
import configparser
from arcturus.utils import db_get_signing_request

PUBLIC_NETWORK: str = 'PUBLIC'
TESTNET_NETWORK: str = 'TESTNET'
FUTURENET_NETWORK: str = 'FUTURENET'

async def pay(key:str) -> quart.Response :
    url = db_get_signing_request(key)
    if url is None:
       return await quart.render_template("signing_err.html", err_msg="Invalid request: key not found.")
    
    valid = valid_signature(url)
    if not valid:
        return await quart.render_template("signing_err.html", err_msg="Invalid signature.")
    
    parsed_uri = parse.urlparse(url)
    query_dic = parse_uri_query(parsed_uri.query)
    
    destination = query_dic.get('destination')
    if destination is None:
        return await quart.render_template("signing_err.html", err_msg="Missing destination.")
    amount = query_dic.get('amount')
    if amount is None:
        return await quart.render_template("signing_err.html", err_msg="Missing amount.")
    
    asset_code = query_dic.get('asset_code')
    asset_issuer = query_dic.get('asset_issuer')
    memo = query_dic.get('memo')
    memo_type = js_sdk_memo_type(query_dic.get('memo_type'))
    callback = query_dic.get('callback')
    msg = query_dic.get('msg')
    origin_domain = query_dic.get('origin_domain')
    signature = query_dic.get('signature')
    
    network_passphrase = query_dic.get('network_passphrase')
    network = network_for_passphrase(passphrase=network_passphrase)
    horizon_url = horizon_url_for_network(network=network)
    if not network_is_supported(network=network):
        return await quart.render_template("signing_err.html", err_msg=err_unsupported_passphrase(passphrase=network_passphrase))
    
    return await quart.render_template("signing_pay.html", destination=destination, amount=amount, asset_code=asset_code,
                                       asset_issuer=asset_issuer, memo=memo, memo_type=memo_type, callback=callback, msg=msg,
                                       origin_domain=origin_domain, signature=signature, network=network, network_passphrase=network_passphrase,
                                       horizon_url=horizon_url)

async def tx(key: str) -> quart.Response :
    url = db_get_signing_request(key)
    if url is None:
        return await quart.render_template("signing_err.html", err_msg="Invalid request: key not found.")
    
    valid = valid_signature(url)
    if not valid:
        return await quart.render_template("signing_err.html", err_msg="Invalid signature.")
    
    parsed_uri = parse.urlparse(url)
    query_dic = parse_uri_query(parsed_uri.query)
    
    xdr = query_dic.get('xdr')
    network_passphrase = query_dic.get('network_passphrase')
    network = network_for_passphrase(passphrase=network_passphrase)
    tx_rep = None
    tx_envelope = None
    try:
        tx_envelope = TransactionEnvelope.from_xdr(xdr, network_passphrase= network_passphrase)
    except Exception:
        return await quart.render_template("signing_err.html", err_msg=err_invalid_xdr(xdr=xdr))


    is_soroban_tx = False
    for operation in tx_envelope.transaction.operations:
        if operation._XDR_OPERATION_TYPE is stellar_xdr.OperationType.INVOKE_HOST_FUNCTION:
            is_soroban_tx = True
            break
    
    if not network_is_supported(network=network, is_soroban=is_soroban_tx):
        return await quart.render_template("signing_err.html", err_msg=err_unsupported_passphrase(passphrase=network_passphrase))
    
    rpc_server_url = None
    if is_soroban_tx:
        # simulate first
        rpc_server_url = rpc_url_for_network(network=network)
        soroban_server = SorobanServer(rpc_server_url)
        try:
            tx_envelope = soroban_server.prepare_transaction(tx_envelope)
            xdr = tx_envelope.to_xdr_object().to_xdr()
        except PrepareTransactionException as e:
            return await quart.render_template("signing_err.html", err_msg=f"Simulate Soroban transaction failure: {e.simulate_transaction_response}")
        except Exception as e:
            return await quart.render_template("signing_err.html", err_msg=f"An error occured while preparing the transaction for signing: {e}")
        
    try:
        tx_rep = to_txrep(transaction_envelope=tx_envelope)
    except Exception:
        tx_rep = xdr
    
    if is_soroban_tx:
        return await quart.render_template("signing_soroban.html", xdr=xdr, network=network, 
                                        network_passphrase=network_passphrase, tx_rep=tx_rep,
                                        rpc_server_url=rpc_server_url)
        
    horizon_url = horizon_url_for_network(network=network)
    return await quart.render_template("signing_tx.html", xdr=xdr, network=network, 
                                        network_passphrase=network_passphrase, tx_rep=tx_rep,
                                        horizon_url=horizon_url)

def network_for_passphrase(passphrase:Union[str, None]) -> Union[str, None] : 
    if PUBLIC_NETWORK_PASSPHRASE == passphrase:
        return PUBLIC_NETWORK
    if TESTNET_NETWORK_PASSPHRASE == passphrase:
        return TESTNET_NETWORK
    if FUTURENET_NETWORK_PASSPHRASE == passphrase:
        return FUTURENET_NETWORK
    return None

def network_is_supported(network:Union[str, None], is_soroban = False) -> bool : 
    if is_soroban and (TESTNET_NETWORK == network or FUTURENET_NETWORK == network):
        return True
    if PUBLIC_NETWORK == network or TESTNET_NETWORK == network or FUTURENET_NETWORK == network:
        return True
    return False

def horizon_url_for_network(network:str):
    if PUBLIC_NETWORK == network:
        return HORIZON_PUBLIC_URL
    if TESTNET_NETWORK == network:
        return HORIZON_TESTNET_URL
    if FUTURENET_NETWORK == network:
        return HORIZON_FUTURENET_URL
    return network

def rpc_url_for_network(network:str):
    if TESTNET_NETWORK == network:
        return SOROBAN_RPC_TESTNET_URL
    if FUTURENET_NETWORK == network:
        return SOROBAN_RPC_FUTURENET_URL
    return network

def js_sdk_memo_type(memo_type:Union[str, None]) -> Union[str, None] :
    if "MEMO_TEXT" == memo_type:
        return "text"
    if "MEMO_ID" == memo_type:
        return "id"
    if "MEMO_HASH" == memo_type:
        return "hash"
    if "MEMO_RETURN" == memo_type:
        return "return"
    return memo_type

def err_unsupported_passphrase(passphrase:Union[str, None]) -> str:
    return f'Unsupported network with passphrase "{passphrase}". \n\nSupported network passphrases are: \n{PUBLIC_NETWORK_PASSPHRASE}, \n{TESTNET_NETWORK_PASSPHRASE}, \n{FUTURENET_NETWORK_PASSPHRASE}.'

def err_invalid_xdr(xdr:Union[str, None]) -> str:
    return f'Could not encode transaction xdr: "{xdr}"'

def valid_signature(url: str) -> bool:
    parsed_uri = parse.urlparse(url)
    query = parsed_uri.query

    query_dic = parse_uri_query(query)
    signature = query_dic.pop("signature")

    if signature is None:
        return False

    path = parsed_uri.path.replace('/', '')
    data_query = f"web+stellar:{path}?{parse.urlencode(query_dic, quote_via=parse.quote)}" 
    
    payload_bytes = signature_payload(data_query)
    signature_bytes = base64.b64decode(signature.encode())
 
    config = configparser.ConfigParser()
    config.read('signing.ini')
    pk = config['signing']['account_id']
    kp = Keypair.from_public_key(pk)
    try:
        kp.verify(data=payload_bytes, signature=signature_bytes)
    except BadSignatureError:
        return False
    
    return True

def parse_uri_query(uri_query) -> Dict[str, str]:
    return dict(parse.parse_qsl(uri_query))     

def signature_payload(data_query) -> bytes:
    sign_data = b"\0" * 35 + b"\4" + b"stellar.sep.7 - URI Scheme" + data_query.encode()
    return sign_data