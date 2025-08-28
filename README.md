# 🤖 Agent IA - Analyse de Données

Une application Streamlit avancée permettant d'interagir avec des données CSV/Excel en langage naturel grâce à l'intelligence artificielle.

## 🌟 Fonctionnalités

### 🧠 Intelligence Artificielle
- **Agent IA avec LangChain** : Interaction en langage naturel avec vos données
- **Cache sémantique FAISS** : Optimisation des requêtes répétitives
- **Base vectorielle ChromaDB** : Stockage persistant et recherche sémantique

### 📊 Analyse de Données
- **Support multi-formats** : CSV, XLSX, XLS
- **Analyse automatique** : Statistiques descriptives, détection de tendances
- **Questions en français** : Posez vos questions naturellement

### 📈 Visualisations Intelligentes
- **Génération automatique** : Histogrammes, scatter plots, line charts, bar charts
- **Heatmaps de corrélation** : Analyse des relations entre variables
- **Export d'images** : Téléchargement en format PNG haute résolution

### 💡 Interface Moderne
- **Interface Streamlit** : Design moderne et intuitif
- **Chat interactif** : Conversation naturelle avec l'IA
- **Gestion de fichiers** : Upload et gestion simplifiés

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- Clé API OpenAI

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd ChatPOC2
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration des variables d'environnement**
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env et ajouter votre clé API OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Lancer l'application**
```bash
streamlit run app.py
```

## 📁 Structure du Projet

```
ChatPOC2/
├── app.py                          # Interface Streamlit principale
├── requirements.txt                # Dépendances Python
├── .env.example                   # Exemple de configuration
├── README.md                      # Documentation
├── src/
│   └── components/
│       ├── semantic_cache.py     # Cache sémantique FAISS
│       ├── data_manager.py       # Gestionnaire ChromaDB
│       └── ai_agent.py           # Agent IA LangChain
├── data/                          # Fichiers de données uploadés
├── cache/                         # Cache sémantique FAISS
├── chroma_db/                     # Base de données ChromaDB
└── exports/                       # Visualisations exportées
```

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# API OpenAI (obligatoire)
OPENAI_API_KEY=your_openai_api_key_here

# Configuration ChromaDB
CHROMA_DB_PATH=./chroma_db

# Configuration du cache sémantique
SEMANTIC_CACHE_THRESHOLD=0.85
FAISS_INDEX_PATH=./cache

# Configuration de l'application
APP_TITLE=Agent IA - Analyse de Données
APP_DESCRIPTION=Interagissez avec vos données en langage naturel

# Configuration des modèles
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.1

# Configuration des fichiers
MAX_FILE_SIZE_MB=50
SUPPORTED_FORMATS=csv,xlsx,xls

