# Besoins et fonctionnalités

| Périmètre | Besoin | Solution / Piste | Status |
|-----------|--------|------------------|--------|
| **Général** | API sécurisée | Utiliser un .env pour stocker les clés d'API | ✅ Fait |
| **Architecture** | 2 pages (Doc Management & Chat) | Gestion des pages avec Streamlit (page manager) | ✅ Fait |
| | RAG System | Pipeline RAG complet avec base vectorielle (Elasticsearch) | ✅ Fait |
| | Design modulaire | Séparer les modules en classes : preprocessing, vectorisation, retrieval, agents | ✅ Fait |
| **Page 1 -- Chatbot** | Chat input/output | Interface type ChatGPT : question ↔ réponse | ✅ Fait |
| | Réponse basée exclusivement sur les documents internes | Vérification stricte des réponses issues uniquement des documents vectorisés | |
| | Gestion de conversation | Bouton reset permettant de réinitialiser le chat et la mémoire de l'agent | ✅ Fait |
| | Historique de conversation | Gérer avec Elasticsearch | |
| | Montrer les sources utilisées | Afficher la ou les sources à l'origine de la réponse | ✅ Fait |
| **Page 2 -- Gestion des documents** | Upload de documents | Accepter .csv, .txt, .html → lancer automatiquement la pipeline d'indexation | ✅ Fait |
| | Suppression de documents | Voir les documents existants + suppression locale et BDD + réindexation | ✅ Fait |
| **Partie Offline** | Préprocessing | Nettoyage du texte (HTML, ponctuation, espaces...) | ✅ Fait |
| | Chunking | Chunk si document > 300 tokens | |
| | Vectorisation | Génération des embeddings | ✅ Fait |
| | Stockage | Index vectoriel local ou BDD | ✅ Fait |
| **Partie Online** | Accès au modèle | Agent OpenAI via LangChain | ✅ Fait |
| | Flow (guardrails, HyDE, etc.) | Utilisation d'agents spécialisés | ✅ Fait |
| | Guardrails | Trouver une librairie adaptée | ✅ Fait |
| | RAG moderne | HyDE, rewriting, reranking | ✅ Fait |

# System design

## Offline

https://www.figma.com/board/FvgDWrRwr15tYYXAuU9p90/Offline

## Online

https://www.figma.com/board/9LLqepcrMhF7HL8ktBCNTv/Untitled

# Technical stack (with justifications)

-   **Streamlit** : Interface rapide pour chat + gestion documents\
-   **Docker** : Déploiement Elasticsearch + Kibana\
-   **Python** : Langage principal\
-   **LangChain** : Agents + sorties structurées\
-   **LLM (gpt-4.1)** : Reformulation, instructions, guardrails\
-   **Elasticsearch** : Stockage vectoriel + filtres\
-   **Kibana** : Visualisation des index\
-   **Sentence-Transformers** : Embeddings
    -   Modèle : `paraphrase-multilingual-mpnet-base-v2`\
-   **Transformers (HF)** : Reranking avec
    `crossencoder-camembert-base-mmarcoFR`\
-   **Pandas** : Conversion CSV → JSON\
-   **Pydantic** : Schémas typés\
-   **dotenv** : Gestion des clés API

# Étapes du projet

1.  Lecture et clarification du périmètre → tableau requirements /
    features\
2.  Veille sur l'état de l'art RAG (HyDE, rewriting, reranking...)\
3.  System design backend\
4.  Développement

# Développement

Journal :\
https://www.notion.so/Journal-de-bord-2aa42eb891f6802397a3d80e734d7210

## Implementation

-   Architecture modulaire (preprocessing, embeddings, storage, agents)\
-   Typage complet\
-   Pipeline RAG\
-   Conception du front-end

# Results

https://github.com/cleophass/test_technique

# Références

-   Query Rewriting : https://aclanthology.org/2023.emnlp-main.322.pdf
-   HyDE : Gao et al., 2023
-   HTML structure : https://aclanthology.org/2023.emnlp-main.322.pdf
-   Tabular encoding : https://arxiv.org/pdf/2401.02333
