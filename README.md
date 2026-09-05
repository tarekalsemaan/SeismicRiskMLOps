# Risque sismique — MLOps

## Présentation du projet

Ce projet met en œuvre une chaîne MLOps complète appliquée à des données sismiques réelles provenant de l’USGS.

L’objectif est de construire une solution reproductible allant de la collecte et de la préparation des données jusqu’au déploiement d’une application permettant de classifier un événement sismique.

Le système ne prédit pas la date ni le lieu d’un futur séisme. Il classifie un scénario sismique à partir de ses caractéristiques.

## Exécuter le projet

### Prérequis

Seulement deux outils sont nécessaires :

- Git
- Docker Desktop

Ouvrir PowerShell et exécuter :

```powershell
git clone https://github.com/tarekalsemaan/SeismicRiskMLOps.git
cd SeismicRiskMLOps
docker compose up --build
```

Une fois l’application démarrée, ouvrir :

```text
http://localhost:8502
```

La documentation FastAPI est disponible à :

```text
http://localhost:8001/docs
```

Il n’est pas nécessaire d’installer séparément Python, Java, H2O, FastAPI ou Streamlit. Docker installe les dépendances nécessaires dans les conteneurs.

## Effectuer une prédiction

Dans le dashboard :

1. Choisir la date.
2. Choisir l’heure UTC.
3. Cliquer directement sur un endroit de la carte mondiale.
4. La latitude et la longitude sont récupérées automatiquement.
5. La prédiction est lancée automatiquement.
6. Le résultat est affiché sous la carte et dans le marqueur.

Le résultat indique :

- la probabilité de séisme fort
- la probabilité de séisme non fort
- le seuil de décision
- la classification finale

La carte affiche également les limites tectoniques mondiales.

La profondeur n’est pas demandée à l’utilisateur. Une valeur interne de 20 km est utilisée afin de rester compatible avec le modèle entraîné.

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
- Folium : carte interactive
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

SeaweedFS est utilisé pour stocker les différentes versions des données à travers une interface compatible S3.

Git conserve le code source, les fichiers de configuration et les métadonnées DVC.

## Machine Learning

L’entraînement est réalisé avec H2O AutoML.

Configuration principale :

- Maximum de 10 modèles
- Seed = 42
- Équilibrage des classes activé
- Comparaison automatique de plusieurs algorithmes

Comme la classe des séismes forts représente seulement 6,96 % des observations, le classement des modèles utilise principalement AUCPR.

Le modèle sélectionné est un **Stacked Ensemble**.

### Résultats du modèle

- AUC : 0,8201
- AUCPR : 0,2171
- RMSE : 0,2405
- Seuil de décision : 11,92 %

L’évaluation ne repose pas uniquement sur l’accuracy, car les classes sont fortement déséquilibrées.

## MLflow

MLflow est utilisé pour suivre les expériences de Machine Learning.

Il permet notamment de conserver :

- les paramètres
- les métriques
- le leaderboard
- les informations sur les expériences
- les artefacts associés au modèle

## API FastAPI

FastAPI charge le modèle H2O sélectionné et expose l’endpoint :

```text
/predict
```

L’API reçoit les caractéristiques du scénario, exécute le modèle H2O et retourne les probabilités ainsi que la classification finale.

Documentation interactive :

```text
http://localhost:8001/docs
```

## Dashboard Streamlit

Streamlit fournit l’interface graphique de l’application.

L’utilisateur choisit une date et une heure puis clique directement sur la carte. Le dashboard récupère les coordonnées et appelle automatiquement FastAPI.

À l’intérieur du réseau Docker, Streamlit communique avec l’API à l’adresse :

```text
http://api:8001/predict
```

Le résultat reste affiché après la prédiction et un marqueur est ajouté sur la carte.

## Docker

FastAPI et Streamlit sont exécutés dans des conteneurs Docker séparés.

Docker Compose construit, démarre et connecte les services de l’application.

Le conteneur FastAPI contient également :

- Python
- Java
- H2O
- le modèle H2O Stacked Ensemble entraîné

Le modèle entraîné est inclus dans le dépôt GitHub et est automatiquement copié dans l’image Docker de l’API lors du build.

## Validation sur une nouvelle installation

La reproductibilité du projet a été vérifiée à partir d’un nouveau clone du dépôt GitHub dans un dossier séparé.

Le test complet a été réalisé avec succès :

GitHub clone  
→ Docker build  
→ H2O  
→ chargement du modèle  
→ FastAPI  
→ Streamlit  
→ carte interactive  
→ prédiction

L’API a retourné :

```text
POST /predict HTTP/1.1 200 OK
```

La carte, les limites tectoniques, la sélection d’une position, la prédiction automatique et l’affichage du résultat ont également été testés avec succès.

### Exemple de résultat

Lors d’un test :

- Probabilité de séisme fort : 18,86 %
- Probabilité de séisme non fort : 81,14 %
- Seuil de décision : 11,92 %

Comme 18,86 % est supérieur au seuil de 11,92 %, la classification retournée est :

**Séisme fort**

## GitHub Actions

GitHub Actions assure l’intégration continue du projet.

Le pipeline CI permet notamment de :

- vérifier le code Python
- valider la construction des images Docker

## Arrêter l’application

Dans la fenêtre où Docker Compose est exécuté :

```text
Ctrl+C
```

Puis :

```powershell
docker compose down
```

## Limites

Ce projet est une démonstration pédagogique de Machine Learning et de MLOps.

Le modèle ne prédit pas :

- quand un futur séisme aura lieu
- où un futur séisme aura lieu

Le point choisi sur la carte représente simplement un scénario soumis au modèle.

## Perspectives

Plusieurs améliorations peuvent être envisagées :

- enrichir les données géologiques
- utiliser une période historique plus longue
- améliorer les variables prédictives
- comparer davantage de modèles
- améliorer la gestion de la profondeur
- déployer l’application dans le cloud

## Code source

GitHub :

https://github.com/tarekalsemaan/SeismicRiskMLOps