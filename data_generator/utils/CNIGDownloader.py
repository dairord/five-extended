import json
from pathlib import Path
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import certifi
import os
os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(certifi.where())
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1
base_dir = Path(__file__).parent.parent

# The endpoint URL
url = 'https://centrodedescargas.cnig.es/CentroDescargas/descargaDir'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0 Safari/537.36',
    'Referer': 'https://centrodedescargas.cnig.es/CentroDescargas/index.jsp',
}

cookies = {
    'JSESSIONID': 'F62CDFBD330A6EE0526A8B7FED452A83',
}

# data = {
#     'codSerieMD': '02107',          
#     'secDescDirLA': '9073493',      
#     'filtroContiene': '',           
#     'pagActual': '1',               
#     'numTotReg': '50',             
#     'codSerieSel': '02107'          
# }

def build_data(tif_code):
    return json.dumps({
    'codSerieMD': '02107',          
    'secDescDirLA': [tif_code],      
    'filtroContiene': '',           
    'pagActual': '1',               
    'numTotReg': '50',             
    'codSerieSel': '02107'          
})

def download_elevation(tif_code):
    with requests.Session() as session:
        data = build_data(tif_code)
        print("1--------------------------------------------------------------------------------------------------------------------------------------------------------------")
        session.get('https://centrodedescargas.cnig.es/CentroDescargas/descargaDir', verify=False)
        session.cookies.update(cookies)
        print("2--------------------------------------------------------------------------------------------------------------------------------------------------------------")
        
        response = session.post(url, data=data, verify=False)

        print("3--------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print(response.status_code)
        print(response.headers)

        if response.ok:
            
            with open(str(base_dir / "elevations" / "spain_elevation_" + tif_code + ".tif"), 'wb') as file:
                file.write(response.content)
        else:
            print("Failed to download the file.")
