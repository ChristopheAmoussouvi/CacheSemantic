# 📊 Explication de la Logique du Chat de Visualisation de Données

**Date**: 3 octobre 2025  
**Projet**: AI Data Interaction Agent - ChatPOC2

---

## 🎯 Vue d'Ensemble

L'application est un **agent IA conversationnel local** qui permet aux utilisateurs d'**analyser et visualiser des données** (CSV/Excel) en utilisant le **langage naturel français**. Le système fonctionne **sans dépendance OpenAI** et repose sur une architecture locale intelligente.

---

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────┐
│                   INTERFACE STREAMLIT                    │
│                        (app.py)                          │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌──────────────┐
│  Data   │  │ Simple  │  │  LocalAI     │
│ Manager │  │  Cache  │  │   Agent      │
│(ChromaDB)│  │ (FAISS) │  │              │
└─────────┘  └─────────┘  └──────┬───────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
            ┌───────────┐  ┌──────────┐  ┌─────────────┐
            │ Decision  │  │   Viz    │  │   Data      │
            │   Tree    │  │ Manager  │  │  Analysis   │
            │ Chatbot   │  │(Seaborn) │  │   Tools     │
            └───────────┘  └──────────┘  └─────────────┘
```

---

## 🔄 Flux de Traitement d'une Requête Utilisateur

### **Étape 1: Réception de la Question** 📥
```python
# app.py - Interface Streamlit
user_question = st.chat_input("Posez votre question sur les données...")
```

**Exemple**: "Montre-moi les ventes par région"

---

### **Étape 2: Vérification du Cache** 🔄

```python
# app.py -> _get_ai_response()
cached_entry = simple_cache.get(question)
if cached_entry:
    return cached_entry  # ⚡ Réponse instantanée du cache
```

**Le système de cache (SimpleCache)**:
- Utilise **FAISS** pour la recherche sémantique
- Compare la question avec les questions précédentes
- Seuil de similarité: **85%** (configurable)
- Si trouvée → réponse instantanée avec visualisation cachée

**Avantages**:
- ⚡ Réponses ultra-rapides pour questions similaires
- 💾 Évite la régénération de visualisations identiques
- 🎯 Recherche sémantique (comprend les paraphrases)

---

### **Étape 3: Traitement par l'Agent IA Local** 🤖

Si pas de cache, l'agent traite la requête:

```python
# ai_agent.py -> process_query()
analysis = self.chatbot.analyze_query(query, self.current_dataframe)
```

**L'agent IA identifie 3 types d'actions**:

#### **Action 1: SUMMARY** (Résumé)
```python
# Détecté par mots-clés: "résumé", "aperçu", "statistiques"
if analysis['action'] == 'summary':
    result = self._handle_summary_request(parameters)
```

**Génère**:
- Nombre de lignes/colonnes
- Types de données par colonne
- Statistiques descriptives (moyenne, min, max)
- Valeurs manquantes

**Exemple de sortie**:
```
Résumé des données
- Nombre de lignes: 1,250
- Nombre de colonnes: 8
Colonnes disponibles:
- Region (object)
- Ventes (int64)
- Date (datetime64)
Statistiques numériques:
- Ventes: Moy=15234.50, Min=1200.00, Max=45600.00
```

---

#### **Action 2: VISUALIZATION** (Visualisation) 📊

```python
# Détecté par: "graphique", "visualise", "montre", "crée un chart"
if analysis['action'] == 'visualization':
    result = self._handle_visualization_request(parameters)
