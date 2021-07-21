from shopify_store import ShopifyStore
from wordpress_store import WordpressStore
import os.path
import json
import time
from datetime import datetime

def find_new_skus(old_sku_stock, sku_stock):
    old_keys = list(old_sku_stock.keys())
    new_keys = list(sku_stock.keys())
    new_skus = []

    for sku in new_keys:
        if sku not in old_keys:
            new_skus.append(sku)
    return new_skus


def update_stock_forever(mura, brands):
    # Initiate with a reading, if there don't exists one already. This is guarded if the code is restarted.
    sku_stock_mura = mura.get_sku_stocklevel_dict()
    if not os.path.exists(mura.storename + ".json"):
        mura.write_dict_to_json_file(mura.storename, sku_stock_mura)
    for brand in brands:
        sku_stock = brand.get_sku_stocklevel_dict()
        if not os.path.exists(brand.storename + ".json"):
            brand.write_dict_to_json_file(brand.storename, sku_stock)
    
    # Create seen before files
    for brand in brands:
        filename = mura.storename + brand.storename + ".json"
        if not os.path.exists(filename):
            open(filename, "w")


    while True:
        print(str(datetime.now()) + " - Running don't stop me!")
        sku_stock_mura = mura.get_sku_stocklevel_dict()
        old_sku_stock_mura = mura.read_dict_from_json_file(mura.storename)
        difference_mura = mura.get_difference_stock_level(old_sku_stock_mura, sku_stock_mura)
        print(mura.storename + " differences: ", difference_mura)

        # Any new SKU's?
        new_mura_sku = find_new_skus(old_sku_stock_mura, sku_stock_mura)

        for brand in brands:
            sku_stock_brand = brand.get_sku_stocklevel_dict()
            old_sku_stock_brand = brand.read_dict_from_json_file(brand.storename)
            difference_brand = brand.get_difference_stock_level(old_sku_stock_brand, sku_stock_brand)
            print(brand.storename + " differences: ", difference_brand)
            for sku in difference_mura:
                success = brand.update_stock_level_for_sku(sku, difference_mura[sku])
                if success:
                    sku_stock_brand[sku] = sku_stock_brand[sku] + difference_mura[sku]

            for brand_sku in difference_brand:
                success = mura.update_stock_level_for_sku(brand_sku, difference_brand[brand_sku])
                if success:
                    sku_stock_mura[brand_sku] = sku_stock_mura[brand_sku] + difference_brand[brand_sku]
                
        brand.write_dict_to_json_file(brand.storename, sku_stock_brand)
        mura.write_dict_to_json_file(mura.storename, sku_stock_mura)

        sleep_time = 60
        print(str(datetime.now()) + " - Done updating, sleeping for " + str(sleep_time) + " seconds.")
        time.sleep(sleep_time)


if __name__ == "__main__":
    mura = ShopifyStore("storename[CHANGE]", "username[CHANGE]", "password[CHANGE]")

    nike = WordpressStore("nike[CHANGE]", "nikeuser[CHANGE]", "password1234[CHANGE]")
    adidas = ShopifyStore("adidas[CHANGE]", "adidasuser[CHANGE]", "password123456789[CHANGE]")

    brands = [nike, adidas]

    update_stock_forever(mura, brands)
