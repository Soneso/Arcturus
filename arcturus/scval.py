from stellar_sdk import xdr as stellar_xdr
from stellar_sdk import StrKey

async def decode_scval(base64_xdr):
    val = stellar_xdr.SCVal.from_xdr(base64_xdr)
    return prepare_decoded_scval(val=val)

def prepare_decoded_scval(val):
    data = {}
    if val.type == stellar_xdr.SCValType.SCV_BOOL:
        data['type'] = 'bool'
        data['value'] = val.b
    elif val.type == stellar_xdr.SCValType.SCV_VOID:
        data['type'] = 'void'
    elif val.type == stellar_xdr.SCValType.SCV_ERROR:
        data['type'] = 'scval of type error'
        data['decoded_error'] = prepare_decoded_scerr(val.error)
    elif val.type == stellar_xdr.SCValType.SCV_U32:
        data['type'] = 'u32'
        data['value'] = val.u32.uint32
    elif val.type == stellar_xdr.SCValType.SCV_I32:
        data['type'] = 'i32'
        data['value'] = val.i32.int32
    elif val.type == stellar_xdr.SCValType.SCV_U64:
        data['type'] = 'u64'
        data['value'] = val.u64.uint64
    elif val.type == stellar_xdr.SCValType.SCV_I64:
        data['type'] = 'i64'
        data['value'] = val.i64.int64
    elif val.type == stellar_xdr.SCValType.SCV_TIMEPOINT:
        data['type'] = 'timepoint'
        data['value'] = val.timepoint.time_point.uint64
    elif val.type == stellar_xdr.SCValType.SCV_DURATION:
        data['type'] = 'duration'
        data['value'] = val.duration.duration.uint64
    elif val.type == stellar_xdr.SCValType.SCV_U128:
        data['type'] = 'u128'
        u128_parts = {}
        u128_parts['hi'] = val.u128.hi.uint64
        u128_parts['lo'] = val.u128.lo.uint64
        data['u128_parts'] = u128_parts
    elif val.type == stellar_xdr.SCValType.SCV_I128:
        data['type'] = 'i128'
        i128_parts = {}
        i128_parts['hi'] = val.i128.hi.int64
        i128_parts['lo'] = val.i128.lo.uint64
        data['i128_parts'] = i128_parts
    elif val.type == stellar_xdr.SCValType.SCV_U256:
        data['type'] = 'u256'
        u256_parts = {}
        u256_parts['hi_hi'] = val.u256.hi_hi.uint64
        u256_parts['hi_lo'] = val.u256.hi_lo.uint64
        u256_parts['lo_hi'] = val.u256.lo_hi.uint64
        u256_parts['lo_lo'] = val.u256.lo_lo.uint64
        data['u256_parts'] = u256_parts
    elif val.type == stellar_xdr.SCValType.SCV_I256:
        data['type'] = 'i256'
        i256_parts = {}
        i256_parts['hi_hi'] = val.i256.hi_hi.int64
        i256_parts['hi_lo'] = val.i256.hi_lo.uint64
        i256_parts['lo_hi'] = val.i256.lo_hi.uint64
        i256_parts['lo_lo'] = val.i256.lo_lo.uint64
        data['i256_parts'] = i256_parts
    elif val.type == stellar_xdr.SCValType.SCV_BYTES:
        data['type'] = 'bytes'
        data['value'] = val.bytes.sc_bytes.hex()
    elif val.type == stellar_xdr.SCValType.SCV_STRING:
        data['type'] = 'string'
        data['value'] = val.str.sc_string.decode('utf-8')
    elif val.type == stellar_xdr.SCValType.SCV_SYMBOL:
        data['type'] = 'symbol'
        data['value'] = val.sym.sc_symbol.decode('utf-8')
    elif val.type == stellar_xdr.SCValType.SCV_VEC:
        data['type'] = 'vector'
        elements = []
        if val.vec is not None:
            for vnext in val.vec.sc_vec:
                elements.append(prepare_decoded_scval(val=vnext))
        data['elements'] = elements
    elif val.type == stellar_xdr.SCValType.SCV_MAP:
        data['type'] = 'map'
        entries = []
        if val.map is not None:
            for mnext in val.map.sc_map:
                entry = {}
                entry['key'] = prepare_decoded_scval(val=mnext.key)
                entry['value'] = prepare_decoded_scval(val=mnext.val)
                entries.append(entry)
        data['map_entries'] = entries
    elif val.type == stellar_xdr.SCValType.SCV_ADDRESS:
        data['type'] = 'address'
        address = {}
        if val.address.type == stellar_xdr.SCAddressType.SC_ADDRESS_TYPE_ACCOUNT:
            address['type'] = 'account_address'
            address['account_id'] = StrKey.encode_ed25519_public_key(
                val.address.account_id.account_id.ed25519.uint256
                )
        elif val.address.type == stellar_xdr.SCAddressType.SC_ADDRESS_TYPE_CONTRACT:
            address['type'] = 'contract_address'
            address['contract_id'] = val.address.contract_id.hash.hex()
            address['contract_addr'] = StrKey.encode_contract(val.address.contract_id.hash)
        data['address'] = address
    elif val.type == stellar_xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE:
        data['type'] = 'ledger key instance'
    elif val.type == stellar_xdr.SCValType.SCV_LEDGER_KEY_NONCE:
        data['type'] = 'ledger key nonce'
        data['vale'] = val.nonce_key.nonce.int64
    elif val.type == stellar_xdr.SCValType.SCV_CONTRACT_INSTANCE:
        data['type'] = 'contract instance'
        instance = {}
        executable = {}
        if val.instance.executable.type == stellar_xdr.ContractExecutableType.CONTRACT_EXECUTABLE_WASM:
            executable['type'] = "wasm"
            executable['wasm_id'] = val.instance.executable.wasm_hash.hash.hex()
        elif val.instance.executable.type == stellar_xdr.ContractExecutableType.CONTRACT_EXECUTABLE_TOKEN:
            executable['type'] = "token"
        
        instance['executable'] = executable
        if val.instance.storage is not None:
            storage = []
            for mnext in val.instance.storage.sc_map:
                entry = {}
                entry['key'] = prepare_decoded_scval(val=mnext.key)
                entry['value'] = prepare_decoded_scval(val=mnext.val)
                storage.append(entry)
            instance['storage'] = storage
        data['contract_instance'] = instance
    return data

