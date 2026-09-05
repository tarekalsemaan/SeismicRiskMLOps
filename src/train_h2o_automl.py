import os
import h2o
import mlflow
from h2o.automl import H2OAutoML

DATA_FILE = "data/usgs_ml_ready_2026.csv"
TARGET = "strong_earthquake"

FEATURES = [
    "latitude",
    "longitude",
    "depth",
    "month",
    "day",
    "hour",
    "day_of_week"
]

mlflow.set_tracking_uri("http://127.0.0.1:5001")
mlflow.set_experiment("Seismic-Risk-H2O")

h2o.init()

df = h2o.import_file(DATA_FILE)
df[TARGET] = df[TARGET].asfactor()

train, test = df.split_frame(
    ratios=[0.8],
    seed=42
)

with mlflow.start_run(run_name="H2O_AutoML_Seismic"):

    mlflow.log_param("max_models", 10)
    mlflow.log_param("seed", 42)
    mlflow.log_param("balance_classes", True)
    mlflow.log_param("target", TARGET)
    mlflow.log_param("features", ",".join(FEATURES))

    aml = H2OAutoML(
        max_models=10,
        seed=42,
        balance_classes=True,
        sort_metric="AUCPR"
    )

    print("Starting H2O AutoML...")

    aml.train(
        x=FEATURES,
        y=TARGET,
        training_frame=train
    )

    leader = aml.leader
    performance = leader.model_performance(test)

    auc = performance.auc()
    aucpr = performance.aucpr()
    rmse = performance.rmse()
    logloss = performance.logloss()

    print("\nBest model:", leader.model_id)
    print("AUC:", auc)
    print("AUCPR:", aucpr)
    print("RMSE:", rmse)
    print("LogLoss:", logloss)

    mlflow.log_metric("auc", auc)
    mlflow.log_metric("aucpr", aucpr)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("logloss", logloss)

    mlflow.set_tag("best_model", leader.model_id)
    mlflow.set_tag("framework", "H2O AutoML")

    os.makedirs("models", exist_ok=True)

    model_path = h2o.save_model(
        model=leader,
        path="models",
        force=True
    )

    mlflow.log_artifact(
        model_path,
        artifact_path="h2o_model"
    )

    leaderboard_path = "models/leaderboard.csv"

    aml.leaderboard.as_data_frame().to_csv(
        leaderboard_path,
        index=False
    )

    mlflow.log_artifact(
        leaderboard_path,
        artifact_path="leaderboard"
    )

print("\nMLflow run completed.")

h2o.cluster().shutdown()
