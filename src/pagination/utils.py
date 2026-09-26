from math import ceil

def generate_meta(page,limit,total):

    total_pages = ceil(total/limit)
    meta = {
        "page": page,
        "limit": limit,
        "total":total,
        "total_pages": total_pages,
        "has_next": page<total_pages,
        "has_previous": page>1
    }
    
    return meta
