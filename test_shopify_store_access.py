from shopify_store import ShopifyStore
import requests

if __name__ == "__main__":
    storename = "store[CHANGE]"
    username = "user[CHANGE]"
    password = "pass[CHANGE]"
    store = ShopifyStore(storename, username, password)

    url = "https://" + username + ":" + password + "@" + storename + ".myshopify.com/admin/api/2021-04/products.json?limit=250"
    r = requests.get(url)

    products = r.json()["products"]
    inventory_item_id = ""
    for prod in products:
        if "inventory_item_id" in prod:
            inventory_item_id = prod["inventory_item_id"]
        for variant in prod["variants"]:
            if "inventory_item_id" in variant:
                inventory_item_id = variant["inventory_item_id"]
        if inventory_item_id != "":
            break
    
    url_location = "https://" + username + ":" + password + "@" + storename + ".myshopify.com/admin/api/2021-04/locations.json"
    req_location = requests.get(url_location).json()
    location_id = req_location["locations"][0]["id"]
    data = {
          "location_id": location_id,
          "inventory_item_id": inventory_item_id,
          "available_adjustment": 0
        }
    url_post = "https://" + username + ":" + password + "@" + storename + ".myshopify.com/admin/api/2021-04/inventory_levels/adjust.json"
    res = requests.post(url_post, data=data)

    if r.status_code == 200 and res.status_code == 200:
        print("Access")
    else:
        print("ACCESS DENIED")
    
