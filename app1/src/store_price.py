import requests
import logging

def clone_product(product_id, new_product_id, coef):
    LIST_PRODUCT_URL = "http://ms1:8000/clone"
    items = requests.get(url = f"{LIST_PRODUCT_URL}/{product_id}/{new_product_id}/{coef}").text

    logging.warning(items)

    return int(items)

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
