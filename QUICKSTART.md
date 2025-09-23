# 🚀 Guide de Démarrage Rapide (Mise à jour 2025)

Agent d'analyse de données 100% local (aucun appel externe) avec interface Streamlit, gestion intelligente de prompts et génération de visualisations.

---
## ✅ Fonctionnalités Principales

- Chargement multi-fichiers CSV / Excel
- Indexation locale (ChromaDB)
- Agent déterministe (arbre de décision) – pas de LLM
- Cache simple des réponses
- Visualisations Seaborn/Matplotlib exportables (PNG)
- Gestion avancée des prompts :
	- Catégories + prompts d'exemple
	- Ajout de prompts personnalisés persistants (`custom_prompts.json`)
	- Marquage `(custom)` automatique
	- Sélecteurs dynamiques des colonnes (X, Y, multiples)
	- Validation automatique des colonnes vs DataFrame
	- Suggestion du type de visualisation + bouton "Appliquer suggestion"
	- Recherche textuelle (catégorie / titre / contenu)
- Récupération de visualisations identiques depuis le cache
- Outils d'administration : reset DB, vider cache, effacer historique

---
## 🛠 Installation

```powershell
git clone <url-du-repo>
cd ChatPOC2
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Créer le fichier d'environnement :
```powershell
copy .env.example .env
```

Variables utiles :
```env
CHROMA_DB_PATH=./chroma_db
SEMANTIC_CACHE_THRESHOLD=0.85
FAISS_INDEX_PATH=./cache
```

Lancement :
```powershell
streamlit run app.py
```

Accès : http://localhost:8501

---
## 📂 Structure
```
app.py
src/components/
	ai_agent.py
	data_manager.py
	visualization_manager.py
	simple_cache.py
	decision_tree_chatbot.py
src/utils/example_prompts.py
custom_prompts.json
data/
chroma_db/
cache/
exports/
```

---
## 🚀 Première Utilisation
1. Charger un fichier (ex: data/exemple_ventes.csv)
2. Onglet "💬 Chat": poser "Montre-moi un résumé des données"
3. Tester une visualisation: "Crée un graphique des ventes par région"
4. Onglet "🧪 Prompts": ajouter un prompt custom avec colonnes X/Y
5. Cliquer sur "Appliquer suggestion" si proposé
6. Utiliser la recherche pour filtrer des prompts

---
## � Exemples de Requêtes

Analyse :
```
Montre-moi un résumé des données
Quels sont les produits les plus vendus ?
Y a-t-il des valeurs aberrantes ?
```

Visualisations :
```
Crée un histogramme du prix
Affiche l'évolution des ventes dans le temps
Montre la relation entre prix et quantité vendue
```

Exploration avancée :
```
Affiche une matrice de corrélation
Identifie des patterns intéressants
Fais un clustering automatique
```

---
## 🧪 Prompts Personnalisés
Dans l'onglet "🧪 Prompts" :
1. Catégorie, titre, texte
2. Sélectionner X, Y et/ou colonnes multiples
3. (Optionnel) Appliquer la suggestion de visualisation
4. Enregistrer → apparaît avec suffixe (custom)

Persistant dans `custom_prompts.json`.

---
## 🔍 Recherche de Prompts
Champ "Recherche" = filtre plein texte (catégorie / titre / contenu). Combinable avec filtre de catégorie.

---
## 🧠 Suggestions de Visualisation
Règles simples :
- X numérique + Y numérique → scatter
- X temporel + Y numérique → line_chart
- X catégoriel + Y numérique → bar_chart
- Y seul numérique → histogram
- ≥3 colonnes numériques (liste) → heatmap
- Fallback → boxplot

Le bouton "Appliquer suggestion" remplit le champ si désiré.

---
## 🗃 Cache & Indexation
- Cache : stocke réponses & visuels (évite recomputation)
- ChromaDB : stockage vectoriel local
- Visualisation identique → récupérée instantanément

---
## 🔧 Administration
Onglet Configuration :
- Réinitialiser base (ChromaDB)
- Vider cache simple
- Effacer historique du chat

---
## 🆘 Dépannage
| Problème | Solution |
|----------|----------|
| Aucune colonne dans sélecteurs | Charger un fichier valide |
| Visualisation vide | Vérifier colonnes X/Y sélectionnées |
| Lenteur | Limiter taille fichier, nettoyer cache |
| Port occupé | `streamlit run app.py --server.port 8502` |
| Fichier verrouillé | Fermer Excel ou autre programme |

---
## ♻️ Flux Recommandé
Charger → Explorer (prompts rapides) → Affiner (prompts custom) → Générer visuels → Exporter → Répéter.

---
## � Localité & Données
Tout reste en local. Aucun envoi externe.

---
## 🚀 Améliorations Possibles
- Edition / suppression de prompts custom
- Multi-DataFrames
- Export rapport PDF
- Anomalies avancées

---
**🎉 L'agent est opérationnel. Bonne analyse !**
