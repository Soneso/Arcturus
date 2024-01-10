from stellar_sdk.soroban_server import (SorobanServer, Durability)
from stellar_sdk.soroban_rpc import (EventFilter, EventFilterType, EventInfo)
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk import StrKey, TransactionBuilder, TransactionEnvelope
from stellar_sdk.address import Address
from stellar_sdk.exceptions import AccountNotFoundException
from stellar_sdk.sep.stellar_uri import TransactionStellarUri
from arcturus.scval import decode_scval, prepare_decoded_scval, format_spec_entry, format_bytes_2_str
from arcturus.utils import memo_from, db_add_signing_request
from arcturus.constants import APP_URL
from typing import Union, Sequence
import base64
import re
import traceback
import configparser
    
async def get_latest_ledger(rpc_url:str):
    response = SorobanServer(rpc_url).get_latest_ledger()
    return response.__dict__

async def contract_events(rpc_url, start_ledger, contract_id, cursor, limit):
    filters = [
        EventFilter(
            event_type=EventFilterType.CONTRACT,
            contract_ids=[
                contract_id
            ],
        )
    ]
    response = SorobanServer(rpc_url).get_events(start_ledger, filters, cursor, limit)
    records = []
    for event_info in response.events:
       records.append(decode_event_info(event_info))
    return records

async def contract_data(rpc_url:str, contract_id:str, key:str, durability:str):
    dur = Durability.PERSISTENT
    if durability == "temporary":
       dur = Durability.TEMPORARY
    
    try:
        key_val = stellar_xdr.SCVal.from_xdr(key)
        if not StrKey.is_valid_contract(contract_id):
            contract_id = StrKey.encode_contract(bytes.fromhex(contract_id))
        result = SorobanServer(rpc_url).get_contract_data(contract_id, key_val, dur)
        if result == None:
            return result
        ledger_entry_data = stellar_xdr.LedgerEntryData.from_xdr(result.xdr)
        return prepare_decoded_scval(ledger_entry_data.contract_data.val)
    except Exception as e:
        print("Error getting legder entry data:", e)
        return None
    
async def contract_code_for_wasm_id(rpc_url:str, wasm_id:str):
    ledger_key = stellar_xdr.LedgerKey(
        stellar_xdr.LedgerEntryType.CONTRACT_CODE,
        contract_code = stellar_xdr.LedgerKeyContractCode(
            hash = stellar_xdr.Hash(bytes.fromhex(wasm_id))),
    )
    resp = SorobanServer(rpc_url).get_ledger_entries([ledger_key])
    entries = resp.entries
    if not entries:
        return None
    ledger_entry_data = stellar_xdr.LedgerEntryData.from_xdr(entries[0].xdr)
    return base64.b64encode(ledger_entry_data.contract_code.code).decode('latin-1')

async def contract_code_for_contract_id(rpc_url:str, contract_id:str):
    
    if not StrKey.is_valid_contract(contract_id):
        contract_id = StrKey.encode_contract(bytes.fromhex(contract_id))
        
    sc_address = Address(contract_id).to_xdr_sc_address()
    
    ledger_key = stellar_xdr.LedgerKey(
        stellar_xdr.LedgerEntryType.CONTRACT_DATA,
        contract_data=stellar_xdr.LedgerKeyContractData(
            contract=sc_address,
            key=stellar_xdr.SCVal(stellar_xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE),
            durability=stellar_xdr.ContractDataDurability.PERSISTENT
        ),
    )
    
    resp = SorobanServer(rpc_url).get_ledger_entries([ledger_key])
    entries = resp.entries
    if not entries:
        return None
    ledger_entry_data = stellar_xdr.LedgerEntryData.from_xdr(entries[0].xdr)
    wasm_id = ledger_entry_data.contract_data.val.instance.executable.wasm_hash.hash.hex()
    if wasm_id == None:
        return None
    return await contract_code_for_wasm_id(rpc_url=rpc_url, wasm_id=wasm_id)

async def contract_meta(rpc_url:str, wasm_id:str, contract_id:str):
    code = None
    if wasm_id is not None:
        code = await contract_code_for_wasm_id(rpc_url, wasm_id=wasm_id)
    elif contract_id is not None:
        code = await contract_code_for_contract_id(rpc_url, contract_id=contract_id)
    if code == None:
        return None
    #print(f"Code: {code}")
    
    meta = meta_from_code(code=code)
    if not meta:
        return None
    
    return meta

async def transaction_status(rpc_url:str, transaction_hash:str):
    response = SorobanServer(rpc_url).get_transaction(transaction_hash)
    return response.status.value
    
        
def decode_event_info(event_info: EventInfo):
    data = {}    
    data['event_type'] = event_info.event_type
    data['id'] = event_info.id
    data['paging_token'] = event_info.paging_token
    topic_vals = []
    for val in event_info.topic:
       topic_vals.append(decode_scval(val))
    data['topic'] = topic_vals
    data['value'] = decode_scval(event_info.value)
    data['contract_id'] = event_info.contract_id
    data['ledger'] = event_info.ledger
    data['in_successful_contract_call'] = event_info.in_successful_contract_call
    return data

