import numpy as np
import cv2
import os

import rasterio
from utils.tiffGenerator import point_to_square_coordinates
from utils.kmlGenerator import KMLDocument

distancia = 48


def tr_colores(color):
    if color == "B":
        return "Negro"
    elif color == "C":
        return "Azul"
    elif color == "D":
        return "Rojo"
    elif color == "E":
        return "Verde"
    elif color == "G":
        return "Azul claro"
    elif color == "H":
        return "Blanco"
    elif color == "I":
        return "Amarillo"
    elif color == "J":
        return "Rosa"
    return "Empty"


def create_mask(img, lowerbound, upperbound):
    mask = cv2.inRange(img, lowerbound, upperbound)
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return masked_img


def create_otsu(masked_img):
    gray_img = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray_img, (19, 19), 0)
    _, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thr


def create_image_detection(contours, img, generate_kml):
    x, y, w, h = cv2.boundingRect(contours[0])
    miny = y
    maxy = y
    minx, maxx = x, x
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if y < miny:
            miny = y
        if y > maxy:
            maxy = y
        if x < minx:
            minx = x
        if x > maxx:
            maxx = x
    
    nlineasy = (maxy - miny) // distancia + 1
    nlineasx = (maxx - minx) // distancia + 1

    terreno = np.empty((nlineasy, nlineasx), dtype=str)
    terreno[:][:] = " "
    ocupacion = np.empty((nlineasy, nlineasx), dtype=int)
    ocupacion[:][:] = 0
    kml = KMLDocument("Pruebita")
    transform = ""
    with rasterio.open("geolocated.tiff") as dataset:
        transform = dataset.transform
    for contour in contours:
        # Calcular el área del contorno
        area = cv2.contourArea(contour)

        # Si el área es mayor que el umbral mínimo, dibujar un cuadrado que encierra el contorno
        if area > 25 and area < 2000:  # Cambio Luis 500->25
            # Calcular los momentos del contorno
            M = cv2.moments(contour)
            # Calcular el centro del contorno
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Imprimir el centro del contorno
            # print("Centro: ({}, {})".format(cx, cy))

            x, y, w, h = cv2.boundingRect(contour)
            # print("Objeto encontrado en ({}, {}), ancho = {}, alto = {} con el area de {}".format(x, y, w, h,area))
            aux += 1

            # Quitamos un 0 a todo
            if area <= 210:  # 70:
                letra = "B "
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 2)  # Negro
                if (generate_kml): kml.addPolygon(
                    point_to_square_coordinates(x, y, w, h, transform),
                    "ff000000",
                    "Black",
                )
            elif area <= 290:  # 120:
                letra = "C "
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Azul
                if (generate_kml): kml.addPolygon(
                    point_to_square_coordinates(x, y, w, h, transform),
                    "ffff0000",
                    "Blue",
                )
            elif area <= 370:  # 170:
                letra = "D "
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Rojo
                if (generate_kml): kml.addPolygon(
                    point_to_square_coordinates(x, y, w, h, transform),
                    "ff0000ff",
                    "Red",
                )
            elif area <= 450:  # 210:
                letra = "E "
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Verde
                if (generate_kml): kml.addPolygon(
                    point_to_square_coordinates(x, y, w, h, transform),
                    "ff00ff00",
                    "Green",
                )
            elif area <= 530:  # 250:
                letra = "G "
                cv2.rectangle(
                    img, (x, y), (x + w, y + h), (255, 255, 0), 2
                )  # Azul Claro
                if (generate_kml): kml.addPolygon(
                    point_to_square_coordinates(x, y, w, h, transform),
                    "ffffff00",
                    "Light Blue",
                )
            elif area <= 610:  # 290:
                letra = "H "
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)  # Blanco
                if (generate_kml): kml.addPolygon(
                    point_to_square_coordinates(x, y, w, h, transform),
                    "ffffffff",
                    "White",
                )
            elif area <= 690:  # 330:
                letra = "I "
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)  # Amarillo
                if (generate_kml): kml.addPolygon(
                    point_to_square_coordinates(x, y, w, h, transform),
                    "ff00ffff",
                    "Yellow",
                )
            else:
                letra = "J "
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)  # Rosa
                if (generate_kml): kml.addPolygon(
                    point_to_square_coordinates(x, y, w, h, transform),
                    "ffff00ff",
                    "Pink",
                )
            
            locate_char(x, y, w, h, letra, terreno, ocupacion)

    with open("myfile.kml", "w") as file:
        # Write the string to the file
        file.write(str(kml))
    
    return terreno

    

