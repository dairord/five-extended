import json
from pathlib import Path
import time
import requests
import certifi
import os

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(certifi.where())

# The endpoint URL
url = 'https://centrodedescargas.cnig.es/CentroDescargas/descargaDir'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Referer': 'https://centrodedescargas.cnig.es/CentroDescargas/index.jsp',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'centrodedescargas.cnig.es',
    'Origin': 'https://centrodedescargas.cnig.es',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

cookies = {
    # 'JSESSIONID': 'F4CD9F017FABF4EC74D84A9315944127',
    '_ga': 'GA1.1.1378021722.1707671118',
    '_fbp': 'fb.1.1707671118098.2100817625',
    '__utmc': '103291538',
    '__utmz': '103291538.1707671145.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    '__utma': '103291538.1378021722.1707671118.1712599149.1717345626.3',
    '__utmt': '1',
    '__utmb': '103291538.2.10.1717345626',
    '_ga_MHC1KPDP10': 'GS1.1.1717343720.20.1.1717345680.0.0.0'
}

data_template = {
    'codSerieMD': 'MDT02',
    'secDescDirLA': '',  
    'filtroContiene': '',
    'pagActual': '1',
    'numTotReg': '6',
    'codSerieSel': 'MDT02'
}

# Mapas de 25m
    # 'codSerieMD': '02107',
    # 'codSerieSel': '02107'


base_dir = Path(__file__).parent.parent
elevations_dir = base_dir / "elevations"
elevations_dir.mkdir(parents=True, exist_ok=True)

def build_data(tif_code, resolution_code):
    data = data_template.copy()
    data['secDescDirLA'] = tif_code
    data['codSerieMD'] = resolution_code
    data['codSerieSel'] = resolution_code
    return data

def download_elevation(tif_code, resolution_code):
    with requests.Session() as session:
        data = build_data(tif_code, resolution_code)
        initial_get = session.get(url, headers=headers, verify=False, cookies=cookies)
        
        response = session.post(url, headers=headers, data=data, verify=False, cookies=cookies)

        if response.ok and 'image/tiff' in response.headers.get('Content-Type', ''):
            name = f"spain_elevation_{tif_code}.tif"
            file_path = elevations_dir / name
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return response.content
        else:
            # error_file_path = elevations_dir / f"error_{index}.html"
            # with open(error_file_path, 'wb') as file:
            #     file.write(response.content)
            return None
# tif_code = '9073493'
# for i in range(5):
#     download_elevation(tif_code, i)
#     time.sleep(100)