def prepare_decoded_scerr(err_val):
    error = {}
    if err_val.type == stellar_xdr.SCErrorType.SCE_CONTRACT:
        error['error_type_string'] = 'contract'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_WASM_VM:
        error['error_type_string'] = 'wasm vm'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_CONTEXT:
        error['error_type_string'] = 'context'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_STORAGE:
        error['error_type_string'] = 'storage'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_OBJECT:
        error['error_type_string'] = 'object'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_CRYPTO:
        error['error_type_string'] = 'crypto'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_EVENTS:
        error['error_type_string'] = 'events'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_BUDGET:
        error['error_type_string'] = 'budget'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_VALUE:
        error['error_type_string'] = 'value'
    elif err_val.type == stellar_xdr.SCErrorType.SCE_AUTH:
        error['error_type_string'] = 'auth'

    error['error_type'] = err_val.type
    
    if err_val.code == stellar_xdr.SCErrorCode.SCEC_ARITH_DOMAIN:
        error['error_code_string'] = 'arith domain'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_INDEX_BOUNDS:
        error['error_code_string'] = 'index bounds'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_INVALID_INPUT:
        error['error_code_string'] = 'invalid input'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_MISSING_VALUE:
        error['error_code_string'] = 'missing value'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_EXISTING_VALUE:
        error['error_code_string'] = 'existing value'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_EXCEEDED_LIMIT:
        error['error_code_string'] = 'exeeded limit'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_INVALID_ACTION:
        error['error_code_string'] = 'invalid action'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_INTERNAL_ERROR:
        error['error_code_string'] = 'internal'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_UNEXPECTED_TYPE:
        error['error_code_string'] = 'unexpected type'
    elif err_val.code == stellar_xdr.SCErrorCode.SCEC_UNEXPECTED_SIZE:
        error['error_code_string'] = 'unexpected size'
    
    error['error_code'] = err_val.code
    return error
    