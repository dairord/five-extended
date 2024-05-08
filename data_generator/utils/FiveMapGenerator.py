import json


class FiveMap:
    def __init__(self, title):
        self.title = title
        self.polygons = []

    def addPolygon(self, coordinates, type, color, elevation = 0):
        polygon = {
            "coordinates": coordinates,
            "color": color,
            "type": type,
            "elevation": float(elevation),
        }
        self.polygons.append(polygon)

    def __str__(self):
        objects = [
            {
                "active": True,
                "objectName": f"{polygon['type']} {i+1}",
                "objectPrefabName": polygon["type"],
                "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
                "metadata": {
                    "areaCoordinates": [
                        {"latitude": y, "longitude": x}
                        for x, y in polygon["coordinates"]
                    ],
                    "elevation": polygon["elevation"],
                },
            }
            for i, polygon in enumerate(self.polygons)
        ]
        return json.dumps({"objects": objects}, indent=4)
