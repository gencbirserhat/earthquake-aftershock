from flask import Flask, jsonify, request
import random
import uuid
from datetime import datetime, timezone, timedelta
from flasgger import Swagger, swag_from

app = Flask(__name__)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Sümilasyon Deprem API",
        "description": "Sahte deprem verisi sağlayan API",
        "version": "1.0",
    },
}

swagger = Swagger(app, template=swagger_template)

# Global fake earthquake list
earthquakes = []

city_coords = {
    "Adana": (37.0017, 35.3289),
    "Adıyaman": (37.7648, 38.2767),
    "Afyonkarahisar": (38.7638, 30.5401),
    "Ağrı": (39.7191, 43.0511),
    "Aksaray": (38.3687, 34.0360),
    "Amasya": (40.6521, 35.8336),
    "Ankara": (39.9334, 32.8597),
    "Antalya": (36.8841, 30.7056),
    "Ardahan": (41.1105, 42.7022),
    "Artvin": (41.1828, 41.8183),
    "Aydın": (37.8560, 27.8416),
    "Balıkesir": (39.6494, 27.8826),
    "Bartın": (41.5811, 32.4613),
    "Batman": (37.8812, 41.1351),
    "Bayburt": (40.2553, 40.2249),
    "Bilecik": (40.1500, 29.9829),
    "Bingöl": (38.8847, 40.4933),
    "Bitlis": (38.3995, 42.1101),
    "Bolu": (40.7370, 31.6063),
    "Burdur": (37.7203, 30.2886),
    "Bursa": (40.1950, 29.0600),
    "Çanakkale": (40.1553, 26.4142),
    "Çankırı": (40.6013, 33.6134),
    "Çorum": (40.5506, 34.9556),
    "Denizli": (37.7765, 29.0864),
    "Diyarbakır": (37.9144, 40.2306),
    "Düzce": (40.8438, 31.1565),
    "Edirne": (41.6771, 26.5557),
    "Elazığ": (38.6744, 39.2226),
    "Erzincan": (39.7500, 39.4914),
    "Erzurum": (39.9080, 41.2769),
    "Eskişehir": (39.7767, 30.5206),
    "Gaziantep": (37.0662, 37.3833),
    "Giresun": (40.9128, 38.3895),
    "Gümüşhane": (40.4601, 39.4813),
    "Hakkari": (37.5744, 43.7401),
    "Hatay": (36.2027, 36.1609),
    "Iğdır": (39.8883, 44.0048),
    "Isparta": (37.7648, 30.5561),
    "İstanbul": (41.0082, 28.9784),
    "İzmir": (38.4192, 27.1287),
    "Kahramanmaraş": (37.5764, 36.9378),
    "Karabük": (41.2061, 32.6214),
    "Karaman": (37.1811, 33.2150),
    "Kars": (40.6013, 43.0978),
    "Kastamonu": (41.3887, 33.7827),
    "Kayseri": (38.7312, 35.4787),
    "Kilis": (36.7167, 37.1167),
    "Kırıkkale": (39.8468, 33.5153),
    "Kırklareli": (41.7356, 27.2255),
    "Kırşehir": (39.1425, 34.1700),
    "Kocaeli": (40.8533, 29.8815),
    "Konya": (37.8716, 32.4840),
    "Kütahya": (39.4249, 29.9833),
    "Malatya": (38.3556, 38.3095),
    "Manisa": (38.6191, 27.4289),
    "Mardin": (37.3127, 40.7350),
    "Mersin": (36.7998, 34.6415),
    "Muğla": (37.2153, 28.3636),
    "Muş": (38.9461, 41.7536),
    "Nevşehir": (38.6240, 34.7123),
    "Niğde": (37.9667, 34.6833),
    "Ordu": (40.9860, 37.8797),
    "Osmaniye": (37.0742, 36.2454),
    "Rize": (41.0201, 40.5234),
    "Sakarya": (40.7767, 30.4036),
    "Samsun": (41.2867, 36.33),
    "Siirt": (37.9333, 41.95),
    "Sinop": (42.0222, 35.1556),
    "Sivas": (39.7483, 37.0150),
    "Şanlıurfa": (37.1674, 38.7950),
    "Şırnak": (37.4186, 42.4911),
    "Tekirdağ": (40.9833, 27.5167),
    "Tokat": (40.3167, 36.5556),
    "Trabzon": (41.0027, 39.7161),
    "Tunceli": (39.1081, 39.5535),
    "Uşak": (38.6824, 29.4082),
    "Van": (38.5019, 43.4167),
    "Yalova": (40.6500, 29.2667),
    "Yozgat": (39.8183, 34.8147),
    "Zonguldak": (41.4559, 31.7987),
}

