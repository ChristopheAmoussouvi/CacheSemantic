# 🚀 Guide de Démarrage Rapide (Mise à jour 2025)

Ce projet fournit un agent d'analyse de données 100% local (aucun appel OpenAI) avec interface Streamlit, génération de visualisations, gestion de prompts dynamiques et cache simple.

---
## ✅ Fonctionnalités Clés

- Chargement de fichiers CSV / Excel (multi-fichiers)
- Indexation locale via ChromaDB
- Agent IA local déterministe (arbre de décision)
- Cache simple (réponses réutilisées instantanément)
- Génération de visualisations (Seaborn / Matplotlib) avec export PNG
- Gestion avancée des prompts :
  - Prompts d'exemple organisés par catégorie
  - Ajout de prompts personnalisés persistants (fichier JSON)
  - Marquage automatique (custom)
  - Suggestion intelligente du type de visualisation selon les colonnes
  - Validation automatique des colonnes vs DataFrame courant
  - Sélecteurs dynamiques (selectbox / multiselect) pour colonnes X / Y / multiples
  - Bouton "Appliquer suggestion" (aucune auto-saisie forcée)
  - Recherche textuelle (titre / contenu / catégorie)
- Gestion des visualisations en cache (évite les régénérations identiques)
- Administration : reset DB, vider cache, effacer historique

---
## 🛠 Installation & Configuration

### 1. Cloner et préparer l'environnement

```powershell
# Cloner le dépôt
git clone <url-du-repo>
cd ChatPOC2

# (Optionnel) Créer un environnement virtuel
python -m venv .venv
./.venv/Scripts/Activate.ps1

# Installer dépendances
pip install -r requirements.txt
```

### 2. Fichier d'environnement

Copiez le fichier exemple :
```powershell
copy .env.example .env
```

Éditez `.env` si nécessaire (les variables OpenAI peuvent être ignorées si vous restez 100% local) :
```env
CHROMA_DB_PATH=./chroma_db
SEMANTIC_CACHE_THRESHOLD=0.85
FAISS_INDEX_PATH=./cache
```

### 3. Lancer l'application

```powershell
streamlit run app.py
```

Accédez ensuite à : http://localhost:8501

---
## 📂 Organisation du Projet
```
ChatPOC2/
├── app.py                  # Interface Streamlit
├── src/
│   ├── components/
│   │   ├── ai_agent.py     # Agent local + pipeline
│   │   ├── data_manager.py # Gestion ChromaDB
│   │   ├── visualization_manager.py
│   │   ├── simple_cache.py # Cache simple clé → résultat
│   │   └── decision_tree_chatbot.py
│   └── utils/
│       └── example_prompts.py # Prompts + gestion custom + suggestions
├── custom_prompts.json     # Persist des prompts utilisateurs
├── data/                   # Fichiers d'exemple
├── chroma_db/              # Stockage persistant vecteurs
├── cache/                  # Cache des résultats
└── exports/                # Graphiques PNG générés
```

---
## 🚀 Premier Parcours

1. Charger un fichier via la sidebar (ex: data/exemple_ventes.csv)
2. Poser une question dans l'onglet "💬 Chat" (ex: "Montre-moi un résumé des données")
3. Demander une visualisation (ex: "Crée un graphique des ventes par région")
4. Ajouter un prompt custom dans l'onglet "🧪 Prompts"
5. Utiliser la recherche pour filtrer des prompts
6. Appliquer une suggestion de type de visualisation

---
## �️ Démo Carte Choropleth (exemples inclus)

Des fichiers d'exemple sont fournis pour tester la carte immédiatement :

- Données agences: `data/sample_agencies.csv`
  - Colonnes: `name, latitude, longitude, reclamation_rate, zone_code`
- Polygones: `choropleth/sample_polygons.geojson`
  - Propriété de jointure: `code` (ex: PAR, LYO)

Essai rapide:
1. Dans la sidebar, chargez `data/sample_agencies.csv`
2. Onglet "🗺️ Carte Choropleth" → Mode "Polygones + Points"
3. Importez `choropleth/sample_polygons.geojson`
4. Clés de jointure:
   - Propriété GeoJSON: `code`
   - Colonne DataFrame: `zone_code`
5. Affichez la carte et utilisez le bouton de téléchargement HTML


---
## �💡 Exemples de Prompts

Analyse générale :
- "Montre-moi un résumé des données"
- "Quels sont les produits les plus vendus ?"

Visualisations :
- "Crée un histogramme du prix"
- "Affiche l'évolution des ventes dans le temps"
- "Montre la relation entre prix et quantité vendue"

Exploration :
- "Y a-t-il des valeurs aberrantes ?"
- "Quels sont les corrélations principales ?"

---
## 🧪 Ajout de Prompts Personnalisés

Dans l'onglet "🧪 Prompts" :
- Renseigner catégorie, titre, texte
- (Optionnel) Sélectionner colonnes X, Y et colonnes multiples
- Cliquer sur "Appliquer suggestion" si une proposition apparaît
- Enregistrer → le prompt est marqué (custom) et persisté dans `custom_prompts.json`

---
## 🔍 Recherche de Prompts

Champ "Recherche" :
- Filtre sur titre, contenu ET catégorie
- Combinable avec le filtre de catégorie

---
## 🧠 Suggestions de Visualisation

Heuristiques :
- X numérique + Y numérique → scatter
- X temporel + Y numérique → line_chart
- X catégoriel + Y numérique → bar_chart
- Y seul numérique → histogram
- 3+ colonnes numériques (liste) → heatmap
- Fallback → boxplot

Utilisation :
- La suggestion n'est pas imposée
- Cliquer sur "Appliquer suggestion" pour la retenir

---
## 🗃 Cache & Indexation

- Cache simple : évite recomputation de réponses identiques
- ChromaDB : index des données et visualisations (rejouabilité)
- Visualisation identique → récupérée rapidement

---
## 🛠 Administration
Dans l'onglet Configuration :
- Réinitialiser la base (ChromaDB)
- Vider le cache simple
- Effacer l'historique de chat

---
## 🧼 Maintenance / Nettoyage

Supprimer tous les graphiques générés :
```powershell
Remove-Item -Recurse -Force .\exports\*.png
```

Réinitialiser la DB : supprimer le dossier `chroma_db/` (ou via UI).

---
## 🆘 Dépannage

| Problème | Piste |
|----------|-------|
| Aucune donnée détectée | Vérifier format CSV/Excel, encodage UTF-8 |
| Pas de colonnes dans sélecteurs | Charger un fichier d'abord |
| Visualisation vide | Vérifier mapping colonnes X/Y |
| Lenteur | Réduire taille du fichier, nettoyer cache |
| Fichier verrouillé | Fermer l'application utilisant le fichier |

---
## ♻️ Flux de Travail Recommandé
1. Charger données
2. Explorer via prompts rapides
3. Affiner avec prompts custom
4. Générer et exporter visuels
5. Réutiliser réponses mises en cache

---
## 🔒 Données & Localité
Tout fonctionne en local : aucune donnée envoyée vers un service externe.

---
## ✅ Prochaines Améliorations Possibles (Roadmap)
- Edition / suppression de prompts custom
- Sélection de plusieurs DataFrames
- Génération automatique de rapports PDF
- Détection avancée d'anomalies

---
Bon usage et bonnes analyses ! 🎉
