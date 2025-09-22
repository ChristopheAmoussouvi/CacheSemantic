# 🤖 Agent IA - Analyse de Données Locale

Une application Streamlit avancée permettant d'interagir avec des données CSV/Excel en langage naturel grâce à un système intelligent **100% local** (sans LLM/OpenAI).

## 🌟 Fonctionnalités

### 🧠 Intelligence Locale
- **Chatbot à arbre de décision** : Interaction en langage naturel avec logique déterministe
- **Cache simple local** : Optimisation des requêtes répétitives sans dépendances externes
- **Base vectorielle ChromaDB** : Stockage persistant et recherche sémantique

### 📊 Analyse de Données
- **Support multi-formats** : CSV, XLSX, XLS
- **Analyse automatique** : Statistiques descriptives, détection de tendances
- **Questions en français** : Posez vos questions naturellement

### 📈 Visualisations Intelligentes
- **Génération automatique** : Histogrammes, scatter plots, line charts, bar charts, heatmaps, boxplots
- **Gestionnaire de visualisations ChromaDB** : Cache persistant des graphiques générés
- **Export d'images** : Téléchargement en format PNG haute résolution (300 DPI)

### 💡 Interface Moderne
- **Interface Streamlit** : Design moderne et intuitif avec thème sombre
- **Chat interactif** : Conversation naturelle avec logique locale intelligente
- **Génération de données test** : Datasets réalistes intégrés (ventes, clients, produits)
- **Prompts d'exemples** : 40+ exemples de questions pré-enregistrés

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- **Aucune clé API requise** - Fonctionnement 100% local

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

3. **Lancer l'application**
```bash
streamlit run app.py
```

**Alternative :** Utiliser les scripts de démarrage
- Windows : `start.bat`
- PowerShell : `start.ps1`

## 📁 Structure du Projet

```
ChatPOC2/
├── app.py                          # Interface Streamlit principale
├── requirements.txt                # Dépendances Python (locales uniquement)
├── README.md                      # Documentation
├── start.bat / start.ps1          # Scripts de démarrage
├── src/
│   ├── components/
│   │   ├── simple_cache.py       # Cache local (remplace FAISS)
│   │   ├── data_manager.py       # Gestionnaire ChromaDB
│   │   ├── ai_agent.py           # Agent IA local (sans LLM)
│   │   └── visualization_manager.py # Gestionnaire visualisations
│   └── utils/
│       ├── data_generator.py     # Générateur de données test
│       ├── example_prompts.py    # Prompts d'exemples
│       └── qa_generator.py       # Génération Q&A/visualisations
├── data/                          # Données d'exemple et uploadées
├── cache/                         # Cache local
├── chroma_db/                     # Base de données ChromaDB
├── qa_visualizations/             # Q&A et visualisations générées
└── exports/                       # Visualisations exportées
```

## 🔧 Configuration

### Configuration Streamlit (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "monospace"

[server]
port = 8501
headless = false
runOnSave = true
```

### Configuration de l'application (directement dans le code)

```python
# Configuration ChromaDB
CHROMA_DB_PATH = "./chroma_db"

# Configuration du cache local
CACHE_DIR = "./cache"

# Configuration de l'application
APP_TITLE = "Agent IA - Analyse de Données Locale"
APP_DESCRIPTION = "Interagissez avec vos données en langage naturel (100% local)"

# Configuration des fichiers
MAX_FILE_SIZE_MB = 50
SUPPORTED_FORMATS = ["csv", "xlsx", "xls"]