# Configuration des visualisations
PLOT_DPI=300
PLOT_FORMAT=png
```

## 💬 Utilisation

### 1. Chargement des données
1. Utilisez la sidebar pour uploader un fichier CSV ou Excel
2. Cliquez sur "Charger le fichier"
3. Attendez la confirmation de chargement

### 2. Interaction avec l'IA
Posez vos questions en français dans le chat. Exemples :

#### 📊 Analyse descriptive
- "Montre-moi un résumé des données"
- "Quelles sont les colonnes disponibles ?"
- "Combien de lignes contient le dataset ?"
- "Y a-t-il des valeurs manquantes ?"

#### 📈 Visualisations
- "Crée un histogramme de la colonne âge"
- "Montre la corrélation entre les variables numériques"
- "Fais un graphique en barres des catégories"
- "Trace un scatter plot entre X et Y"

#### 🔍 Questions métier
- "Quelle est la tendance des ventes par mois ?"
- "Trouve les valeurs aberrantes dans les prix"
- "Compare les performances par région"
- "Calcule la moyenne des revenus par catégorie"

### 3. Visualisations
- Les graphiques sont générés automatiquement
- Utilisez le bouton "Télécharger l'image" pour exporter
- Formats supportés : PNG haute résolution (300 DPI)

## 🧠 Architecture Technique

### Cache Sémantique (FAISS)
```python
# Le système de cache utilise FAISS pour stocker les embeddings
# et retourne des réponses cachées si la similarité > seuil
semantic_cache = SemanticCache(
    threshold=0.85,  # Seuil de similarité
    cache_dir="./cache",
    max_cache_size=1000
)
```

### Base Vectorielle (ChromaDB)
```python
# ChromaDB stocke les données de manière persistante
# et permet la recherche sémantique
data_manager = DataManager(
    db_path="./chroma_db",
    collection_name="data_collection"
)
```

### Agent IA (LangChain)
```python
# L'agent combine pandas, OpenAI et les outils de visualisation
ai_agent = AIAgent(
    openai_api_key=OPENAI_API_KEY,
    data_manager=data_manager,
    semantic_cache=semantic_cache
)
```

## 🎯 Fonctionnalités Avancées

### Cache Sémantique Intelligent
- **Optimisation des performances** : Les requêtes similaires sont servies depuis le cache
- **Seuil de similarité configurable** : Contrôle de la précision du cache
- **Éviction automatique** : Gestion intelligente de la mémoire

### Recherche Vectorielle
- **Indexation automatique** : Les données sont automatiquement vectorisées
- **Recherche sémantique** : Compréhension du contexte des requêtes
- **Persistance** : Les données restent disponibles entre les sessions

### Génération de Visualisations
- **Détection automatique du type** : L'IA choisit le graphique approprié
- **Paramètres optimisés** : Configuration automatique selon les données
- **Export haute qualité** : Images PNG 300 DPI

## 🔍 Exemples Concrets

### Dataset de ventes
```
Fichier: ventes_2024.csv
Colonnes: date, produit, quantite, prix_unitaire, region, vendeur

Questions possibles:
- "Quelle région a les meilleures ventes ?"
- "Montre l'évolution des ventes par mois"
- "Quel vendeur est le plus performant ?"
- "Crée un graphique des ventes par produit"
```

### Dataset RH
```
Fichier: employes.xlsx
Colonnes: nom, age, salaire, departement, anciennete, performance

Questions possibles:
- "Quel est le salaire moyen par département ?"
- "Y a-t-il une corrélation entre âge et salaire ?"
- "Montre la distribution des performances"
- "Compare l'ancienneté entre les départements"
```

## 🛠️ Dépannage

### Erreurs communes

1. **Clé API manquante**
```
Solution: Vérifiez votre fichier .env et votre clé OpenAI
```

2. **Fichier non supporté**
```
Solution: Utilisez uniquement CSV, XLSX ou XLS
```

3. **Mémoire insuffisante**
```
Solution: Réduisez la taille du fichier ou augmentez la RAM
```

4. **Erreur de visualisation**
```
Solution: Vérifiez que les colonnes existent et sont du bon type
```

### Logs et debug
- Les logs sont affichés dans la console Streamlit
- Niveau de log configurable dans le code
- Messages d'erreur détaillés dans l'interface

## 🚀 Performance

### Optimisations implémentées
- **Cache sémantique** : Réduction du temps de réponse
- **Chunking des données** : Traitement efficace des gros fichiers
- **Embeddings optimisés** : Modèles légers et rapides
- **Persistance** : Évite le rechargement des données

### Limites recommandées
- **Taille de fichier** : 50 MB maximum
- **Nombre de lignes** : 100,000 lignes maximum
- **Cache** : 1,000 entrées maximum

## 🤝 Contribution

1. Fork du projet
2. Créer une branche feature
3. Commit des changements
4. Push sur la branche
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
1. Consultez cette documentation
2. Vérifiez les logs dans la console
3. Créez une issue sur GitHub

---

**Développé avec ❤️ pour l'analyse de données intelligente**
