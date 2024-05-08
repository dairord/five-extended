import json
from pathlib import Path
import requests
import urllib3
import certifi
import os
import http.client as http_client
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(certifi.where())
http_client.HTTPConnection.debuglevel = 1
base_dir = Path(__file__).parent.parent

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

def buildPetitionBody(coordinates):
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
    'codSerie': '02107',
    'series': '02107',
    'codProvAv': '',
    'codIneAv': '',
    'codComAv': '',
    'numHojaAv': '',
    'todaEsp': '',
    'todoMundo': '',
    'tipoBusqueda': 'VI',
    'idProcShape': '',
    'orderBy': ''
}

def getIndex(coordinates):
    body = buildPetitionBody(coordinates)
    headers['Content-Length'] = str(len(requests.models.RequestEncodingMixin._encode_params(body)))

    with requests.Session() as session:
        session.get('https://centrodedescargas.cnig.es/CentroDescargas/resultadosArchivos', verify=False)
        # session.cookies.update(cookies)
        
        response = session.post(url, data=body, headers=headers, verify=False)
        # print(response.status_code)
        # print(response.headers)
        if response.ok:
            with open(str(base_dir / "elevations" / "indexer.html"), "wb") as file:
                file.write(response.content)
        else:
            print("Failed to download the content. Status code:", response.status_code)


coords = [-5.101967049436507, 40.588499937840766], [-5.08643003520145, 41.415137431052784], [-3.7269412896340524, 41.397657422653964], [-3.7075200218402324, 40.57965022364732]
for i in range(0, 5):

    getIndex(coords)
    time.sleep(100)