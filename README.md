# Guide d'installation et de configuration

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation de l'environnement](#installation-de-lenvironnement)
3. [Configuration des services](#configuration-des-services)
4. [Configuration de l'application](#configuration-de-lapplication)
5. [Lancement de l'application](#lancement-de-lapplication)


---

## Prérequis

### Logiciels

- **Python** : Version 3.10 ou supérieure
- **Docker** : Version 20.x ou supérieure
- **Docker Compose** : Version 2.x ou supérieure
- **uv** 



### Clés API

- **OpenAI API Key** 
- **LangSmith API Key** (optionnel, pour le traçage)


## Installation de l'environnement

### 1. Cloner le repository

```bash
git clone https://github.com/cleophass/test_technique.git
cd test_technique
```

### 2. Créer l'environnement Python

#### Avec uv 

```bash
uv sync
```


### Vérifier l'installation des dépendances

```bash
# Avec uv
uv pip list

# Avec pip
pip list
```

---

## Configuration des services

### Lancer Elasticsearch et Kibana avec Docker

```bash
docker-compose up -d
```

### Vérifier que les services sont opérationnels

```bash
docker ps

# Vous devriez voir 2 conteneurs en cours d'exécution :
# - elasticsearch (port 9200)
# - kibana (port 5601)
```

### Tester la connexion à Elasticsearch

```bash
# Test de connexion
curl http://localhost:9200

# Réponse attendue : JSON avec les informations du cluster
# Si vous voyez une erreur, attendez quelques instants que Elasticsearch démarre complètement et réessayez.
```

### Accéder à Kibana (optionnel, pour monitoring)

Ouvrir dans un navigateur : [http://localhost:5601](http://localhost:5601)

---

## Configuration de l'application

### 1. Créer le fichier `.env`

À la racine du projet, créer un fichier `.env` :

```bash
touch .env
```

### 2. Ajouter la clé OpenAI

Éditer le fichier `.env` et ajouter :

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
### 3. Configurer LangSmith (optionnel)
Si vous souhaitez utiliser LangSmith pour le traçage, ajoutez également :

```env
LANGSMITH_API_KEY=lsv2_pt_....
LANGSMITH_TRACING=true
```
Pour accéder a "traces" dans LangSmith, vous pouvez utiliser ce lien : https://smith.langchain.com/

### 3. Vérifier la configuration dans `core/config.py`

Le fichier `core/config.py` contient les paramètres des modèles :

```python
EMBEDDINGS_MODEL_NAME="paraphrase-multilingual-mpnet-base-v2"
REWRITER_MODEL_NAME="gpt-4.1"
GUARDRAILS_MODEL_NAME="gpt-4.1"
HYDE_MODEL_NAME="gpt-4.1"
GENERATOR_MODEL_NAME="gpt-4.1"
TITLE_MODEL_NAME="gpt-4.1"
RERANKER_MODEL_NAME="antoinelouis/crossencoder-camembert-base-mmarcoFR"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DOCUMENTS_INDEX_NAME="documents_index"
HISTORY_INDEX_NAME="history_index"
MESSAGE_INDEX_NAME="message_index"
LOGGER_INDEX_NAME="logger_index"
```

Ces paramètres peuvent être modifiés selon vos besoins.

---

## Lancement de l'application

### Méthode 1 : Avec le script `run.sh` (recommandé)

```bash
# Rendre le script exécutable
chmod +x run.sh

# Lancer l'application
./run.sh
```

Le script effectue automatiquement :
1. Démarrage des conteneurs Docker (Elasticsearch + Kibana)
2. Lancement de l'application Streamlit
PS: Le premier lancement peut prendre quelques minutes. 

### ⚠️ **Si rien ne s'affiche sur streamlit pensez à rafraîchir la page** ⚠️


### 3. Accéder à l'application

L'application sera disponible à l'adresse : [http://localhost:8501](http://localhost:8501)

### 4. Ajouter des documents
Pour ajouter des documents, aller dans la page "Documents" de l'application Streamlit et utiliser l'interface d'upload. Les formats supportés sont : `.txt`, `.csv`, `.html`.
Le dossier "data/raw/" contient déjà des fichier, au premier lancement de streamlit les documents seront indexés automatiquement.



