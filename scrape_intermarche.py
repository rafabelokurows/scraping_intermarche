# %%
import os
from datetime import datetime
import time
import requests
import json
import pandas as pd
import math
import random
import ua_generator

url = "https://www.loja-online.intermarche.pt/api/service/produits/v2/pdvs/07348/boutiques/2119"
# %%

# %%
today = datetime.now().strftime("%Y%m%d")
today_dir = os.path.join("./data/", today)
#os.chdir(today_dir)
# %%

# %%
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8,es;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://www.loja-online.intermarche.pt',
    'Referer': 'https://www.loja-online.intermarche.pt/shop/2119',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'sec-ch-device-memory': '8',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="125.0.6422.76", "Chromium";v="125.0.6422.76", "Not.A/Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'x-itm-device-fp': 'c73252c9-4bcb-4bf5-b2d4-87fad19d21fd',
    'x-itm-session-id': 'b8acba50-7dcf-4192-ab67-fd0d91cccb6a',
    'x-pdv': '{"ref":"07348","isEcommerce":true}',
    'x-red-device': 'red_fo_desktop',
    'x-red-version': '3',
    'x-service-name': 'produits'
}
# %%

# %%
def expand_list_of_dicts(lst):
        if isinstance(lst, list) and lst:
            return pd.DataFrame(lst).add_prefix('pictogrammes_')
        else:
            return pd.DataFrame([{}])
            
def fetch_and_process_data(page, headers , return_number_pages=True):
    # Body of the request
    body = {
        "page": page,
        "size": 100,
        "filtres": [{"type": "3", "id": "2"}],
        "tri": "pertinence",
        "ordreTri": None,
        "catalog": ["PDV"]
    }
    s.headers.update(ua.headers.get())
    # Making the POST request
    response = s.post(url, headers=headers, data=json.dumps(body), verify=False)

    # Parsing the JSON response
    json_data = response.json()

    # Extracting products
    #products = json_data['produits']
    try:
        # Extracting products
        products = json_data['produits']
    except KeyError:
        # Handle the case where 'produits' key is not found
        print("Error: Page is blocking web scraping attempt.")
        products = []
    products_df = pd.DataFrame(products)

    if products_df.empty:
        if return_number_pages == True:
            return products_df, 0
        else:
            return products_df
    # Selecting specific columns
    # selected_columns = [
    #     'identifier', 'idProduit', 'itemId', 'produitEan13', 'typeProduit', 'unitePrixVente', 'pviIncrement', 'capacite', 
    #     'qteMaxPanier', 'marque', 'libelle', 'conditionnement', 'images', 'prix', 'unitPrice', 'prixKg', 'prixBarre', 
    #     'vignetteCollector', 'pictogrammes', 'poidsMinimum', 'poidsNet', 'poidsUnite', 'volume', 'isTrad', 
    #     'isPresentAlcoholProduct', 'avantages', 'origine', 'categorie', 'nbPiece'
    # ]
    selected_columns = [

        'identifier', 'produitEan13','capacite', 'typeProduit', 'unitePrixVente', 
         'marque', 'libelle', 'conditionnement', 'images', 'prix', 'unitPrice',  
        'pictogrammes', 'volume', 'avantages'
    ]
    #products_df[selected_columns]
    aux_produtos = products_df.reindex(columns=selected_columns)

    #Added verification in case there is more than one pictogramme per product (which was throwing an error before)
    nro_picto = aux_produtos['pictogrammes'].explode().reset_index(drop=True).apply(pd.Series).shape[0]
    if nro_picto == aux_produtos.shape[0]:
        aux_produtos = aux_produtos.assign(
        **aux_produtos['typeProduit'].apply(pd.Series).add_prefix('typeProduit_'),
        **aux_produtos['unitePrixVente'].apply(pd.Series).add_prefix('unit_'),
        **aux_produtos['pictogrammes'].explode().apply(pd.Series).add_prefix('pictogrammes_'),
        **aux_produtos['avantages'].explode().apply(pd.Series).add_prefix('avantages_'),
        **aux_produtos['images'].apply(pd.Series).add_prefix('images_')
        ).drop(columns=['typeProduit', 'unitePrixVente', 'images'])
        
    else:
        aux_produtos = aux_produtos.assign(
        **aux_produtos['typeProduit'].apply(pd.Series).add_prefix('typeProduit_'),
        **aux_produtos['unitePrixVente'].apply(pd.Series).add_prefix('unit_'),
        **aux_produtos['avantages'].explode().apply(pd.Series).add_prefix('avantages_'),
        **aux_produtos['images'].apply(pd.Series).add_prefix('images_')
        ).drop(columns=['typeProduit', 'unitePrixVente', 'images'])
        
        pictogrammes_expanded = pd.concat([expand_list_of_dicts(row) for row in aux_produtos['pictogrammes']], keys=aux_produtos.index).reset_index(level=1, drop=True)
        pictogrammes_df = pictogrammes_expanded.groupby(level=0).first().reindex(aux_produtos.index)
        
        aux_produtos = pd.concat([aux_produtos.drop(columns=['pictogrammes']),pictogrammes_df],axis=1)

    # Adding the 'page' column
    #aux_produtos['page'] = page
    
    # aux_produtos = aux_produtos[['identifier', 'produitEan13', 'capacite', 'marque', 'libelle', 'conditionnement',
    #    'prix', 'unitPrice',  'volume',  
    #    'typeProduit_uniteByCode', 'unit_value', 
    #    'pictogrammes_libelleCategorie', 'avantages_dateFin', 'avantages_categorie',
    #    'images_0', 'images_1', 'images_2', 'images_3']]
    aux_produtos = aux_produtos.drop(columns=['pictogrammes','avantages','pictogrammes_idPicto','pictogrammes_idCategorie','pictogrammes_image','typeProduit_code','typeProduit_value','pictogrammes_infoBulle','pictogrammes_0'])    
    aux_produtos['nro_paginas'] = json_data['searchResultsMetaData']['totalPageNbre']
    nro_paginas = json_data['searchResultsMetaData']['totalPageNbre']

    if return_number_pages == True:
        # Extracting the total number of pages
        return aux_produtos, nro_paginas
    else:
        return aux_produtos
