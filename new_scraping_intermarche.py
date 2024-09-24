#%%
from datetime import datetime
import requests
import re
import pandas as pd
import json
import os

# url = "https://www.loja-online.intermarche.pt/shelves/frutas-e-legumes/frutas/laranjas-e-outros-citrinos/11510"
# url = "https://www.loja-online.intermarche.pt/shelves/frutas-e-legumes/frutas/macas-e-peras/11508"
# url  = "https://www.loja-online.intermarche.pt/shelves/frutas-e-legumes/frutas/uvas/11515"

payload = {}
#; datadome=xQZp9NZJIXOzwh3PYrVpAT1Rfp7f2a2lbzjZimQzhusekdNH6tvpmwsX9DWWY11u9N8_h9CQjxCp7iSQo9nMKQGmg7yHTSXBKK7nOink3D7FtRRmsaYLEoj7wJVkITyg'
headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8,es;q=0.7',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Cookie': 'itm_pdv={%22ref%22:%2207348%22%2C%22isEcommerce%22:true}; novaParams={%22pdvRef%22:%2207348%22}',
  'Pragma': 'no-cache',
  'Referer': 'https://www.loja-online.intermarche.pt/shelves/frutas-e-legumes/frutas/11508',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
  'sec-ch-device-memory': '8',
  'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
  'sec-ch-ua-arch': '"x86"',
  'sec-ch-ua-full-version-list': '"Chromium";v="128.0.6613.138", "Not;A=Brand";v="24.0.0.0", "Google Chrome";v="128.0.6613.138"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-model': '""',
  'sec-ch-ua-platform': '"Windows"'
}

