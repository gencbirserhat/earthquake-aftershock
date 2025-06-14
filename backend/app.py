from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
from flask import Flask
from flask_socketio import SocketIO, emit
import requests
import threading
import time
from main import check_model_status, format_eq, predict_aftershock
import firebase_admin
from firebase_admin import credentials, messaging

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

cred = credentials.Certificate(
    "earthquake-aftershock-firebase-adminsdk-fbsvc-703a825086.json"
)
firebase_admin.initialize_app(cred)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Aftershock Prediction API",
        "description": "Deprem sonrası artçı şok tahmin servisi",
        "version": "1.0",
    },
}

swagger = Swagger(app, template=swagger_template)

API_URL = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
FAKE_API_URL = "http://127.0.0.1:4000/deprem/kandilli/live"
initial_data = []
last_eq_id = None
initial_data_sent = False  
fcm_tokens = []
recent_predictions = []  


def send_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body), token=token
    )

    response = messaging.send(message)
    print("Successfully sent message:", response)


def fetch_and_emit_earthquakes():
    global last_eq_id, initial_data_sent, initial_data, fcm_tokens, recent_predictions
    while True:
        try:
            
            response = requests.get(FAKE_API_URL)
            data = response.json()

            if data["status"] and data["result"]:
                earthquakes = data["result"]

                if not initial_data_sent:
                    initial_data_sent = True
                    initial_data = [
                        {
                            "id": eq["_id"],
                            "title": eq["title"],
                            "date": eq["date"],
                            "datetime": eq["date_time"],
                            "magnitude": eq["mag"],
                            "depth": eq["depth"],
                            "coordinates": eq["geojson"]["coordinates"],
                            "closest_city": eq["location_properties"]["closestCity"]["name"],
                            "airports": [
                                {
                                    "name": ap["name"],
                                    "code": ap["code"],
                                    "distance_km": round(ap["distance"] / 1000, 1),
                                }
                                for ap in eq["location_properties"].get("airports", [])
                            ],
                        }
                        for eq in earthquakes[:50]
                    ]
                    print("Initial 20 data cached")

                
                latest_eq = earthquakes[0]
                print("Latest earthquake ID:", latest_eq["_id"])
                print("Last earthquake ID:", last_eq_id)
                if latest_eq["_id"] != last_eq_id or last_eq_id is None:
                    last_eq_id = latest_eq["_id"]
                    
                    formatted_eq = {
                        "id": latest_eq["_id"],
                        "title": latest_eq["title"],
                        "date": latest_eq["date"],
                        "datetime": latest_eq["date_time"],
                        "magnitude": latest_eq["mag"],
                        "depth": latest_eq["depth"],
                        "coordinates": latest_eq["geojson"]["coordinates"],
                        "closest_city": latest_eq["location_properties"]["closestCity"]["name"],
                        "airports": [
                            {
                                "name": ap["name"],
                                "code": ap["code"],
                                "distance_km": round(ap["distance"] / 1000, 1),
                            }
                            for ap in latest_eq["location_properties"].get("airports", [])
                        ],
                    }
                    
                    initial_data.insert(0, formatted_eq)
                    
                    if len(initial_data) > 50:
                        initial_data = initial_data[:50]

                    prediction_result = None
                    
                    if latest_eq["mag"] >= 5.5:
                        prediction_result = predict_aftershock(
                            latest_eq["mag"],
                            latest_eq["depth"],
                            latest_eq["geojson"]["coordinates"][1],  
                            latest_eq["geojson"]["coordinates"][0],  
                            return_format="dict",
                        )
                        
                        prediction_result["id"] = latest_eq["_id"]
                        prediction_result["timestamp"] = latest_eq["date_time"]
                        aftermagnitude = prediction_result["predictions"]["aftershock_magnitude"]["value"]

                        
                        recent_predictions.insert(0, prediction_result)
                        if len(recent_predictions) > 50:
                            recent_predictions = recent_predictions[:50]

                        socketio.emit("prediction_result", prediction_result)
                        for token in fcm_tokens:
                            send_notification(
                                token,
                                "Deprem Uyarısı",
                                f"{formatted_eq['closest_city']} bölgesinde {formatted_eq['magnitude']} şiddetinde deprem!\n\nBeklenen ilk artçı şok şiddeti: {aftermagnitude}",
                            )
                    print(
                        "Emitting new earthquake:",
                        format_eq(latest_eq, prediction_result),
                    )
                    socketio.emit(
                        "earthquake_update", format_eq(latest_eq, prediction_result)
                    )
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(15)


