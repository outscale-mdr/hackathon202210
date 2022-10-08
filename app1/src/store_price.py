import requests

def clone_product(product_id, new_product_id, coef):
    LIST_PRODUCT_URL = "http://ms1:8000/product_items"
    items = requests.get(url = f"{LIST_PRODUCT_URL}/{product_id}").json()
    
    ADD_PRODUCT_URL = "http://ms1:8000/product_item"
    for item in items:
        del(item['id'])
        item['product_id'] = new_product_id
        item['price'] *= coef
        requests.put(url = ADD_PRODUCT_URL, json = item)

    return len(items)

"""
Find the sum of items prices of a product
"""
def sum_of_prices(product_id):
    LIST_PRODUCT_URL = "http://ms1:8000/product_items"
    items = requests.get(url = f"{LIST_PRODUCT_URL}/{product_id}").json()
    
    return round(sum([i['price'] for i in items]))


"""
Delete all product's items
"""
def delete_product(product_id):
    LIST_PRODUCT_URL = "http://ms1:8000/product"
    
    return requests.delete(url = f"{LIST_PRODUCT_URL}/{product_id}").text
