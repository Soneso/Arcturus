from stellar_sdk.soroban_server import (SorobanServer, Durability)
from stellar_sdk.soroban_rpc import (EventFilter, EventFilterType)
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk import StrKey
from stellar_sdk.address import Address
from arcturus.scval import decode_scval, prepare_decoded_scval
import base64
    
async def get_latest_ledger(rpc_url):
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

async def contract_data(rpc_url, contract_id, key, durability):
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
        return prepare_decoded_scval(ledger_entry_data.contract_data.body.data.val)
    except Exception as e:
        print("Error getting legder entry data:", e)
        return None
    
async def contract_code_for_wasm_id(rpc_url, wasm_id):
    ledger_key = stellar_xdr.LedgerKey(
        stellar_xdr.LedgerEntryType.CONTRACT_CODE,
        contract_code = stellar_xdr.LedgerKeyContractCode(
            hash = stellar_xdr.Hash(bytes.fromhex(wasm_id)), 
            body_type=stellar_xdr.ContractEntryBodyType.DATA_ENTRY),
    )
    resp = SorobanServer(rpc_url).get_ledger_entries([ledger_key])
    entries = resp.entries
    if not entries:
        return None
    ledger_entry_data = stellar_xdr.LedgerEntryData.from_xdr(entries[0].xdr)
    return base64.b64encode(ledger_entry_data.contract_code.body.code).decode('ascii')

async def contract_code_for_contract_id(rpc_url, contract_id):
    
    if not StrKey.is_valid_contract(contract_id):
        contract_id = StrKey.encode_contract(bytes.fromhex(contract_id))
        
    sc_address = Address(contract_id).to_xdr_sc_address()
    
    ledger_key = stellar_xdr.LedgerKey(
        stellar_xdr.LedgerEntryType.CONTRACT_DATA,
        contract_data=stellar_xdr.LedgerKeyContractData(
            contract=sc_address,
            key=stellar_xdr.SCVal(stellar_xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE),
            durability=stellar_xdr.ContractDataDurability.PERSISTENT,
            body_type=stellar_xdr.ContractEntryBodyType.DATA_ENTRY,
        ),
    )
    resp = SorobanServer(rpc_url).get_ledger_entries([ledger_key])
    entries = resp.entries
    if not entries:
        return None
    ledger_entry_data = stellar_xdr.LedgerEntryData.from_xdr(entries[0].xdr)
    wasm_id = ledger_entry_data.contract_data.body.data.val.instance.executable.wasm_hash.hash.hex()
    if wasm_id == None:
        return None
    return await contract_code_for_wasm_id(rpc_url=rpc_url, wasm_id=wasm_id)
        
def decode_event_info(event_info):
    data = {}    
    data['event_type'] = event_info.event_type
    data['id'] = event_info.id
    data['paging_token'] = event_info.paging_token
    topic_vals = []
    for val in event_info.topic:
       topic_vals.append(decode_scval(val))
    data['topic'] = topic_vals
    data['value'] = decode_scval(event_info.value.xdr)
    data['contract_id'] = event_info.contract_id
    data['ledger'] = event_info.ledger
    return data