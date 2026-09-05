# Seismic Risk MLOps

## Project Overview
Short description of the project and objective.

## Architecture
USGS API | Python | SQLite | DVC | SeaweedFS |
H2O AutoML | MLflow | FastAPI | Streamlit |
Docker | GitHub Actions

## Dataset
19,527 earthquakes
Target: magnitude >= 5
Strong events: 6.96%

## Machine Learning
H2O AutoML
AUC: 0.8201
AUCPR: 0.2171
Selected model: Stacked Ensemble

## MLOps Components
DVC: data versioning
SeaweedFS: data storage
MLflow: experiment tracking
FastAPI: model serving
Streamlit: dashboard
Docker: containers
GitHub Actions: CI

## Run the Project
dvc repro
docker compose up -d

Dashboard: localhost:8502
API: localhost:8001

## Limitation
The model classifies recorded seismic events.
It does not predict the time or location of future earthquakes.