# %% 

# %%
filename = f"{today}_intermarche.csv"
#file_path = os.path.join(os.getcwd(), filename)
file_path = os.path.join(today_dir, filename)
ua = ua_generator.generate(browser=('chrome', 'edge'))
s = requests.Session()
s.verify = False
if os.path.exists(file_path):
    print(f"File '{filename}' exists in the folder '{os.getcwd()}'.")
    df = pd.read_csv(file_path)
    ultima_pagina = max(df.page)
    nro_paginas = max(df.nro_paginas)
    print(f"Ultima pagina obtida foi: {ultima_pagina}")
    pagina = ultima_pagina+1
    print(f"Proxima pagina será: {pagina}")
    print(f"Numero total de paginas: {nro_paginas}")
else:
    print(f"File '{filename}' does not exist in the folder '{os.getcwd()}'.")
    pagina = 1
    print(f"Proxima pagina será: {pagina}")
    
# %%
if pagina == 1:
    print("Tentando primeira página")
    df = fetch_and_process_data(1, headers,return_number_pages=False)
    print(f"Obtidos '{df.shape[0]}' produtos da página 1.")
    nro_paginas = max(df.nro_paginas)
    print(f"Numero total de paginas: {nro_paginas}")
    if(df.shape[0] == 100):
        pagina = 2
# %%

print("Continuando obtenção de produtos")
for i in range(pagina, nro_paginas+1):
    print(f"Page: {i}")
    
    aux_df = fetch_and_process_data(i, headers,return_number_pages=False)
    if aux_df.shape[0] == 0:
        print(f"No products found on page {i}. Stopping the loop.")
        break
    time.sleep(random.uniform(10, 60))

    print(f"Obtidos {aux_df.shape[0]} produtos da página {i}.")
    # Combining the current data with the total products DataFrame
    df = pd.concat([df, aux_df], ignore_index=True)
s.close()

if (max(df.page) == nro_paginas):
    with open('./log/last_execution.txt', 'w') as f:
        f.write(today)

print("Salvando ficheiros")
os.makedirs(today_dir, exist_ok=True)
filename_csv = os.path.join(today_dir,f"{today}_intermarche.csv")
filename_pkl = os.path.join(today_dir,f"{today}_intermarche.pkl")
df.to_csv(filename_csv,encoding='utf-8-sig', index=False)
df.to_pickle(filename_pkl)
#df.to_pickle(f"{today}_intermarche.pkl")
#df.to_csv(f"{today}_intermarche.csv",encoding='utf-8-sig', index=False)
