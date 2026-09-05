from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import h2o

MODEL_PATH = "models/StackedEnsemble_AllModels_1_AutoML_1_20260904_204429"

FEATURES = [
    "latitude",
    "longitude",
    "depth",
    "month",
    "day",
    "hour",
    "day_of_week"
]

DECISION_THRESHOLD = 0.11923830048383477

app = FastAPI(
    title="Seismic Risk API",
    version="1.1.0"
)

h2o.init()
model = h2o.load_model(MODEL_PATH)


class EarthquakeInput(BaseModel):
    latitude: float
    longitude: float
    depth: float
    month: int
    day: int
    hour: int
    day_of_week: int


@app.get("/")
def root():
    return {
        "message": "Seismic Risk API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": model.model_id,
        "decision_threshold": DECISION_THRESHOLD
    }


@app.post("/predict")
def predict(data: EarthquakeInput):

    row = pd.DataFrame([[
        data.latitude,
        data.longitude,
        data.depth,
        data.month,
        data.day,
        data.hour,
        data.day_of_week
    ]], columns=FEATURES)

    input_data = h2o.H2OFrame(row)

    prediction = model.predict(input_data).as_data_frame()

    probability_strong = float(prediction.iloc[0]["p1"])
    probability_not_strong = float(prediction.iloc[0]["p0"])

    predicted_class = 1 if probability_strong >= DECISION_THRESHOLD else 0

    return {
        "predicted_class": predicted_class,
        "strong_earthquake": predicted_class == 1,
        "probability_strong": probability_strong,
        "probability_not_strong": probability_not_strong,
        "decision_threshold": DECISION_THRESHOLD,
        "decision_threshold_percent": DECISION_THRESHOLD * 100
    }
