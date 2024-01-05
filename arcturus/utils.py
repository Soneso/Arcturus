from stellar_sdk import Memo, NoneMemo, TextMemo, IdMemo, HashMemo, ReturnHashMemo,  Asset
from stellar_sdk.exceptions import AssetCodeInvalidError, AssetIssuerInvalidError
from typing import (Union, Dict, Any, List)
from sqlite3 import dbapi2 as sqlite3
from quart import g
import random
import string

ASSET_TYPE_KEY = 'asset_type'
ASSET_CODE_KEY = 'asset_code'
ASSET_ISSUER_KEY = 'asset_issuer'


def add_paging(builder, cursor:Union[int, str], order:str, limit:int):
    if cursor is not None:
        builder.cursor(cursor)
        
    # default to desc
    if order is not None and order == 'asc':
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

def memo_from(memo:Union[str, None], memo_type:Union[str, None]) -> Memo :
    new_memo = NoneMemo()
    if memo is not None:
        if memo_type is not None and memo_type == 'id':
            try:
                new_memo = IdMemo(int(memo))
            except Exception:
                raise ValueError("invalid memo for memo type id: must be a 64 bit unsigned integer") 
        elif memo_type is not None and memo_type == 'hash':
            try:
                new_memo = HashMemo(memo)
            except Exception:
                raise ValueError("invalid memo for memo type hash: must be a 32 byte hex encoded string")
        elif memo_type is not None and memo_type == 'return':
            try:
                new_memo = ReturnHashMemo(memo)
            except Exception:
                raise ValueError("invalid memo for memo type return: must be a 32 byte hex encoded string")
        else:
            text = bytes(memo, encoding="utf-8")
            if len(text) > 28:
                raise ValueError("invalid memo for memo type text: memo to long. must be <= 28 bytes")
            new_memo = TextMemo(memo)
    return new_memo

def asset_from(asset_code:Union[str, None], asset_issuer:Union[str, None]) -> Asset :
    new_asset = Asset.native()
    if asset_code is not None and asset_code != 'native' and asset_code != 'XLM':
        if asset_issuer is not None:
            try:
                new_asset = Asset(asset_code, asset_issuer)
            except AssetCodeInvalidError:
                raise ValueError("invalid asset code")
            except AssetIssuerInvalidError:
                raise ValueError("invalid asset issuer")
        else:
            raise ValueError("invalid asset: missing asset issuer")
    return new_asset

def connect_db():
    engine = sqlite3.connect("arcturus.db")
    #engine.row_factory = sqlite3.Row
    return engine

def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def get_random_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

def db_add_signing_request(value:str) -> str:
   key = get_random_string(12)
   old_val = db_get_signing_request(key=key)
   if old_val is not None:
       return db_add_signing_request(value=value)
   db = get_db()
   db.execute(
       "INSERT INTO sign_requests (key, value) VALUES (?, ?)",
       [key, value],)
   db.commit()
   return key

def db_get_signing_request(key:str) -> Union[str, None]:
   db = get_db()
   cur = db.execute(
       "SELECT value from sign_requests WHERE key = ?",
       [key],)
   res = cur.fetchone()
   if res is None:
       return None
   
   return res[0]      