# Configuration des visualisations
PLOT_DPI = 300
PLOT_FORMAT = "png"
```

## 💬 Utilisation

### 1. Chargement des données
**Option A : Upload de fichier**
1. Utilisez la sidebar pour uploader un fichier CSV ou Excel
2. Cliquez sur "Charger le fichier"
3. Attendez la confirmation de chargement

**Option B : Données d'exemple**
1. Cliquez sur "Générer des données d'exemple" dans la sidebar
2. Choisissez parmi : Ventes, Clients, Produits, Employés, Marketing
3. Le dataset est automatiquement chargé

### 2. Interaction avec le système local
Posez vos questions en français dans le chat ou utilisez les prompts d'exemples. Exemples :

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

### 3. Utilisation des prompts d'exemples
- Cliquez sur "Exemples de prompts" dans la sidebar
- Choisissez parmi plus de 40 exemples organisés par catégories
- Les prompts sont automatiquement insérés dans le chat

### 4. Visualisations
- Les graphiques sont générés automatiquement avec Seaborn/Matplotlib
- Système de cache intelligent avec ChromaDB
- Utilisez le bouton "Télécharger l'image" pour exporter
- Formats supportés : PNG haute résolution (300 DPI)

## 🧠 Architecture Technique

### Cache Local Simple
```python
# Système de cache local avec hachage MD5
# Aucune dépendance externe requise
simple_cache = SimpleCache(
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

### Agent IA Local
```python
# Agent local avec chatbot à arbre de décision
# Aucune API externe requise
local_agent = LocalAIAgent(
    data_manager=data_manager,
    visualization_manager=visualization_manager,
    simple_cache=simple_cache
)
```

### Chatbot à Arbre de Décision
```python
# Logique déterministe pour analyser les requêtes
chatbot = DecisionTreeChatbot()
# Détecte automatiquement : visualisations, statistiques, requêtes
```

## 🎯 Fonctionnalités Avancées

### Cache Local Intelligent
- **Optimisation des performances** : Les requêtes identiques sont servies depuis le cache
- **Hachage MD5** : Système de cache simple et efficace
- **Éviction automatique** : Gestion intelligente de la mémoire

### Système Q&A Intelligent
- **59 Q&A pré-générées** : Questions et visualisations correspondantes
- **Index de recherche** : Recherche par mots-clés, datasets, types de visualisations
- **Script d'intégration** : `qa_search_tool.py` pour explorer les Q&A

### Génération de Données Test
- **5 domaines métier** : Ventes, Clients, Produits, Employés, Marketing
- **Données réalistes** : Corrélations et distributions authentiques
- **Intégration Streamlit** : Génération directe dans l'interface

### Gestionnaire de Visualisations ChromaDB
- **Cache persistant** : Les visualisations sont stockées et réutilisées
- **Détection automatique du type** : Logique déterministe pour choisir le graphique
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

## 🛠️ Utilitaires et Scripts

### Scripts de génération
```bash
# Générer des Q&A avec visualisations
python launch_qa_generator.py

# Créer les index de recherche Q&A
python create_qa_indexes.py

# Outil de recherche dans les Q&A
python qa_search_tool.py
```

### Dépannage

1. **Fichier non supporté**
```
Solution: Utilisez uniquement CSV, XLSX ou XLS
```

2. **Mémoire insuffisante**
```
Solution: Réduisez la taille du fichier ou augmentez la RAM
```

3. **Erreur de visualisation**
```
Solution: Vérifiez que les colonnes existent et sont du bon type
```

4. **ChromaDB non accessible**
```
Solution: Vérifiez les permissions du dossier chroma_db/
```

### Logs et debug
- Les logs sont affichés dans la console Streamlit
- Messages d'erreur détaillés dans l'interface
- Mode debug disponible dans le code

## 🚀 Performance

### Optimisations implémentées
- **Cache local simple** : Réduction du temps de réponse sans dépendances
- **Chunking des données** : Traitement efficace des gros fichiers
- **Logique déterministe** : Analyse rapide sans modèles externes
- **Persistance ChromaDB** : Évite le rechargement des données
- **Cache de visualisations** : Réutilisation des graphiques générés

### Limites recommandées
- **Taille de fichier** : 50 MB maximum
- **Nombre de lignes** : 100,000 lignes maximum
- **Cache** : 1,000 entrées maximum
- **Visualisations** : Cache ChromaDB sans limite théorique

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

## 🔄 Workflow Complet

### Pour un nouvel utilisateur
1. **Clone et installation** : `git clone` → `pip install -r requirements.txt`
2. **Démarrage** : `streamlit run app.py` ou `start.bat`
3. **Test avec données d'exemple** : Générer des données → Tester des prompts
4. **Exploration Q&A** : Utiliser `qa_search_tool.py` pour explorer les 59 Q&A
5. **Upload de ses données** : CSV/Excel personnalisés

### Pour développeurs
1. **Génération Q&A** : `python launch_qa_generator.py`
2. **Indexation** : `python create_qa_indexes.py`
3. **Test des fonctionnalités** : Interface Streamlit + scripts CLI
4. **Extension** : Ajouter de nouveaux types de données/visualisations

---

**🎯 Agent IA 100% Local - Aucune API externe requise**

**Développé avec ❤️ pour l'analyse de données intelligente et autonome**
