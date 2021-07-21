from woocommerce import API
import json

class WordpressStore:

    def __init__(self, storeurl, consumer_key, consumer_secret):
        url = "https://" + storeurl + "/"
        self.storename = storeurl
        self.woocommerce_api = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            wp_api=True,
            version="wc/v3",
            timeout=50
        )
    
    def get_sku_stocklevel_dict(self):
        req = self.woocommerce_api.get("products")
        products = req.json()
        sku_stocklevel = {}

        for product in products:
            if "sku" in product and "stock_quantity" in product:
                sku = product["sku"]
                stocklevel = product["stock_quantity"]
                sku_stocklevel[sku] = stocklevel
            
            variants = product["variations"]
            for variant in variants:
                variant_endpoint = "products/" + str(product["id"]) + "/variations/" + str(variant)
                variant_data = self.woocommerce_api.get(variant_endpoint).json()
                if "sku" in variant_data and "stock_quantity" in variant_data:
                    variant_sku = variant_data["sku"]
                    variant_stocklevel = variant_data["stock_quantity"]
                    sku_stocklevel[variant_sku] = variant_stocklevel
        
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
        products = self.woocommerce_api.get("products?sku=" + sku).json() # There will only be one product
        if len(products) > 0:
            sku_data = products[0]
            variant_id = sku_data["id"]
            links = sku_data["_links"]
            up = links["up"]
            href = up[0]["href"]
            href_list = href.split("/")
            parent_id = href_list[-1]
            get_url = "products/" + str(parent_id) + "/variations/" + str(variant_id)
            old_stock_quantity = sku_data["stock_quantity"]
            stock_quantity = old_stock_quantity + stockchange
            updated_product_data = {
                "stock_quantity": stock_quantity
            }
            res = self.woocommerce_api.put(get_url, updated_product_data)
            return res.status_code == 200
        return False

    def get_difference_stock_level(self, old_stock, new_stock):
        difference_stock = {}
        skus_all = set(list(old_stock.keys()) + list(new_stock.keys()))
        for sku in skus_all:
            if sku in old_stock and sku in new_stock and sku != "":
                difference = 0
                try:
                    difference = new_stock[sku] - old_stock[sku]
                except TypeError:
                    if new_stock[sku] is not None:
                        difference = new_stock[sku]
                    else:
                        difference = 0
                if not difference == 0:
                    difference_stock[sku] = difference
        return difference_stock
