from stellar_sdk import xdr as stellar_xdr
from stellar_sdk import StrKey
from stellar_sdk import scval as sdk_scval
import base64

def decode_scval(base64_xdr:str):
    val = stellar_xdr.SCVal.from_xdr(base64_xdr)
    return prepare_decoded_scval(val=val)

def prepare_decoded_scval(val:stellar_xdr.SCVal):
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
        data['value'] = val.nonce_key.nonce.int64
    elif val.type == stellar_xdr.SCValType.SCV_CONTRACT_INSTANCE:
        data['type'] = 'contract instance'
        instance = {}
        executable = {}
        if val.instance.executable.type == stellar_xdr.ContractExecutableType.CONTRACT_EXECUTABLE_WASM:
            executable['type'] = "wasm"
            executable['wasm_id'] = val.instance.executable.wasm_hash.hash.hex()
        elif val.instance.executable.type == stellar_xdr.ContractExecutableType.CONTRACT_EXECUTABLE_STELLAR_ASSET:
            executable['type'] = "asset"
        
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

def xdr_for(scval_type:str, data: str):
    value = val_for(scval_type=scval_type, data=data)
    return value.to_xdr()

def scval_from_xdr(xdr:str): 
    return stellar_xdr.SCVal.from_xdr(xdr)

def val_for(scval_type:str, data: str):
    if scval_type == 'address':
        return sdk_scval.to_address(data)
    elif scval_type == 'symbol':
        return sdk_scval.to_symbol(data)
    elif scval_type == 'string':
        return sdk_scval.to_string(data)
    elif scval_type == 'u32':
        return sdk_scval.to_uint32(int(data))
    elif scval_type == 'i32':
        return sdk_scval.to_int32(int(data))
    elif scval_type == 'u64':
        return sdk_scval.to_uint64(int(data))
    elif scval_type == 'i64':
        return sdk_scval.to_int64(int(data))
    elif scval_type == 'u128':
        return sdk_scval.to_uint128(int(data))
    elif scval_type == 'i128':
        return sdk_scval.to_int128(int(data))
    elif scval_type == 'u256':
        return sdk_scval.to_uint256(int(data))
    elif scval_type == 'i256':
        return sdk_scval.to_int256(int(data))
    elif scval_type == 'bool':
        return sdk_scval.to_bool(bool(data))
    elif scval_type == 'duration':
        return sdk_scval.to_duration(int(data))
    elif scval_type == 'timepoint':
        return sdk_scval.to_timepoint(int(data))
    else:
        raise ValueError("Invalid type")
    
def format_spec_entry(entry: stellar_xdr.SCSpecEntry):
    dic = {}
    if entry.kind == stellar_xdr.SCSpecEntryKind.SC_SPEC_ENTRY_FUNCTION_V0:
        if entry.function_v0 is not None:
            dic['function'] = format_spec_entry_function(entry.function_v0)
    elif entry.kind == stellar_xdr.SCSpecEntryKind.SC_SPEC_ENTRY_UDT_STRUCT_V0:
        if entry.udt_struct_v0 is not None:
            dic['udt_struct'] = format_spec_entry_udt_struct(entry.udt_struct_v0)
    elif entry.kind == stellar_xdr.SCSpecEntryKind.SC_SPEC_ENTRY_UDT_UNION_V0:
        if entry.udt_union_v0 is not None:
            dic['udt_union'] = format_spec_entry_udt_union(entry.udt_union_v0)
    elif entry.kind == stellar_xdr.SCSpecEntryKind.SC_SPEC_ENTRY_UDT_ENUM_V0:
        if entry.udt_enum_v0 is not None:
            dic['udt_enum'] = format_spec_entry_udt_enum(entry.udt_enum_v0)
    elif entry.kind == stellar_xdr.SCSpecEntryKind.SC_SPEC_ENTRY_UDT_ERROR_ENUM_V0:
        if entry.udt_error_enum_v0 is not None:
            dic['udt_error_enum'] = format_spec_entry_udt_error_enum(entry.udt_error_enum_v0)
            
    return dic
        
def format_spec_entry_function(function: stellar_xdr.SCSpecFunctionV0):
    dic = {}
    if function.name is not None:
        dic['name'] = format_bytes_2_str(function.name.sc_symbol)
    if function.doc is not None:
        doc = format_bytes_2_str(function.doc)
        if len(doc) > 0:
            dic['doc'] = doc
    if function.inputs is not None:
        inputs = []
        for input in function.inputs:
            d = {'name':format_bytes_2_str(input.name), 'type':format_spec_type_def(input.type)}
            doc = format_bytes_2_str(input.doc)
            if len(doc) > 0:
                d['doc'] = doc
            inputs.append(d)
        dic['inputs'] = inputs
    if function.outputs is not None and len(function.outputs) > 0:
        dic['output'] = format_spec_type_def(function.outputs[0])
         
    return dic

def format_spec_entry_udt_struct(udt_struct: stellar_xdr.SCSpecUDTStructV0):
    dic = {}
    if udt_struct.name is not None:
        dic['name'] = format_bytes_2_str(udt_struct.name)
    if udt_struct.lib is not None:
        lib = format_bytes_2_str(udt_struct.lib)
        if len(lib) > 0:
            dic['lib'] = lib
    if udt_struct.doc is not None:
        doc = format_bytes_2_str(udt_struct.doc)
        if len(doc) > 0:
            dic['doc'] = doc
        
    if udt_struct.fields is not None:
        fields = []
        for field in udt_struct.fields:
            d = {'name':format_bytes_2_str(field.name), 'type':format_spec_type_def(field.type)}
            doc = format_bytes_2_str(field.doc)
            if len(doc) > 0:
                d['doc'] = doc
            fields.append(d)
        dic['fields'] = fields
         
    return dic

