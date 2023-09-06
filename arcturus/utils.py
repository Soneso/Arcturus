
from typing import Union

def add_paging(builder, cursor:Union[int, str], order:str, limit:int):
    if cursor is not None:
        builder.cursor(cursor)
    if order == 'asc' or order is None:
        builder.order(desc=False)
    else:
        builder.order(desc=True)
    if limit is not None:
        builder.limit(int(limit))