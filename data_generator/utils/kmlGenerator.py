class KMLDocument:
    def __init__(self, title):
        self.title = title
        self.polygons = []

    def addPolygon(self, coordinates, color, type):
        polygon = {"coordinates": coordinates, "color": color, "type": type}
        self.polygons.append(polygon)

    def __str__(self):
        res = f"""<?xml version="1.0" encoding="UTF-8"?>
            <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
            <Document>
                <name>Pruebita</name>\n"""
        for polygon in self.polygons:
            ((x1, y1), (x2, y2), (x3, y3), (x4, y4)) = polygon["coordinates"]
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
                            <outerBoundaryIs>
                                <LinearRing>
                                    <coordinates>
                                        {x1},{y1},0 {x2},{y2},0 {x3},{y3},0 {x4},{y4},0 {x1},{y1},0
                                    </coordinates>
                                </LinearRing>
                            </outerBoundaryIs>
                        </Polygon>
                    </Placemark>\n"""
            res += polystr
        res += "</Document>\n</kml>"
        return res
