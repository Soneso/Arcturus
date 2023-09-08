
from typing import (Union, Dict, Any, List)

ASSET_TYPE_KEY = 'asset_type'
ASSET_CODE_KEY = 'asset_code'
ASSET_ISSUER_KEY = 'asset_issuer'

def add_paging(builder, cursor:Union[int, str], order:str, limit:int):
    if cursor is not None:
        builder.cursor(cursor)
    if order == 'asc' or order is None:
        builder.order(desc=False)
    else:
        builder.order(desc=True)
    if limit is not None:
        builder.limit(int(limit))
        
def delete_keys_except(dictionary:Dict[str, Any], keys_to_keep:List[str]):
    keys_to_delete = [key for key in dictionary.keys() if key not in keys_to_keep]
    for key in keys_to_delete:
        del dictionary[key]
        
def replace_key(dictionary:Dict[str, Any], old_key:str, new_key:str):
    if old_key in dictionary:
        dictionary[new_key] = dictionary.pop(old_key)

def canonic_asset(dic:Dict[str, Any], key:str):
    if key in dic:
        entry = dic[key]
        value = None
        if ASSET_CODE_KEY in entry:
            value = entry[ASSET_CODE_KEY]
            del entry[ASSET_CODE_KEY]
        else:
            value = "native"; 
        if ASSET_ISSUER_KEY in entry:
            value += ":" + entry[ASSET_ISSUER_KEY]
            del entry[ASSET_ISSUER_KEY]
            
        if ASSET_TYPE_KEY in entry:
            del entry[ASSET_TYPE_KEY]

        dic[key] = value