import pandas as pd
import numpy as np
from typing import Dict, Optional, Union
import json
import joblib

try:
    trained_lgbm_mag_pipe = joblib.load("models/lgbm_mag_pipeline.pkl")
    trained_lgbm_time_pipe = joblib.load("models/lgbm_time_pipeline.pkl")
except FileNotFoundError:
    print("Model dosyaları bulunamadı.")
    trained_lgbm_mag_pipe = None
    trained_lgbm_time_pipe = None


def predict_aftershock(
    mainshock_magnitude: float,
    mainshock_depth: float,
    mainshock_latitude: float,
    mainshock_longitude: float,
    return_format: str = "dict",
) -> Union[Dict, str]:
    try:

        if trained_lgbm_mag_pipe is None or trained_lgbm_time_pipe is None:
            error_result = {
                "success": False,
                "error": "Models are not trained yet. Please train the models first.",
                "error_code": "MODEL_NOT_TRAINED",
            }
            return (
                json.dumps(error_result, indent=2)
                if return_format == "json"
                else error_result
            )

        if not all(
            isinstance(val, (int, float))
            for val in [
                mainshock_magnitude,
                mainshock_depth,
                mainshock_latitude,
                mainshock_longitude,
            ]
        ):
            error_result = {
                "success": False,
                "error": "All input parameters must be numeric values.",
                "error_code": "INVALID_INPUT_TYPE",
            }
            return (
                json.dumps(error_result, indent=2)
                if return_format == "json"
                else error_result
            )

        if not (0 <= mainshock_magnitude <= 10):
            error_result = {
                "success": False,
                "error": "Magnitude must be between 0 and 10.",
                "error_code": "INVALID_MAGNITUDE",
            }
            return (
                json.dumps(error_result, indent=2)
                if return_format == "json"
                else error_result
            )

        if not (0 <= mainshock_depth <= 1000):
            error_result = {
                "success": False,
                "error": "Depth must be between 0 and 1000 km.",
                "error_code": "INVALID_DEPTH",
            }
            return (
                json.dumps(error_result, indent=2)
                if return_format == "json"
                else error_result
            )

        if not (-90 <= mainshock_latitude <= 90):
            error_result = {
                "success": False,
                "error": "Latitude must be between -90 and 90 degrees.",
                "error_code": "INVALID_LATITUDE",
            }
            return (
                json.dumps(error_result, indent=2)
                if return_format == "json"
                else error_result
            )

        if not (-180 <= mainshock_longitude <= 180):
            error_result = {
                "success": False,
                "error": "Longitude must be between -180 and 180 degrees.",
                "error_code": "INVALID_LONGITUDE",
            }
            return (
                json.dumps(error_result, indent=2)
                if return_format == "json"
                else error_result
            )

        input_features_df = pd.DataFrame(
            [
                [
                    mainshock_magnitude,
                    mainshock_depth,
                    mainshock_latitude,
                    mainshock_longitude,
                ]
            ],
            columns=[
                "mainshock_mag",
                "mainshock_depth",
                "mainshock_lat",
                "mainshock_lon",
            ],
        )

        predicted_magnitude = trained_lgbm_mag_pipe.predict(input_features_df)[0]

        predicted_time_log = trained_lgbm_time_pipe.predict(input_features_df)[0]

        predicted_time_hours = np.expm1(predicted_time_log)
        predicted_time_hours = max(0, predicted_time_hours)

        predicted_time_minutes = predicted_time_hours * 60

        result = {
            "success": True,
            "input": {
                "mainshock_magnitude": mainshock_magnitude,
                "mainshock_depth_km": mainshock_depth,
                "mainshock_latitude": mainshock_latitude,
                "mainshock_longitude": mainshock_longitude,
            },
            "predictions": {
                "aftershock_magnitude": {
                    "value": round(predicted_magnitude, 2),
                },
                "time_to_aftershock": {
                    "minutes": round(predicted_time_minutes, 1),
                },
            },
            "model_info": {
                "algorithm": "LightGBM",
                "prediction_type": "Regression",
            },
            "warnings": [],
        }

        if predicted_magnitude > mainshock_magnitude:
            result["warnings"].append(
                "Predicted aftershock magnitude is higher than mainshock - this is unusual"
            )

        if predicted_time_hours > 24 * 30:
            result["warnings"].append("Predicted time is unusually long (>30 days)")

        if predicted_time_hours < 0.1:
            result["warnings"].append("Predicted time is very short (<6 minutes)")

        if return_format == "json":
            return json.dumps(result, indent=2)
        else:
            return result

    except Exception as e:
        error_result = {
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}",
            "error_code": "PREDICTION_ERROR",
        }
        return (
            json.dumps(error_result, indent=2)
            if return_format == "json"
            else error_result
        )


def batch_predict_aftershocks(
    earthquake_data: list, return_format: str = "dict"
) -> Union[Dict, str]:
    try:
        if not isinstance(earthquake_data, list):
            error_result = {
                "success": False,
                "error": "earthquake_data must be a list of dictionaries",
                "error_code": "INVALID_INPUT_FORMAT",
            }
            return (
                json.dumps(error_result, indent=2)
                if return_format == "json"
                else error_result
            )

        results = {
            "success": True,
            "total_predictions": len(earthquake_data),
            "predictions": [],
        }

        for i, eq_data in enumerate(earthquake_data):
            if not isinstance(eq_data, dict):
                results["predictions"].append(
                    {
                        "index": i,
                        "success": False,
                        "error": "Each earthquake must be a dictionary",
                    }
                )
                continue

            required_fields = ["magnitude", "depth", "latitude", "longitude"]
            if not all(field in eq_data for field in required_fields):
                results["predictions"].append(
                    {
                        "index": i,
                        "success": False,
                        "error": f"Missing required fields. Required: {required_fields}",
                    }
                )
                continue

            prediction = predict_aftershock(
                eq_data["magnitude"],
                eq_data["depth"],
                eq_data["latitude"],
                eq_data["longitude"],
                return_format="dict",
            )

            if "id" in eq_data:
                prediction["earthquake_id"] = eq_data["id"]

            prediction["index"] = i
            results["predictions"].append(prediction)

        if return_format == "json":
            return json.dumps(results, indent=2)
        else:
            return results

    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Batch prediction failed: {str(e)}",
            "error_code": "BATCH_PREDICTION_ERROR",
        }
        return (
            json.dumps(error_result, indent=2)
            if return_format == "json"
            else error_result
        )


def check_model_status() -> Dict:
    return {
        "magnitude_model_trained": trained_lgbm_mag_pipe is not None,
        "time_model_trained": trained_lgbm_time_pipe is not None,
        "both_models_ready": (
            trained_lgbm_mag_pipe is not None and trained_lgbm_time_pipe is not None
        ),
        "model_type": "LightGBM" if trained_lgbm_mag_pipe is not None else None,
    }

def format_eq(eq, prediction_result: Optional[Dict] = None) -> Dict:
    return {
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
                "distance_km": round(ap["distance"] / 1000, 1)
            } for ap in eq["location_properties"].get("airports", [])
        ],
        "prediction": prediction_result
    }
