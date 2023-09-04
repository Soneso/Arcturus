from stellar_sdk.soroban_server import (SorobanServer, Durability)
from stellar_sdk.soroban_rpc import (EventFilter, EventFilterType)
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk import StrKey
from arcturus.scval import decode_scval, prepare_decoded_scval
    
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