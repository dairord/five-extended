class KMLDocument:
    def __init__(self, title):
        self.title = title
        self.polygons = []
        self.paths = []
        pass

    def addPath(self, coordinates, color, name):
        path = {"coordinates": coordinates, "color": color, "name": name}
        self.paths.append(path)


    def addPolygon(self, coordinates, color, type, altitude=0):
        polygon = {"coordinates": coordinates, "color": color, "type": type, "altitude": altitude}
        self.polygons.append(polygon)

    def polygonToString(self):
        res = ""
        for polygon in self.polygons:
            ((x1, y1), (x2, y2), (x3, y3), (x4, y4)) = polygon["coordinates"]
            z = polygon["altitude"]
            polystr = f"""    <Placemark>
                        <name>{polygon['type']}</name>
                        <Style>
                            <LineStyle>
                                <color>{polygon['color']}</color>
                                <width>2</width>
                            </LineStyle>
                            <PolyStyle>
                                <fill>0</fill>
                            </PolyStyle>
                        </Style>
                        <Polygon>
                            <extrude>1</extrude>
                            <altitudeMode>absolute</altitudeMode>
                            <outerBoundaryIs>
                                <LinearRing>
                                    <coordinates>
                                        {x1},{y1},{z} {x2},{y2},{z} {x3},{y3},{z} {x4},{y4},{z} {x1},{y1},{z}
                                    </coordinates>
                                </LinearRing>
                            </outerBoundaryIs>
                        </Polygon>
                    </Placemark>\n"""
            res += polystr
        return res

    def pathToString(self):
        res = ""
        for path in self.paths:
            coordinates = path["coordinates"]
            res += f"""
                        <Placemark>
                            <name>{path["name"]}</name>
                            <LineString>
                            <coordinates>
                    """
            for point in coordinates:
                res += f"""
                                {point.x},{point.y},0
                        """
            res += f"""
                            </coordinates>
                            </LineString>
                        </Placemark>
                    """
        return res

    def __str__(self):
        res = f"""<?xml version="1.0" encoding="UTF-8"?>
            <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
            <Document>
                <name>Pruebita</name>\n"""
        res += self.polygonToString()
        if(len(self.paths) > 0):
            res += self.pathToString()
        res += "</Document>\n</kml>"
        return res