def format_spec_entry_udt_union(udt_union: stellar_xdr.SCSpecUDTUnionV0):
    dic = {}
    if udt_union.name is not None:
        dic['name'] = format_bytes_2_str(udt_union.name)
    if udt_union.lib is not None:
        lib = format_bytes_2_str(udt_union.lib)
        if len(lib) > 0:
            dic['lib'] = lib
    if udt_union.doc is not None:
        doc = format_bytes_2_str(udt_union.doc)
        if len(doc) > 0:
            dic['doc'] = doc
        
    if udt_union.cases is not None:
        cases = []
        for case in udt_union.cases:
            if case.kind == stellar_xdr.SCSpecUDTUnionCaseV0Kind.SC_SPEC_UDT_UNION_CASE_VOID_V0:
                d = {'kind':'void', 'name': format_bytes_2_str(case.void_case.name)}
                doc = format_bytes_2_str(case.void_case.doc)
                if len(doc) > 0:
                    d['doc'] = doc
                cases.append(d)
            elif case.kind == stellar_xdr.SCSpecUDTUnionCaseV0Kind.SC_SPEC_UDT_UNION_CASE_TUPLE_V0:
                case_dick = {'kind':'tuple', 'name': format_bytes_2_str(case.tuple_case.name)}
                doc = format_bytes_2_str(case.tuple_case.doc)
                if len(doc) > 0:
                    case_dick['doc'] = doc
                case_types = []
                for case_type in case.tuple_case.type:
                    case_types.append(format_spec_type_def(case_type))
                case_dick['type'] = case_types
                cases.append(case_dick)
        dic['cases'] = cases
         
    return dic

def format_spec_entry_udt_enum(udt_enum: stellar_xdr.SCSpecUDTEnumV0):
    dic = {}
    if udt_enum.name is not None:
        dic['name'] = format_bytes_2_str(udt_enum.name)
    if udt_enum.lib is not None:
        lib = format_bytes_2_str(udt_enum.lib)
        if len(lib) > 0:
            dic['lib'] = lib
    if udt_enum.doc is not None:
        doc = format_bytes_2_str(udt_enum.doc)
        if len(doc) > 0:
            dic['doc'] = doc
        
    if udt_enum.cases is not None:
        cases = []
        for case in udt_enum.cases:
            d = {'name': format_bytes_2_str(case.name), 'value': str(case.value.uint32)}
            doc = format_bytes_2_str(case.doc)
            if len(doc) > 0:
                d['doc'] = doc
            cases.append(d)
        dic['cases'] = cases
         
    return dic

def format_spec_entry_udt_error_enum(udt_error_enum: stellar_xdr.SCSpecUDTErrorEnumV0):
    dic = {}
    if udt_error_enum.name is not None:
        dic['name'] = format_bytes_2_str(udt_error_enum.name)
    if udt_error_enum.lib is not None:
        lib = format_bytes_2_str(udt_error_enum.lib)
        if len(lib) > 0:
            dic['lib'] = lib
    if udt_error_enum.doc is not None:
        doc = format_bytes_2_str(udt_error_enum.doc)
        if len(doc) > 0:
            dic['doc'] = doc
        
    if udt_error_enum.cases is not None:
        cases = []
        for case in udt_error_enum.cases:
            d = {'name': format_bytes_2_str(case.name), 'value': str(case.value.uint32)}
            doc = format_bytes_2_str(case.doc)
            if len(doc) > 0:
                d['doc'] = doc
            cases.append(d)
        dic['cases'] = cases
         
    return dic

def format_spec_type_def(type_def: stellar_xdr.SCSpecTypeDef):
    
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_VAL:
        return 'val'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_BOOL:
        return 'bool'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_VOID:
        return 'void'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_ERROR:
        return 'error'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_U32:
        return 'u32'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_I32:
        return 'i32'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_U64:
        return 'u64'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_TIMEPOINT:
        return 'timepoint'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_DURATION:
        return 'duration'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_U128:
        return 'u128'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_I128:
        return 'i128'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_U256:
        return 'u256'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_I256:
        return 'i256'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_BYTES:
        return 'bytes'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_STRING:
        return 'string'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_SYMBOL:
        return 'symbol'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_ADDRESS:
        return 'address'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_OPTION:
        return 'option <value_type = ' + format_spec_type_def(type_def.option.value_type) +'>'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_RESULT:
        return 'result <ok_type = ' + format_spec_type_def(type_def.result.ok_type) + ', error_type = ' +  format_spec_type_def(type_def.result.error_type) + '>'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_VEC:
        return 'vec <element_type = ' + format_spec_type_def(type_def.vec.element_type) +'>'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_MAP:
        return 'map <key_type = ' + format_spec_type_def(type_def.map.key_type) + ', value_type = ' +  format_spec_type_def(type_def.map.value_type) + '>'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_SET:
        return 'set <element_type = ' + format_spec_type_def(type_def.set.element_type) +'>'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_TUPLE:
        result = 'tuple <value_types = '
        for elem_type in type_def.tuple.valueTypes:
            result += format_spec_type_def(elem_type) + ', '
        result += '>'
        return result
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_BYTES_N:
        return 'bytesN[' + str(type_def.bytes_n.n) + ']'
    if type_def.type == stellar_xdr.SCSpecType.SC_SPEC_TYPE_UDT:
        return 'udt <name = ' + format_bytes_2_str(type_def.udt.name) + '>'
    
    return 'unknown'

def format_bytes_2_str(b:bytes):
    if len(b) == 0:
        return ''
    try:
        return b.decode('utf8', 'strict')
    except Exception:
        nase = base64.b64encode(b.decode('latin-1', 'replace'))
        return nase.decode('utf-8')