
import quart
from typing import Union
from arcturus.constants import PUBLIC_NETWORK_PASSPHRASE, TESTNET_NETWORK_PASSPHRASE, FUTURENET_NETWORK_PASSPHRASE, HORIZON_PUBLIC_URL, HORIZON_TESTNET_URL, HORIZON_FUTURENET_URL
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk.sep.txrep import to_txrep

PUBLIC_NETWORK: str = 'PUBLIC'
TESTNET_NETWORK: str = 'TESTNET'
FUTURENET_NETWORK: str = 'FUTURENET'

async def pay(request: quart.Request) -> quart.Response :
    return await quart.render_template("signing.html", res=request.url)

async def tx(request: quart.Request) -> quart.Response :
    xdr = request.args.get('xdr')
    network_passphrase = request.args.get('network_passphrase')
    network = network_for_passphrase(passphrase=network_passphrase)
    if not network_is_supported(network=network):
        return await quart.render_template("signing_err.html", err_msg=err_unsupported_passphrase(passphrase=network_passphrase))
    tx_rep = None
    tx_envelope = None
    try:
        tx_envelope = TransactionEnvelope.from_xdr(xdr, network_passphrase= network_passphrase)
    except Exception:
        return await quart.render_template("signing_err.html", err_msg=err_invalid_xdr(xdr=xdr))
    try:
        tx_rep = to_txrep(transaction_envelope=tx_envelope)
    except Exception:
        tx_rep = xdr
        
    horizon_url = horizon_url_for_network(network=network)
    return await quart.render_template("signing.html", res=request.url, xdr=xdr, network=network, 
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

def network_is_supported(network:Union[str, None]) -> bool : 
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

def err_unsupported_passphrase(passphrase:Union[str, None]) -> str:
    return f'Unsupported network with passphrase "{passphrase}". \n\nSupported network passphrases are: \n{PUBLIC_NETWORK_PASSPHRASE}, \n{TESTNET_NETWORK_PASSPHRASE}, \n{FUTURENET_NETWORK_PASSPHRASE}.'

def err_invalid_xdr(xdr:Union[str, None]) -> str:
    return f'Could not encode transaction xdr: "{xdr}"'