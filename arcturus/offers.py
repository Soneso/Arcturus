from stellar_sdk import Server, Asset
from arcturus.utils import add_paging, delete_keys_except, canonic_asset, replace_key
from typing import (Union, Dict, Any)

SELLING_ASSET = 'selling'
BUYING_ASSET = 'buying'
SELLER = "seller"
LAST_MODIFIED_TIME = "last_modified_time"
KEYS_TO_KEEP = ['id', 'paging_token', 'seller', 'selling', 'buying', 'amount', 'price', LAST_MODIFIED_TIME]

async def for_account(horizon_url:str, account_id:str, cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.offers().for_account(account_id=account_id)
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for offer in records:
        simplify_offer(offer=offer)
        if SELLER in offer and offer[SELLER] == account_id:
            del offer[SELLER]
            
    return records

async def all_offers(horizon_url:str, sponsor_id:str, seller_id:str, selling_asset_code:str, 
                     selling_asset_issuer:str, buying_asset_code:str, buying_asset_issuer:str, 
                     cursor:Union[int, str], order:str, limit:int):
    server = Server(horizon_url=horizon_url)
    records = []
    builder = server.offers()
    
    if sponsor_id is not None:
        builder = builder.for_sponsor(sponsor = sponsor_id)
    if seller_id is not None:
        builder = builder.for_seller(seller = seller_id)
    if selling_asset_code == 'native':
        builder = builder.for_selling(selling = Asset.native())
    elif selling_asset_code is not None and selling_asset_issuer is not None:
        builder = builder.for_selling(selling = Asset(selling_asset_code, selling_asset_issuer))
    if buying_asset_code == 'native':
        builder = builder.for_buying(buying = Asset.native())
    elif buying_asset_code is not None and buying_asset_issuer is not None:
        builder = builder.for_buying(buying = Asset(buying_asset_code, buying_asset_issuer))
    
    
    add_paging(builder, cursor, order, limit) 
    records += builder.call()["_embedded"]["records"]
    
    for offer in records:
        simplify_offer(offer=offer)
        
    return records

async def get_details(horizon_url:str, offer_id:str):
    server = Server(horizon_url=horizon_url)
    builder = server.offers().offer(offer_id=offer_id)
    offer = builder.call()
    simplify_offer(offer=offer)
    return offer

def simplify_offer(offer:Dict[str, Any]):
    canonic_asset(dic=offer, key= SELLING_ASSET)
    canonic_asset(dic=offer, key= BUYING_ASSET)
    delete_keys_except(offer, KEYS_TO_KEEP)
    if LAST_MODIFIED_TIME in offer:
        replace_key(offer, LAST_MODIFIED_TIME, "last_modified")
    