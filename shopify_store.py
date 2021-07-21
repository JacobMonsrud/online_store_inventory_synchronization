import requests
import json

class ShopifyStore:

    def __init__(self, storename, username, password):
        self.storename = storename
        self.username = username
        self.password = password
    
    # This is only to limit the number of api calls, as shopify don't allow to search product by sku
    def create_sku_id_dict(self, products):
        sku_id = {}
        for product in products:
            if "sku" in product and "inventory_item_id" in product:
                sku = product["sku"]
                id_p = product["inventory_item_id"]
                sku_id[sku] = id_p

            product_variants = product["variants"]
            for variant in product_variants:
                if "sku" in variant and "inventory_item_id" in variant:
                    sku = variant["sku"]
                    id_v = variant["inventory_item_id"]
                    sku_id[sku] = id_v

        self.sku_id = sku_id

    def get_sku_stocklevel_dict(self):
        url = "https://" + self.username + ":" + self.password + "@" + self.storename + ".myshopify.com/admin/api/2021-04/products.json?limit=250"
        req = requests.get(url).json()
        products = req["products"]
        self.create_sku_id_dict(products)
        sku_stocklevel = {}

        for product in products:
            if "sku" in product and "inventory_quantity" in product:
                sku = product["sku"]
                stocklevel = product["inventory_quantity"]
                sku_stocklevel[sku] = stocklevel

            product_variants = product["variants"]
            for variant in product_variants:
                if "sku" in variant and "inventory_quantity" in variant:
                    sku = variant["sku"]
                    stocklevel = variant["inventory_quantity"]
                    sku_stocklevel[sku] = stocklevel
        return sku_stocklevel

    def write_dict_to_json_file(self, filename, dictionary):
        with open(filename + ".json", 'w') as json_file:
            json.dump(dictionary, json_file)
    
    def read_dict_from_json_file(self, filename):
        with open(filename + ".json") as json_file:
            dictionary = json.load(json_file)
            return dictionary

    def update_stock_level_for_sku(self, sku, stockchange):
        # stockchange is how much should the stock change. -1 is decrease the stock value by 1 (one item sold). +1 is increase.
        inventory_item_id = ""
        if sku in self.sku_id:
            inventory_item_id = self.sku_id[sku]
        else:
            # If more than 250, we must get all vendors and then get their sku individually
            url = "https://" + self.username + ":" + self.password + "@" + self.storename + ".myshopify.com/admin/api/2021-04/products.json?limit=250"
            req = requests.get(url).json()
            products = req["products"]
            for product in products:
                if "sku" in product:
                    product_sku = product["sku"]
                    if product_sku == sku:
                        inventory_item_id = product["inventory_item_id"]
                        break

                for variant in product["variants"]:
                    if "sku" in variant:
                        variant_sku = variant["sku"]
                        if variant_sku == sku:
                            inventory_item_id = variant["inventory_item_id"]
                if inventory_item_id != "":
                    break

        url_location = "https://" + self.username + ":" + self.password + "@" + self.storename + ".myshopify.com/admin/api/2021-04/locations.json"
        req_location = requests.get(url_location).json()   
        location_id = req_location["locations"][0]["id"]

        data = {
          "location_id": location_id,
          "inventory_item_id": inventory_item_id,
          "available_adjustment": stockchange
        }
        url_post = "https://" + self.username + ":" + self.password + "@" + self.storename + ".myshopify.com/admin/api/2021-04/inventory_levels/adjust.json"

        res = requests.post(url_post, data=data)
        return res.status_code == 200
    
    def get_difference_stock_level(self, old_stock, new_stock):
        difference_stock = {}
        skus_all = set(list(old_stock.keys()) + list(new_stock.keys()))
        for sku in skus_all:
            if sku in old_stock and sku in new_stock:
                difference = new_stock[sku] - old_stock[sku]
                if not difference == 0:
                    difference_stock[sku] = difference
        return difference_stock