```

**Processus de création de visualisation**:

1. **Extraction des paramètres**:
   ```python
   viz_type = parameters.get('viz_type', 'bar_chart')
   columns = parameters.get('columns', {})
   title = parameters.get('title', 'Visualisation des données')
   ```

2. **Appel au Visualization Manager**:
   ```python
   viz_base64, from_cache = self.viz_manager.get_or_create_visualization(
       viz_type=viz_type,
       dataframe=self.current_dataframe,
       columns=columns,
       title=title
   )
   ```

3. **Types de visualisations supportés**:
   - `histogram` - Distribution d'une variable
   - `scatter` - Corrélation entre deux variables
   - `bar_chart` - Comparaison par catégories
   - `line_chart` - Évolution temporelle
   - `heatmap` - Matrice de corrélation
   - `boxplot` - Distribution et outliers

4. **Génération avec Seaborn/Matplotlib**:
   ```python
   # visualization_manager.py
   fig, ax = plt.subplots(figsize=(10, 6))
   sns.barplot(data=dataframe, x=columns['x'], y=columns['y'], ax=ax)
   ax.set_title(title, fontsize=14, fontweight='bold')
   
   # Conversion en base64 pour affichage web
   buffer = BytesIO()
   fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
   img_base64 = base64.b64encode(buffer.getvalue()).decode()
   ```

5. **Cache de visualisation**:
   - ID unique basé sur: `viz_type + colonnes + hash_données`
   - Stocké dans **ChromaDB** séparé (`viz_chroma_db/`)
   - Évite la régénération si données identiques

---

#### **Action 3: ANALYSIS** (Analyse) 🔍

```python
# Détecté par: "analyse", "corrélation", "tendance", "compare"
if analysis['action'] == 'analysis':
    result = self._handle_analysis_request(parameters)
```

**Types d'analyses**:
- Corrélations entre variables
- Groupements et agrégations
- Filtres et recherches
- Calculs statistiques avancés

---

### **Étape 4: Décision Tree Chatbot** 🌳

Le **DecisionTreeChatbot** est le cerveau qui analyse la question:

```python
# decision_tree_chatbot.py
def analyze_query(self, query: str, dataframe: pd.DataFrame) -> Dict[str, Any]:
    query_lower = query.lower()
    
    # Détection de l'intention par mots-clés
    if any(kw in query_lower for kw in ['résumé', 'aperçu', 'statistiques']):
        return {'action': 'summary', 'success': True}
    
    if any(kw in query_lower for kw in ['graphique', 'visualise', 'chart']):
        # Extraction des colonnes mentionnées
        columns = self._extract_columns(query, dataframe)
        # Détermination du type de viz optimal
        viz_type = self._determine_viz_type(query, columns, dataframe)
        return {
            'action': 'visualization',
            'parameters': {
                'viz_type': viz_type,
                'columns': columns,
                'title': self._generate_title(query)
            },
            'success': True
        }
```

**Intelligence du chatbot**:
- 🔍 **Détection d'intention** par mots-clés français
- 🎯 **Extraction de colonnes** depuis la question
- 📊 **Sélection automatique du type de graphique**
- 🧠 **Contexte conversationnel** (historique)

---

### **Étape 5: Génération de la Visualisation** 🎨

**Visualization Manager** - Cache intelligent:

```python
# visualization_manager.py
def get_or_create_visualization(self, viz_type, dataframe, columns, title):
    # 1. Générer ID unique
    data_hash = self.get_data_hash(dataframe)
    viz_id = self.generate_visualization_id(viz_type, columns, data_hash)
    
    # 2. Vérifier le cache ChromaDB
    try:
        results = self.viz_collection.get(ids=[viz_id])
        if results['metadatas']:
            # ✅ Visualisation trouvée dans le cache
            cached_img = results['metadatas'][0].get('image_base64')
            return cached_img, True  # from_cache=True
    except:
        pass
    
    # 3. Créer nouvelle visualisation
    img_base64 = self.create_visualization(viz_type, dataframe, columns, title)
    
    # 4. Sauvegarder dans ChromaDB pour prochaine fois
    self.viz_collection.add(
        ids=[viz_id],
        metadatas=[{
            'viz_type': viz_type,
            'columns': str(columns),
            'title': title,
            'image_base64': img_base64
        }]
    )
    
    return img_base64, False  # from_cache=False