def locate_char(x, y, w, h, letra, terreno, ocupacion):
    PosX = int((x + w / 2) // distancia)
    PosY = int((y + h / 2) // distancia)

    if letra > terreno[PosY][PosX]:
        terreno[PosY][PosX] = letra
    ocupacion[PosY][PosX] += 1
    if w > distancia:
        lonw = w // distancia
        if w % distancia > (0.35 * distancia):
            lonw += 1

            if lonw % 2 == 0:
                dif = distancia / 2
                cenX = x + w / 2
                for i in range(0, lonw // 2):
                    PosX = int((cenX + dif) // distancia)
                    #                            print("Derecha ", PosY, cenY, dif)
                    if letra > terreno[PosY][PosX]:
                        terreno[PosY][PosX] = letra
                    dif += distancia
                dif = -distancia / 2
                for i in range(0, lonw // 2):
                    PosX = int((cenX + dif) // distancia)
                    #                            print("izquierda ", PosY, cenY, dif)
                    if letra > terreno[PosY][PosX]:
                        terreno[PosY][PosX] = letra
                    dif -= distancia
            else:
                for i in range(1, lonw // 2 + 1):
                    if letra > terreno[PosY][PosX + i]:
                        terreno[PosY][PosX + i] = letra
                    if letra > terreno[PosY][PosX - i]:
                        terreno[PosY][PosX - i] = letra
    if h > distancia:
        lonh = int(h // distancia)
        #                print("longh ", lonh, h%distancia, PosY, PosX, y, h)
        if h % distancia > (0.35 * distancia):
            lonh += 1

            if lonh % 2 == 0:
                dif = distancia / 2
                cenY = y + h / 2
                for i in range(0, lonh // 2):
                    PosY = int((cenY + dif) // distancia)
                    #                            print("Derecha ", PosY, cenY, dif)
                    if letra > terreno[PosY][PosX]:
                        terreno[PosY][PosX] = letra
                    dif += distancia
                dif = -distancia / 2
                for i in range(0, lonh // 2):
                    PosY = int((cenY + dif) // distancia)
                    #                            print("izquierda ", PosY, cenY, dif)
                    if letra > terreno[PosY][PosX]:
                        terreno[PosY][PosX] = letra
                    dif -= distancia
            else:
                for i in range(1, lonh // 2 + 1):
                    if letra > terreno[PosY + i][PosX]:
                        terreno[PosY + i][PosX] = letra
                    if letra > terreno[PosY - i][PosX]:
                        terreno[PosY - i][PosX] = letra

    

def main_process(imagen):
    global distancia
    distancia = 48
    aux = 0
    auxY = 0
    if os.path.exists("map.txt"):
        os.remove("map.txt")

    # Load image
    img = cv2.imread(imagen)

    # Define upper and lower bounds for vegetation detection
    upperbound = np.array([70, 255, 50]) 
    lowerbound = np.array([0, 0, 0])

    # Create mask for vegetation detection
    # Apply mask to original image
    masked_img = create_mask(img, lowerbound, upperbound)

    # Convert image to grayscale and apply blur
    # Apply Otsu threshold
    thr = create_otsu(masked_img)

    # Encontrar contornos de las regiones blancas en la imagen
    contours = find_and_sort_contours(thr)

    terreno = create_image_detection(contours, img, False)

    escribirTextoMatriz(terreno)
    colores = f"colores.png"
    filtro = f"filtro.png"
    otsu = f"otsu.png"
    if cv2.imwrite(colores, img):
        print("Se ha creado la imagen correctamente con el nombre de " + colores)
    if cv2.imwrite(filtro, masked_img):
        print("Se ha creado la imagen correctamente con el nombre de " + filtro)
    if cv2.imwrite(otsu, thr):
        print("Se ha creado la imagen correctamente con el nombre de " + otsu)




def calcular_centro(contour, esY):
        m = cv2.moments(contour)
        if m["m00"] != 0:
            if esY:
                ratio = m["m01"] / m["m00"]
            else:
                ratio = m["m10"] / m["m00"]
        else:
            ratio = 0.0
        return ratio



def find_and_sort_contours(thr):
    contours, hierarchy = cv2.findContours(
        thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(
        contours,
        key=lambda contour: (
            calcular_centro(contour, True),
            calcular_centro(contour, False),
        ),
    )
    i = 0
    while i < len(contours) - 1:
        contour = contours[i]
        next_contour = contours[i + 1]

        y = calcular_centro(contours[i], True)
        next_y = calcular_centro(contours[i + 1], True)
        x = calcular_centro(contours[i], False)
        next_x = calcular_centro(contours[i + 1], False)
        if next_y - y < 50:
            # Ordenar por X
            if x > next_x:
                contours[i], contours[i + 1] = next_contour, contour
                i = 0
            else:
                i += 1
        else:
            i += 1
    
    return contours

def escribirTextoMatriz(matriz):
        with open("map.txt", "w") as file:
            filas, cols = matriz.shape
            for i in range(filas):
                for j in range(cols):
                    file.write(matriz[i][j] + " ")
                file.write("\n")