def make_request(url, headers, payload, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.request("GET", url, headers=headers, data=payload, verify=False)
            return response
        except Exception as e:
            retries += 1
            print(f"Error making request to {url}: {e}")
            if retries < max_retries:
                print(f"Retrying ({retries}/{max_retries})...")
    raise Exception(f"Failed to make request to {url} after {max_retries} attempts")


# response = requests.request("GET", url, headers=headers, data=payload,verify=False)

# print(response.text)

#%%

# #%%

# js_data_matches = re.findall(r'window\.__REACT_ESI__\[.*?\] = (\{.*?\});', response.text, re.DOTALL)

# product_list = []

# # Step 2: Iterate over each match and extract the products
# for js_data_str in js_data_matches:
#     try:
#         # Convert the extracted string to a Python dictionary
#         js_data = json.loads(js_data_str)
        
#         # Access the products list
#         products = js_data.get('list', {}).get('products', [])
        
#         # Step 3: Extract details from each product
#         for product in products:
#             product_id = product.get('id')
#             title = product.get('informations', {}).get('title')
#             ean = product.get('ean')
#             packaging = product.get('informations', {}).get('packaging')
#             brand = product.get('informations', {}).get('brand')
#             category = product.get('informations', {}).get('category')
#             price = product.get('prices', {}).get('unitPrice', {}).get('concatenated')
#             price_per_unit = product.get('prices', {}).get('productPrice', {}).get('concatenated')
#             image_url = product.get('informations', {}).get('allImages', [{}])[0].get('src')
#             #origin = product.get('informations', {}).get('originPlp')
#             product_url = product.get('url')
            
#             product_list.append({
#                 'Product ID': product_id,
#                 'EAN': ean,
#                 'Packaging': packaging,
#                 'Brand': brand,
#                 'Category': category,
#                 'Title': title,
#                 'Price': price,
#                 'Price Per Unit': price_per_unit,
#                 'Image URL': image_url,
#                 #'Origin': origin,
#                 'Product URL': product_url
#             })

#             # Print or store the extracted data
#             # print(f"Product ID: {product_id}")
#             # print(f"Title: {title}")
#             # print(f"Price: {price}")
#             # print(f"Image URL: {image_url}")
#             # print(f"Origin: {origin}")
#             # print("-" * 40)
#     except json.JSONDecodeError:
#         print("Error decoding JSON for a match.")

# df_products = pd.DataFrame(product_list)
# df_products
# #%%

#%%
#### ENCONTRANDO CATEGORIAS ####
starting_url = "https://www.loja-online.intermarche.pt/shelves/frutas-e-legumes/frutas/laranjas-e-outros-citrinos/11510"
try:
    response = make_request(starting_url, headers, payload)
    # Process the response
except Exception as e:
    print(f"Final error: {e}")
match = re.search(r'window\.__REACT_ESI__\[.*?\] = \{.*?"categories":(.*?)};\s*document\.currentScript\.remove\(\);', response.text, re.DOTALL)

if match:
    categories_json_str = match.group(1).strip()
    
    # Step 3: Convert the extracted string into a Python dictionary
    categories_data = json.loads(categories_json_str)
    
    # Step 4: Flatten the category tree into a list of dictionaries
    categories_list = []

    def extract_categories(tree):
        for node in tree:
            category_info = {
                "level": node.get("level"),
                "isPromo": node.get("isPromo"),
                "id": node.get("id"),
                "key": node.get("key"),
                "title": node.get("title"),
                "slug": node.get("slug"),
                "link": node.get("link"),
                "picto": node.get("picto"),
                "hasAlcohol": node.get("hasAlcohol")
            }
            categories_list.append(category_info)
            # Recur for children if any
            if "children" in node:
                extract_categories(node["children"])

    # Start extracting from the root of the category tree
    extract_categories(categories_data["tree"])

    # Step 5: Create a DataFrame from the flattened list
    df_categories = pd.DataFrame(categories_list)

levels = df_categories.query("level == 3")
print(f'There are {levels.shape[0]} categories to scrape')
#%%

#%%
df_products = pd.DataFrame()
for index, row in levels.iterrows():
    print(row['title'])
    if index % 10 == 0:
      print(index)
      time.sleep(random.uniform(10, 20))
    url = f"https://www.loja-online.intermarche.pt{row['link']}"
    print(url)
    #response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    try:
        response = make_request(url, headers, payload)
        # Process the response
    except Exception as e:
        print(f"Final error: {e}")

    js_data_matches = re.findall(r'window\.__REACT_ESI__\[.*?\] = (\{.*?\});', response.text, re.DOTALL)

    product_list = []

    # Step 2: Iterate over each match and extract the products
    for js_data_str in js_data_matches:
        try:
            # Convert the extracted string to a Python dictionary
            js_data = json.loads(js_data_str)
            
            # Access the products list
            products = js_data.get('list', {}).get('products', [])
            
            # Step 3: Extract details from each product
            for product in products:
                product_id = product.get('id')
                title = product.get('informations', {}).get('title')
                ean = product.get('ean')
                family = product.get('famillyId')
                department = product.get('departmentId')
                packaging = product.get('informations', {}).get('packaging')
                brand = product.get('informations', {}).get('brand')
                category = product.get('informations', {}).get('category')
                price = product.get('prices', {}).get('unitPrice', {}).get('concatenated')
                price_per_unit = product.get('prices', {}).get('productPrice', {}).get('concatenated')
                image_url = product.get('informations', {}).get('allImages', [{}])[0].get('src')
                promo_end = product.get('informations', {}).get('highlight', {}).get('endDate')
                #origin = product.get('informations', {}).get('originPlp')
                product_url = product.get('url')
                
                product_list.append({
                    'Product ID': product_id,
                    'Title': title,
                    'EAN': ean,
                    'Family ID': family,
                    'Department ID': department,
                    'Packaging': packaging,
                    'Brand': brand,
                    'Category': category,
                    'Price': price,
                    'Price Per Unit': price_per_unit,
                    'Image URL': image_url,
                    'Promo End': promo_end,
                    #'Origin': origin,
                    'Product URL': product_url
                })

                # Print or store the extracted data
                # print(f"Product ID: {product_id}")
                # print(f"Title: {title}")
                # print(f"Price: {price}")
                # print(f"Image URL: {image_url}")
                # print(f"Origin: {origin}")
                # print("-" * 40)
        except json.JSONDecodeError:
            print("Error decoding JSON for a match.")

    aux_products = pd.DataFrame(product_list)
    df_products = pd.concat([df_products, aux_products])

today = datetime.now().strftime("%Y%m%d")
today_dir = os.path.join("./data/", today)
print("Salvando ficheiros")
os.makedirs(today_dir, exist_ok=True)
filename_csv = os.path.join(today_dir,f"{today}_all_products_intermarche.csv")
filename_pkl = os.path.join(today_dir,f"{today}_all_products_intermarche.pkl")
df_products.to_csv(filename_csv,encoding='utf-8-sig', index=False)
df_products.to_pickle(filename_pkl)


#%%