```

**Avantages du cache de visualisations**:
- 🚀 **Performance**: Pas de régénération si données identiques
- 💾 **Persistance**: Visualisations sauvegardées entre sessions
- 🎯 **Déduplication**: Même question = même visualisation

---

### **Étape 6: Affichage dans l'Interface** 🖥️

```python
# app.py -> _display_ai_response()
def _display_ai_response(response_data: dict):
    # 1. Afficher le texte de réponse
    text = response_data.get('response', '')
    st.markdown(text)
    
    # 2. Si visualisation présente, afficher l'image
    viz_base64 = response_data.get('visualization')
    if viz_base64:
        img_bytes = base64.b64decode(viz_base64)
        st.image(img_bytes, caption="Visualisation générée")
    
    # 3. Indicateur de source
    source = response_data.get('source', 'inconnue')
    source_emoji = {'cache': '🔄', 'local_agent': '🤖'}
    st.caption(f"{source_emoji.get(source)} Source: {source}")
```

**L'interface Streamlit affiche**:
1. ✅ Question de l'utilisateur (chat message)
2. 💬 Réponse textuelle de l'agent
3. 📊 Visualisation interactive (si applicable)
4. 🏷️ Badge de source (cache vs nouveau)

---

## 🗄️ Système de Stockage Multi-Couches

### **1. ChromaDB Principal** (`chroma_db/`)
**Rôle**: Indexation des données sources

```python
# data_manager.py
self.collection.add(
    ids=[doc_id],
    embeddings=[embedding],
    documents=[text_chunk],
    metadatas=[{'file': filename, 'chunk': i}]
)
```

**Contenu**:
- Embeddings des données CSV/Excel
- Métadonnées des fichiers chargés
- Permet recherche sémantique dans les données

---

### **2. ChromaDB Visualisations** (`viz_chroma_db/`)
**Rôle**: Cache des graphiques générés

```python
self.viz_collection.add(
    ids=[viz_id],
    metadatas=[{
        'viz_type': 'bar_chart',
        'image_base64': img_base64,
        'columns': "{'x': 'Region', 'y': 'Ventes'}"
    }]
)
```

**Contenu**:
- Images PNG encodées en base64
- Métadonnées de chaque visualisation
- Permet récupération rapide

---

### **3. FAISS Cache** (`cache/`)
**Rôle**: Cache sémantique des questions/réponses

```python
# simple_cache.py
self.index.add(np.array([embedding]))
self.cache[question] = {
    'response': response_data,
    'visualization': viz_base64,
    'timestamp': datetime.now()
}
```

**Contenu**:
- Index FAISS des embeddings de questions
- Réponses complètes associées
- Permet recherche par similarité sémantique

---

### **4. Métadonnées Q&A** (`qa_visualizations/`)
**Rôle**: Catalogue de questions préparées

**Fichiers**:
- `qa_catalog.json` - 59 paires Q&A préparées
- `viz_type_index.json` - Index par type de viz
- `dataset_index.json` - Index par dataset
- `generation_stats.json` - Statistiques globales

**Exemple**:
```json
{
  "question": "Quelles sont les ventes par région ?",
  "viz_type": "bar",
  "dataset": "ventes",
  "columns": {"x": "Region", "y": "Ventes"}
}
```

---

## 🔧 Composants Techniques Détaillés

### **LocalAIAgent** - Orchestrateur principal

**Responsabilités**:
1. ✅ Charger les DataFrames
2. 🔍 Router les requêtes vers les bons handlers
3. 🧠 Maintenir l'historique conversationnel
4. 🎯 Coordonner cache + chatbot + viz manager

```python
class LocalAIAgent:
    def __init__(self, data_manager, simple_cache, viz_manager):
        self.data_manager = data_manager
        self.simple_cache = simple_cache
        self.viz_manager = viz_manager
        self.chatbot = DecisionTreeChatbot()
        self.conversation_history = []
