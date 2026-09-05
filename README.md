# Seismic Risk MLOps

## Présentation du projet

Ce projet met en œuvre une chaîne MLOps complète appliquée à des données sismiques réelles provenant de l’USGS.

L’objectif est de construire une solution reproductible allant de la collecte et de la préparation des données jusqu’au déploiement d’une application permettant de classifier un événement sismique.

Le système ne prédit pas la date ni le lieu d’un futur séisme. Il classifie un événement sismique à partir de ses caractéristiques.

## Architecture

La chaîne MLOps utilisée dans ce projet est :

USGS API → Python / SQLite → Pandas → DVC / SeaweedFS → H2O AutoML → MLflow → FastAPI → Streamlit → Docker → GitHub Actions

### Technologies utilisées

- Python : traitement et préparation des données
- SQLite : stockage local des données
- Pandas : nettoyage et transformation
- DVC : versionnement des données et pipeline
- SeaweedFS : stockage des versions des données
- H2O AutoML : entraînement et comparaison des modèles
- MLflow : suivi des expériences et des métriques
- FastAPI : exposition du modèle via une API REST
- Streamlit : interface utilisateur
- Docker : conteneurisation de l’application
- Docker Compose : orchestration des services
- GitHub : versionnement du code et du modèle
- GitHub Actions : intégration continue

## Données

Les données utilisées proviennent de l’USGS.

- Événements téléchargés : 19 645
- Séismes conservés : 19 527
- Séismes forts : 1 360
- Proportion de la classe forte : 6,96 %

La cible du projet est définie comme suit :

- Séisme fort : magnitude >= 5,0
- Séisme non fort : magnitude < 5,0

La magnitude n’est pas utilisée comme variable prédictive afin d’éviter une fuite de cible.

Le dataset final utilisé pour le Machine Learning contient 19 527 lignes et 8 colonnes.

## Préparation et versionnement des données

Pandas est utilisé pour nettoyer les données, filtrer les événements sismiques et créer les variables nécessaires au Machine Learning.

DVC décrit les principales étapes du pipeline, notamment :

- prepare
- build_features

SeaweedFS est utilisé pour stocker physiquement les différentes versions des données à travers une interface compatible S3.

Git conserve le code source ainsi que les fichiers de configuration et les métadonnées DVC.

## Machine Learning

L’entraînement est réalisé avec H2O AutoML.

Configuration principale :

- Maximum de 10 modèles
- Seed = 42
- Équilibrage des classes activé
- Comparaison automatique de plusieurs algorithmes

Comme la classe des séismes forts représente seulement 6,96 % des observations, le classement des modèles utilise principalement AUCPR.

Le modèle sélectionné est un :

Stacked Ensemble

### Résultats du modèle

- AUC : 0,8201
- AUCPR : 0,2171
- RMSE : 0,2405
- Seuil de décision : 11,92 %

L’évaluation ne repose donc pas uniquement sur l’accuracy, car les classes sont fortement déséquilibrées.

## MLflow

MLflow est utilisé pour suivre les expériences de Machine Learning.

Il permet notamment de conserver :

- les paramètres
- les métriques
- le leaderboard
- les informations sur les expériences
- les artefacts associés au modèle

## API FastAPI

FastAPI charge le modèle H2O sélectionné et expose un endpoint de prédiction :

/predict

L’API reçoit les caractéristiques d’un événement sismique, exécute le modèle H2O et retourne les probabilités ainsi que la classification finale.

Documentation interactive de l’API :

http://localhost:8001/docs

## Dashboard Streamlit

Streamlit fournit une interface permettant de saisir les caractéristiques d’un événement sismique.

Le dashboard communique avec l’API FastAPI à l’intérieur du réseau Docker.

Adresse utilisée entre les conteneurs :

http://seismic-risk-api:8001/predict

Le résultat affiche notamment :

- la probabilité de séisme fort
- la probabilité de séisme non fort
- le seuil de décision
- la classification finale

## Docker

FastAPI et Streamlit sont exécutés dans des conteneurs Docker séparés.

Docker Compose construit, démarre et connecte les services de l’application.

Le conteneur FastAPI contient également :

- Python
- Java
- H2O
- le modèle H2O Stacked Ensemble entraîné

Le modèle entraîné est inclus dans le dépôt GitHub et est automatiquement copié dans l’image Docker de l’API lors du build.

## Exécuter le projet sur une nouvelle machine

### Prérequis

Seulement deux outils sont nécessaires :

- Git
- Docker Desktop

Il n’est pas nécessaire d’installer séparément :

- Python
- Java
- H2O
- FastAPI
- Streamlit

Docker installe et configure les dépendances nécessaires dans les conteneurs.

### Étape 1 — Cloner le dépôt

Ouvrir PowerShell et exécuter :

git clone https://github.com/tarekalsemaan/SeismicRiskMLOps.git

### Étape 2 — Entrer dans le projet

cd SeismicRiskMLOps

### Étape 3 — Construire et démarrer l’application

docker compose up --build

Docker construit les images et démarre automatiquement :

- le serveur H2O
- l’API FastAPI
- le dashboard Streamlit
- le modèle Stacked Ensemble

### Étape 4 — Ouvrir le dashboard

Dans un navigateur :

http://localhost:8502

### Étape 5 — Tester l’API

La documentation FastAPI est disponible à :

http://localhost:8001/docs

### Étape 6 — Effectuer une prédiction

Dans le dashboard Streamlit :

1. Saisir les caractéristiques de l’événement sismique.
2. Cliquer sur Predict.
3. Observer les probabilités.
4. Comparer la probabilité de la classe forte avec le seuil de décision.
5. Observer la classification finale.

## Validation sur une nouvelle installation

La reproductibilité du projet a été vérifiée à partir d’un nouveau clone du dépôt GitHub dans un dossier séparé.

Le test complet suivant a été réalisé avec succès :

GitHub clone
→ Docker build
→ démarrage H2O
→ chargement du modèle
→ démarrage FastAPI
→ démarrage Streamlit
→ appel /predict
→ résultat de prédiction

L’API a retourné :

POST /predict HTTP/1.1 200 OK

Cela confirme que le dashboard communique correctement avec FastAPI et que l’API exécute le modèle H2O.

### Exemple de résultat obtenu

Lors du test :

- Probabilité de séisme fort : 18,86 %
- Probabilité de séisme non fort : 81,14 %
- Seuil de décision : 11,92 %

Comme 18,86 % est supérieur au seuil de 11,92 %, la classification retournée est :

Séisme fort

## GitHub Actions

GitHub Actions assure l’intégration continue du projet.

Le pipeline CI s’exécute automatiquement lors des opérations configurées dans le dépôt.

Il permet notamment de :

- vérifier le code Python
- valider la construction des images Docker

La version contenant le modèle H2O entraîné a également été validée avec succès par le pipeline GitHub Actions.

## Arrêter l’application

Dans la fenêtre où Docker Compose est exécuté :

Ctrl+C

Pour supprimer les conteneurs et le réseau créés par Docker Compose :

docker compose down

## Limites

Ce projet est une démonstration pédagogique de Machine Learning et de MLOps.

Le modèle classifie des événements sismiques enregistrés.

Il ne prédit pas :

- quand un futur séisme aura lieu
- où un futur séisme aura lieu

## Perspectives

Plusieurs améliorations peuvent être envisagées :

- enrichir les données géologiques
- utiliser une période historique plus longue
- améliorer les variables prédictives
- comparer davantage de modèles
- déployer l’application dans le cloud

## Code source

GitHub :

https://github.com/tarekalsemaan/SeismicRiskMLOps