@socketio.on("connect")
def on_connect():
    print("New client connected")
    if initial_data:
        emit("initial_earthquakes", initial_data)
    if recent_predictions:
        emit("initial_predictions", recent_predictions)


@app.route("/ws")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aftershock Prediction</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
    document.addEventListener('DOMContentLoaded', function() {
        var socket = io();
        const container = document.getElementById('earthquake-data');

    socket.on('initial_earthquakes', function(dataList) {
    console.log("Initial earthquakes:", dataList); // burada boş mu?
    });
        // İlk 20 deprem
        socket.on('initial_earthquakes', function(dataList) {
            container.innerHTML = '<h2>Recent Earthquakes</h2>';
            dataList.forEach(function(data) {
                container.innerHTML += renderEarthquake(data);
            });
        });

        // Yeni deprem geldikçe en üste ekle
        socket.on('earthquake_update', function(data) {
            container.innerHTML = renderEarthquake(data) + container.innerHTML;
        });


        function renderEarthquake(data) {
            return `
                <div style="border-bottom:1px solid 
                    <h3>${data.title}</h3>
                    <p><strong>Magnitude:</strong> ${data.magnitude}</p>
                    <p><strong>Depth:</strong> ${data.depth} km</p>
                    <p><strong>Location:</strong> ${data.closest_city}</p>
                    <p><strong>Date:</strong> ${data.datetime}</p>
                </div>
            `;
        }
    });
</script>
    </head>
    <body>
        <h1>Earthquake Live Updates</h1>
        <div id="earthquake-data">Waiting for earthquake data...</div>
        <hr>
        <h2>API Documentation</h2>
        <p>Visit <a href="/apidocs">/apidocs</a> for the Swagger API documentation</p>
    </body>
    </html>
    """



earthquake_thread = threading.Thread(target=fetch_and_emit_earthquakes, daemon=True)
earthquake_thread.start()


@app.route("/register-token", methods=["POST"])
def register_token():
    global fcm_tokens
    data = request.get_json()
    token = data.get("token")
    if token and token not in fcm_tokens:
        fcm_tokens.append(token)
        print("Yeni FCM token kaydedildi:", token)
    return {"status": "ok"}, 200


@app.route("/predict", methods=["POST"])
@swag_from(
    {
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "magnitude": {"type": "number"},
                        "depth": {"type": "number"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                    },
                    "required": ["magnitude", "depth", "latitude", "longitude"],
                },
            }
        ],
        "responses": {
            200: {
                "description": "Aftershock prediction",
                "examples": {
                    "application/json": {
                        "aftershock_probability": 0.76,
                        "expected_count": 3,
                    }
                },
            }
        },
    }
)
def api_predict():
    data = request.json
    result = predict_aftershock(
        data["magnitude"],
        data["depth"],
        data["latitude"],
        data["longitude"],
        return_format="dict",
    )
    return jsonify(result)


""" @app.route("/batch_predict", methods=["POST"])
@swag_from(
    {
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "earthquakes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "magnitude": {"type": "number"},
                                    "depth": {"type": "number"},
                                    "latitude": {"type": "number"},
                                    "longitude": {"type": "number"},
                                },
                                "required": [
                                    "magnitude",
                                    "depth",
                                    "latitude",
                                    "longitude",
                                ],
                            },
                        }
                    },
                    "required": ["earthquakes"],
                },
            }
        ],
        "responses": {200: {"description": "Batch aftershock predictions"}},
    }
) """


""" def api_batch_predict():
    data = request.json
    result = batch_predict_aftershocks(data["earthquakes"], return_format="dict")
    return jsonify(result) """


@app.route("/status", methods=["GET"])
@swag_from(
    {
        "responses": {
            200: {
                "description": "Model status",
                "examples": {"application/json": {"status": "ready"}},
            }
        }
    }
)
def api_status():
    return jsonify(check_model_status())


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