```

---

### **DataManager** - Gestionnaire de données

**Responsabilités**:
1. 📂 Charger CSV/Excel
2. 🔐 Anonymiser les données sensibles (PII)
3. 🧮 Générer embeddings avec sentence-transformers
4. 💾 Indexer dans ChromaDB
5. 🔍 Recherche vectorielle

**Anonymisation avancée**:
- Détection de noms (même non communs, Maghreb/arabes)
- Masquage emails, téléphones, numéros
- Analyse d'entropie Shannon
- Patterns linguistiques internationaux

---

### **VisualizationManager** - Création de graphiques

**Responsabilités**:
1. 🎨 Créer visualisations Seaborn/Matplotlib
2. 💾 Cacher dans ChromaDB
3. 🔍 Récupérer visualisations existantes
4. 📐 Adapter le type de viz aux données

**Types supportés**:
```python
VIZ_TYPES = [
    'histogram',    # Distribution
    'scatter',      # Corrélation
    'bar_chart',    # Comparaison
    'line_chart',   # Tendance
    'heatmap',      # Matrice
    'boxplot'       # Distribution + outliers
]
```

---

### **DecisionTreeChatbot** - Analyse d'intention

**Responsabilités**:
1. 🔍 Analyser la question en français
2. 🎯 Détecter l'intention (summary/viz/analysis)
3. 📊 Extraire colonnes et paramètres
4. 🧠 Déterminer le meilleur type de visualisation

**Algorithme de détection**:
```python
# Mots-clés par intention
SUMMARY_KEYWORDS = ['résumé', 'aperçu', 'statistiques', 'décris']
VIZ_KEYWORDS = ['graphique', 'visualise', 'montre', 'chart', 'plot']
ANALYSIS_KEYWORDS = ['analyse', 'corrélation', 'compare', 'tendance']

# Types de viz par contexte
if 'évolution' in query or 'temps' in query:
    viz_type = 'line_chart'
elif 'corrélation' in query or 'relation' in query:
    viz_type = 'scatter'
elif 'distribution' in query:
    viz_type = 'histogram'
```

---

### **SimpleCache** - Cache sémantique

**Responsabilités**:
1. 🔢 Générer embeddings des questions
2. 🔍 Recherche par similarité FAISS
3. 💾 Stocker réponses + visualisations
4. ⚡ Retourner résultats cachés

**Mécanisme**:
```python
def get(self, question: str) -> Optional[Dict]:
    # 1. Créer embedding de la question
    query_embedding = self.model.encode([question])[0]
    
    # 2. Rechercher dans l'index FAISS
    distances, indices = self.index.search(
        np.array([query_embedding]), 
        k=1
    )
    
    # 3. Vérifier similarité
    if distances[0][0] < THRESHOLD:
        cached_question = self.questions[indices[0][0]]
        return self.cache[cached_question]
    
    return None  # Pas de cache
