from enum import Enum, auto
import xml.etree.ElementTree as ET

class File_Type(Enum):
    ORIGINAL_IMAGE = "ORIGINAL"
    FINAL_IMAGE = auto()
    GRID_MAP = auto()
    JSON_MAP = auto()
    ELEVATION_TIF = "ELEVATIONS"
    GENERATED_TIF = "TIF"
    REPROJECTED_TIF = auto()
    COORDINATES = "COORDINATES"

class KMLDocument:
    def __init__(self, title):
        self.title = title
        self.polygons = []
        self.paths = []
        self.files = []
        self.coordinates = []
        pass

    def addPath(self, coordinates, color, name):
        path = {"coordinates": coordinates, "color": color, "name": name}
        self.paths.append(path)


    def add_polygon(self, coordinates, color, type, altitude=0):
        polygon = {"coordinates": coordinates, "color": color, "type": type, "altitude": altitude}
        self.polygons.append(polygon)

    def add_extra_data(self, file_type: File_Type , file_name):
        file_extension = None
        if file_type == File_Type.ORIGINAL_IMAGE:
            file_extension = "png"
        elif file_type == File_Type.JSON_MAP:
            file_extension = "json"
        else:
            file_extension = "tif"
        extra_data = {"name": file_name, "type": file_type.value, "extension": file_extension}
        self.files.append(extra_data)

    def add_coordinates(self, latitude, longitude):
        point = {"latitude": latitude, "longitude": longitude}
        self.coordinates.append(point)

    def data_to_KML(self):
        res = "             <ExtendedData>"
        res += self.files_to_KML()
        res += self.coordinates_to_KML()
        res += "\n              </ExtendedData>\n"
        return res
    
    def coordinates_to_KML(self):
        res = f"""\n                <Data name="{File_Type.COORDINATES.value}">"""
        for point in self.coordinates:
            latitude = point["latitude"]
            longitude = point["longitude"]
            data_string = f"""
                    <value>{latitude},{longitude}</value>"""
            res += data_string
        res += """\n            </Data>"""
        return res
    
    def files_to_KML(self):
        res = ""
        for file in self.files:
            name = file["name"]
            file_type = file["type"]
            file_extension = file["extension"]
            data_string = f"""
                <Data name="{file_type}">
                    <value>{name}.{file_extension}</value>
                </Data>"""
            res += data_string
        return res
    
    def polygon_to_KML(self):
        res = ""
        for polygon in self.polygons:
            ((x1, y1), (x2, y2), (x3, y3), (x4, y4)) = polygon["coordinates"]
            z = polygon["altitude"]
            polystr = f"""                    <Placemark>
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
                            <altitudeMode>relative</altitudeMode>
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

    def path_to_KML(self):
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
                <name>{self.title}</name>\n"""
        res += self.data_to_KML()
        res += self.polygon_to_KML()
        if(len(self.paths) > 0):
            res += self.path_to_KML()
        res += "                </Document>\n           </kml>"
        return res




def search_custom_fields_in_document(kml_file, custom_field_names):
    tree = ET.parse(kml_file)
    root = tree.getroot()

    namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

    document = root.find('.//kml:Document', namespaces)
    if document is not None:
        # Find the ExtendedData element within the Document
        extended_data = document.find('.//kml:ExtendedData', namespaces)
        if extended_data is not None:
            data_elements = extended_data.findall('kml:Data', namespaces)
            custom_fields_values = {field_name: [] for field_name in custom_field_names}
            for data_element in data_elements:
                field_name = data_element.get('name')
                if field_name in custom_field_names:
                    # Get all value elements within the Data element
                    value_elements = data_element.findall('kml:value', namespaces)
                    for value_element in value_elements:
                        if value_element is not None:
                            custom_fields_values[field_name].append(value_element.text.strip())
            return custom_fields_values
    return {field_name: [] for field_name in custom_field_names}