def generate_random_earthquake():
    now = datetime.now(timezone(timedelta(hours=3))) 
    city = random.choice(list(city_coords.keys()))
    base_lat, base_lng = city_coords[city]

    lat = round(random.uniform(base_lat - 0.1, base_lat + 0.1), 4)
    lng = round(random.uniform(base_lng - 0.1, base_lng + 0.1), 4)

    return {
        "_id": str(uuid.uuid4()),
        "title": "Kandilli Rasathanesi Deprem Verisi",
        "date": now.strftime("%d.%m.%Y"),
        "date_time": now.isoformat() + "Z",
        "lat": lat,
        "lng": lng,
        "depth": round(random.uniform(1.0, 30.0), 1),
        "mag": round(random.uniform(2.0, 4.5), 1),
        "location_properties": {
            "closestCity": {
                "name": city,
                "distance": round(random.uniform(0, 50), 2)
            },
            "airports": [
                {
                    "name": "Havalimanı " + str(i),
                    "code": "AIR" + str(i),
                    "distance": round(random.uniform(5000, 100000), 2)
                } for i in range(random.randint(1, 3))
            ]
        },
        "geojson": {
            "coordinates": [lng, lat]
        }
    }

@app.route("/deprem/kandilli/live", methods=["GET"])
@swag_from({
    'tags': ['Earthquake'],
    'summary': 'Get 50 fake earthquake data',
    'responses': {
        200: {
            'description': 'List of earthquakes',
            'content': {
                'application/json': {
                    'example': {
                        "status": True,
                        "desc": "Fake earthquake data",
                        "result": [generate_random_earthquake() for _ in range(2)]
                    }
                }
            }
        }
    }
})
def get_fake_earthquakes():
    global earthquakes
    print(len(earthquakes))
    if len(earthquakes) < 50:
        earthquakes = [generate_random_earthquake() for _ in range(50)]
    return jsonify({
        "status": True,
        "desc": "Fake earthquake data",
        "result": earthquakes
    })

@app.route("/deprem/kandilli/add", methods=["POST"])
@swag_from({
    'tags': ['Earthquake'],
    'summary': 'Add a new fake earthquake data',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Manual Entry'},
                    'lat': {'type': 'number', 'example': 39.92},
                    'lng': {'type': 'number', 'example': 32.85},
                    'depth': {'type': 'number', 'example': 12.5},
                    'mag': {'type': 'number', 'example': 6.1},
                    'closest_city': {'type': 'string', 'example': 'Ankara'},
                    'distance_km': {'type': 'number', 'example': 3.2},
                    'airports': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string', 'example': 'Esenboğa'},
                                'code': {'type': 'string', 'example': 'ESB'},
                                'distance': {'type': 'number', 'example': 28000}
                            }
                        },
                        'example': [
                            {'name': 'Esenboğa', 'code': 'ESB', 'distance': 28000}
                        ]
                    }
                },
                'required': ['lat', 'lng', 'depth', 'mag']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Earthquake added successfully',
            'content': {
                'application/json': {
                    'example': {
                        "message": "Earthquake added",
                        "earthquake": {
                            "_id": "uuid",
                            "title": "Manual Entry",
                            "date": "23.05.2025",
                            "date_time": "2025-05-23T12:00:00Z",
                            "lat": 39.92,
                            "lng": 32.85,
                            "depth": 12.5,
                            "mag": 6.1,
                            "location_properties": {
                                "closestCity": {"name": "Ankara", "distance": 3.2},
                                "airports": [{"name": "Esenboğa", "code": "ESB", "distance": 28000}]
                            },
                            "geojson": {"coordinates": [32.85, 39.92]}
                        }
                    }
                }
            }
        }
    }
})
def add_fake_earthquake():
    global earthquakes
    data = request.json
    now = datetime.now(timezone(timedelta(hours=3)))  # Turkey is UTC+3

    new_eq = {
        "_id": str(uuid.uuid4()),
        "title": data.get("title", "Manual Entry"),
        "date": now.strftime("%d.%m.%Y"),
        "date_time": now.isoformat() + "Z",
        "lat": data["lat"],
        "lng": data["lng"],
        "depth": data["depth"],
        "mag": data["mag"],
        "location_properties": {
            "closestCity": {
                "name": data.get("closest_city", "Unknown"),
                "distance": data.get("distance_km", 0)
            },
            "airports": data.get("airports", [])
        },
        "geojson": {
            "coordinates": [data["lng"], data["lat"]]
        }
    }

    earthquakes.insert(0, new_eq)
    # earthquakes = earthquakes[:50]

    return jsonify({"message": "Earthquake added", "earthquake": new_eq}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=4000)