```

---

## 📊 Exemple de Flux Complet

**Question**: "Montre-moi un graphique des ventes par région"

### **Étape par étape**:

1. **Interface Streamlit** 📥
   ```
   User Input: "Montre-moi un graphique des ventes par région"
   → _handle_user_question()
   ```

2. **Vérification Cache** 🔄
   ```
   SimpleCache.get("Montre-moi un graphique...")
   → Aucune question similaire trouvée
   → Cache MISS
   ```

3. **Traitement Agent** 🤖
   ```
   LocalAIAgent.process_query()
   → DecisionTreeChatbot.analyze_query()
   
   Détection:
   - Mot-clé "graphique" → VISUALIZATION
   - Extraction colonnes: "ventes", "région"
   - Type détecté: bar_chart (catégorie vs numérique)
   
   Résultat:
   {
       'action': 'visualization',
       'parameters': {
           'viz_type': 'bar_chart',
           'columns': {'x': 'Region', 'y': 'Ventes'},
           'title': 'Ventes par région'
       },
       'success': True
   }
   ```

4. **Génération Visualisation** 🎨
   ```
   VisualizationManager.get_or_create_visualization()
   
   → Génération ID: hash('bar_chart' + 'Region,Ventes' + data_hash)
   → Vérification ChromaDB viz: Pas trouvé
   → create_visualization():
       - Seaborn: sns.barplot(data=df, x='Region', y='Ventes')
       - Titre: "Ventes par région"
       - Export PNG → base64
   → Sauvegarde ChromaDB
   
   Retour: (img_base64, from_cache=False)
   ```

5. **Mise en Cache** 💾
   ```
   SimpleCache.put("Montre-moi un graphique...", result)
   
   → Embedding de la question
   → Ajout à l'index FAISS
   → Stockage:
       {
           'response': "Visualisation créée: Ventes par région",
           'visualization': img_base64,
           'source': 'local_agent',
           'timestamp': '2025-10-03 10:30:00'
       }
   ```

6. **Affichage Interface** 🖥️
   ```
   _display_ai_response(response_data)
   
   Streamlit affiche:
   ┌─────────────────────────────────────┐
   │ 🤖 Assistant                        │
   │                                     │
   │ Visualisation créée: Ventes par    │
   │ région (nouvellement créée)         │
   │                                     │
   │ [IMAGE: Graphique bar chart]        │
   │                                     │
   │ 🤖 Source: local_agent              │
   └─────────────────────────────────────┘
   ```

7. **Requête Similaire Future** ⚡
   ```
   User Input: "Affiche les ventes par région"
   
   SimpleCache.get("Affiche les ventes...")
   → Similarité: 92% avec "Montre-moi un graphique..."
   → Cache HIT ✅
   → Réponse instantanée (sans régénération)
   
   Temps de réponse: 50ms au lieu de 2000ms
   ```

---

## 🎯 Points Clés de l'Architecture

### **1. Système Local 100%**
❌ Pas de dépendance OpenAI  
✅ Sentence-transformers pour embeddings  
✅ Analyse par mots-clés français  
✅ Seaborn/Matplotlib pour visualisations  

### **2. Triple Cache Intelligent**
1. **FAISS**: Questions similaires → réponses instantanées
2. **ChromaDB Viz**: Graphiques identiques → pas de régénération
3. **ChromaDB Data**: Données indexées → recherche rapide

### **3. Architecture Modulaire**
- `DataManager` → Gestion données
- `LocalAIAgent` → Orchestration
- `DecisionTreeChatbot` → Analyse intention
- `VisualizationManager` → Création graphiques
- `SimpleCache` → Cache sémantique

### **4. Flux Optimisé**
```
Question → Cache? → OUI → Réponse instantanée (50ms)
                  → NON → Analyse (500ms)
                        → Viz cachée? → OUI → Récupération (200ms)
                                      → NON → Génération (2000ms)
                        → Mise en cache → Réponse
```

---

## 📈 Performance & Statistiques

### **État Actuel du Système**:
- **59 paires Q&A** préparées dans `qa_visualizations/`
- **6 documents** indexés dans ChromaDB
- **6 types de visualisations** supportés
- **4 datasets** couverts (ventes, clients, financier, satisfaction)

### **Temps de Réponse**:
- **Cache hit**: ~50ms ⚡
- **Viz cachée**: ~200ms 🚀
- **Nouvelle viz**: ~2000ms 🎨
- **Résumé**: ~100ms 📊

### **Taux de Cache** (estimé):
- Questions similaires: ~60-70% hit rate
- Visualisations identiques: ~40-50% hit rate

---

## 🚀 Améliorations Futures Possibles

1. **Intelligence NLP avancée**
   - Intégration spaCy pour NER
   - Analyse syntaxique plus poussée
   - Compréhension de questions complexes

2. **Visualisations interactives**
   - Passage à Plotly pour interactivité
   - Zoom, filtres, tooltips dynamiques
   - Export multi-format (PDF, SVG)

3. **Analyses avancées**
   - ML automatique (AutoML)
   - Prédictions et forecasting
   - Détection d'anomalies

4. **Intégration Q&A préparées**
   - Utiliser les 59 paires stockées
   - Suggestions intelligentes
   - Apprentissage des préférences utilisateur

---

## 💡 Conclusion

Le système de **Chat de Visualisation de Données** est une architecture **locale, performante et intelligente** qui permet:

✅ **Interaction naturelle** en français  
✅ **Visualisations automatiques** adaptées aux données  
✅ **Cache multi-niveaux** pour performances optimales  
✅ **Aucune dépendance externe** (OpenAI)  
✅ **Anonymisation avancée** des données sensibles  

L'architecture modulaire permet une **extension facile** et une **maintenance simplifiée** tout en offrant une **expérience utilisateur fluide** pour l'analyse de données.