def meta_from_code(code:str):
    result = {}
    
    base64_bytes = code.encode('latin-1')
    code_bytes_as_str = base64.b64decode(base64_bytes).decode('latin-1', 'replace')
    try:
        contract_meta = find_custom_section('contractmetav0', code_bytes_as_str)
        xdr_meta_entries_arr = xdr_meta_entries(meta_type = 'meta', contract_code = contract_meta)
        meta_entries = []
        for xdr_meta_entry in xdr_meta_entries_arr:
            meta_entries.append({'key': format_bytes_2_str(xdr_meta_entry.v0.key), 'value':format_bytes_2_str(xdr_meta_entry.v0.val)})
        result['contract_meta'] = meta_entries
    except Exception as e:
        print("An exception occurred:", str(e))
        traceback.print_exc()
    
    try:
        contract_env_meta = find_custom_section('contractenvmetav0', code_bytes_as_str)
        contract_env_meta_xdr = stellar_xdr.SCEnvMetaEntry.from_xdr_bytes(contract_env_meta.encode('latin-1', 'replace'))
        result['interface_version'] = contract_env_meta_xdr.interface_version.uint64
    except Exception as e:
        print("An exception occurred:", str(e))
        traceback.print_exc()
   
    try:
        contract_spec = find_custom_section('contractspecv0', code_bytes_as_str)
        xdr_spec_entries_arr = xdr_meta_entries(meta_type = 'spec', contract_code = contract_spec)
        spec_entries = []
        for xdr_spec_entry in xdr_spec_entries_arr:
            spec_entries.append(format_spec_entry(xdr_spec_entry))
        result['contract_spec'] = spec_entries
    except Exception as e:
        print("An exception occurred:", str(e))
        traceback.print_exc()
    
    return result

def find_custom_section(section_type:str, code_bytes:str):
    if section_type not in code_bytes:
        return None
    result = None
    if section_type != "contractenvmetav0":
       result = re.search(section_type + '(.*)contractenvmetav0', code_bytes)
       if result != None:
           result = result.group(1)
    
    new_result = None
    if section_type != "contractspecv0":
        new_result = re.search(section_type + '(.*)contractspecv0', code_bytes)
    
    if new_result != None:
        new_result = new_result.group(1)    
    
    if new_result != None and (result == None or len(new_result) < len(result)):
        result = new_result      
     
    new_result = None   
    if section_type != "contractmetav0":
       new_result = re.search(section_type + '(.*)contractmetav0', code_bytes)
       
    if new_result != None:
        new_result = new_result.group(1)
                 
    if new_result != None and (result == None or len(new_result) < len(result)):
        result = new_result

    new_result = None
    if result == None:
        new_result = code_bytes.partition(section_type)
    if new_result != None:
        result = new_result[2]
        
    return result

def xdr_meta_entries(meta_type: str, contract_code:str):
   xdr_entries = []

   while True:
    if contract_code == None or len(contract_code) == 0:
        break
    next_entry = None
    try:
        if meta_type == 'meta':
            next_entry = stellar_xdr.SCMetaEntry.from_xdr_bytes(contract_code.encode('latin-1', 'replace'))
        elif meta_type == 'spec':
            next_entry = stellar_xdr.SCSpecEntry.from_xdr_bytes(contract_code.encode('latin-1', 'replace'))
    except Exception:
        next_entry = None 
    
    if next_entry != None:
        xdr_entries.append(next_entry)
        try:
            next_entry_bytes = next_entry.to_xdr_bytes().decode('latin-1', 'replace')
            contract_code = contract_code.partition(next_entry_bytes)[2]
        except Exception:
            break
    else:
        break
  
   return xdr_entries

async def invoke_contract_function(rpc_server_url: str, 
                                   network_passphrase: str,
                                   source_account_id: str,
                                   contract_id: str,
                                   function_name: str,
                                   arguments: Sequence[stellar_xdr.SCVal] = None,
                                   memo: Union[str, None] = None,
                                   memo_type: Union[str, None] = None,
                                   base_fee: Union[int, None] = None)-> str :
   
    soroban_server = SorobanServer(rpc_server_url)
    source_account = None
    try:
        source_account = soroban_server.load_account(source_account_id)
    except AccountNotFoundException:
        raise ValueError("Source account not found")
    except Exception:
        raise ValueError("An error occured while trying to load data for the source account from stellar network")
    
    tx_base_fee = 100
    if base_fee is not None:
        tx_base_fee = base_fee
        
    tx_builder = TransactionBuilder(source_account, network_passphrase, base_fee=tx_base_fee).add_time_bounds(0, 0).append_invoke_contract_function_op(
        contract_id=contract_id,
        function_name=function_name,
        parameters=arguments,
    )

    memo = memo_from(memo=memo, memo_type=memo_type)
    if memo is not None:
        tx_builder.add_memo(memo)
   
    tx = tx_builder.build()
    tx_envelope = TransactionEnvelope.from_xdr(tx.to_xdr(), network_passphrase=network_passphrase)
    
    config = configparser.ConfigParser()
    config.read('signing.ini')
    secret = config['signing']['secret']
    tx_uri_builder = TransactionStellarUri(transaction_envelope = tx_envelope, network_passphrase = network_passphrase)
    tx_uri_builder.sign(secret)
    sep7_tx_uri = tx_uri_builder.to_uri()
    print(sep7_tx_uri)
    key = db_add_signing_request(sep7_tx_uri)
    tx_link = f"{APP_URL}/sign_tx/{key}"
    return tx_link
    
