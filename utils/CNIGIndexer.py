import json
from pathlib import Path
import requests
import urllib3
import certifi
import os
import http.client as http_client
import time
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(certifi.where())
http_client.HTTPConnection.debuglevel = 1
base_dir = Path(__file__).parent.parent



def get_tif_list(elevation_indexes):
    if isinstance(elevation_indexes, bytes):
        elevation_indexes = elevation_indexes.decode('utf-8')
    pattern = r'linkDescDir_([a-zA-Z0-9]+)'
    matches = re.findall(pattern, elevation_indexes)
    return matches

url = "https://centrodedescargas.cnig.es/CentroDescargas/resultadosArchivos"

headers = {
  "Accept": "text/html, */*; q=0.01",
  "Accept-Encoding": "gzip, deflate, br, zstd",
  "Accept-Language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
  "Connection": "keep-alive",
  "Content-Length": "431",
  "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
  "Host": "centrodedescargas.cnig.es",
  "Origin": "https://centrodedescargas.cnig.es",
  "Referer": "https://centrodedescargas.cnig.es/CentroDescargas/index.jsp",
  "Sec-Ch-Ua": "\"Microsoft Edge\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
  "Sec-Ch-Ua-Mobile": "?0",
  "Sec-Ch-Ua-Platform": "\"Windows\"",
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-origin",
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
  "X-Requested-With": "XMLHttpRequest"
}

cookies = {
    # "JSESSIONID": "F62CDFBD330A6EE0526A8B7FED452A83",
    "_ga":"GA1.1.1378021722.1707671118",
    "_fbp":"fb.1.1707671118098.2100817625",
    "__utmc":"103291538",
    # "__utmz":"103291538.1707671145.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
    "_ga_MHC1KPDP10":"GS1.1.1712596351.10.1.1712596997.0.0.0",
    "__utma":"103291538.1378021722.1707671118.1707671145.1712599149.2"
}

def buildPetitionBody(coordinates, resolution_code):
    ((x1, y1), (x2, y2), (x3, y3), (x4, y4)) = coordinates

    return {
    'geom': 'Polygon',
    'coords': json.dumps({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [x1,y1],
                            [x2,y2],
                            [x3,y3],
                            [x4,y4],
                            [x1,y1]
                        ]
                    ]
                }
            }
        ]
    }),
    'numPagina': '1',
    'numTotalReg': '30',
    'codSerie': resolution_code,
    'series': resolution_code,
    'codProvAv': '',
    'codIneAv': '',
    'codComAv': '',
    'numHojaAv': '',
    'todaEsp': '',
    'todoMundo': '',
    'tipoBusqueda': 'VI',
    'contiene': 'ETRS89',
    'idProcShape': '',
    'orderBy': ''
}


# Mapas 25m
    # 'codSerie': '02107',
    # 'series': '02107',
# Mapas 5m
    # 'codSerie': 'MDT05',
    # 'series': 'MDT05',
# Mapas 2m
    # 'codSerie': 'MDT02',
    # 'series': 'MDT02',




def getIndex(coordinates, resolution_code):
    body = buildPetitionBody(coordinates, resolution_code)
    headers['Content-Length'] = str(len(requests.models.RequestEncodingMixin._encode_params(body)))

    with requests.Session() as session:
        session.get('https://centrodedescargas.cnig.es/CentroDescargas/resultadosArchivos', verify=False)
        
        response = session.post(url, data=body, headers=headers, verify=False)
        if response.ok:
            with open(str(base_dir / "elevations" / "indexer.html"), "wb") as file:
                file.write(response.content)
            return response.content
        else:
            return None


# coords2 = [-5.101967049436507, 40.588499937840766], [-5.08643003520145, 41.415137431052784], [-3.7269412896340524, 41.397657422653964], [-3.7075200218402324, 40.57965022364732]

# coords = [
#     [-0.514737, 39.489113],
#     [-0.514083, 39.489113],
#     [-0.514083, 39.48882],
#     [-0.514737, 39.48882]
# ]
# for i in range(0, 5):

#     res = getIndex(coords2)
#     if res != None:
#         print(get_tif_list(res))
#     time.sleep(100)


