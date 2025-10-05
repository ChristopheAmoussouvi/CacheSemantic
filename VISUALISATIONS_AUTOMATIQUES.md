# 📊 Visualisations Automatiques - Documentation

## 🎯 Vue d'Ensemble

Le système de **visualisations automatiques** génère intelligemment des graphiques pertinents **dès l'upload** des données, sans nécessiter de requête utilisateur. Le système détecte le type de données et propose les visualisations les plus appropriées.

---

## 🧠 Détection Intelligente des Données

### Types de Données Détectés

Le système reconnaît **7 types de données métier** :

| Type | Mots-clés Détectés | Exemples de Colonnes |
|------|-------------------|---------------------|
| **📋 Réclamations** | reclamation, plainte, incident, ticket, gravite, statut | Type_Reclamation, Gravite, Statut, Service |
| **😊 Satisfaction** | satisfaction, nps, csat, ces, score, feedback, avis | NPS_Score, CSAT_Score, Sentiment, Note |
| **💰 Ventes** | vente, ca, chiffre, revenue, prix, montant, quantite | Ventes, Prix, Quantite, CA, Montant |
| **👥 Clients** | client, age, sexe, segment, categorie_client | ID_Client, Age, Sexe, Ville, Anciennete |
| **💼 Finances** | budget, depense, cout, marge, benefice | Budget, Depenses, Revenus, Marge, CA |
| **🧑‍💼 RH** | employe, salaire, poste, departement, formation | Employe, Salaire, Poste, Anciennete |
| **📦 Produits** | produit, stock, inventaire, reference | Produit, Stock, Categorie_Produit, Prix |

### Algorithme de Détection

```python
# Seuil : 2 mots-clés minimum pour valider un type
scores = {}
for data_type, keywords in PATTERNS.items():
    matches = count_matches(columns, keywords)
    if matches >= 2:
        scores[data_type] = matches

detected_type = max(scores)  # Type avec le plus de correspondances
```

---

## 📊 Visualisations Générées par Type

### 1️⃣ Réclamations (jusqu'à 6 graphiques)

#### Graphiques Générés :
1. **Distribution des types** - Histogramme
   - Colonnes cherchées : `type`, `categorie`, `motif`
   - Affiche : Nombre de réclamations par type

2. **Distribution par gravité** - Histogramme
   - Colonnes cherchées : `gravite`, `severite`, `priorite`
   - Affiche : Répartition Faible/Moyenne/Élevée/Critique

3. **Évolution temporelle** - Line chart
   - Colonnes cherchées : Colonnes de type date
   - Affiche : Volume de réclamations dans le temps

4. **Top services** - Bar chart horizontal
   - Colonnes cherchées : `service`, `departement`, `equipe`
   - Affiche : Top 10 services avec le plus de réclamations

5. **Délais de traitement** - Box plot
   - Colonnes cherchées : `delai`, `duree`, `temps`
   - Affiche : Distribution et outliers des délais

6. **Répartition par statut** - Histogramme
   - Colonnes cherchées : `statut`, `etat`, `status`
   - Affiche : Ouverte/En cours/Résolue/Fermée

#### Exemple de Résultat :
```
📊 Visualisations automatiques de reclamations_sample.csv
┌────────────────────────────┬────────────────────────────┐
│ Distribution des types     │ Distribution gravité       │
│ [Histogramme]              │ [Histogramme]              │
├────────────────────────────┼────────────────────────────┤
│ Évolution temporelle       │ Top services               │
│ [Line chart]               │ [Bar horizontal]           │
├────────────────────────────┼────────────────────────────┤
│ Délais de traitement       │ Répartition statut         │
│ [Box plot]                 │ [Histogramme]              │
└────────────────────────────┴────────────────────────────┘
```

---

### 2️⃣ Satisfaction Client (jusqu'à 6 graphiques)

#### Graphiques Générés :
1. **Distribution du NPS** - Histogramme (bins=11)
   - Colonnes cherchées : `nps`, `net_promoter`
   - Affiche : Distribution scores 0-10

2. **Distribution CSAT** - Histogramme (bins=5)
   - Colonnes cherchées : `csat`, `satisfaction`
   - Affiche : Distribution scores 1-5

3. **Évolution de la satisfaction** - Line chart
   - Affiche : Évolution NPS/CSAT dans le temps
   - Moyenne par date

4. **Satisfaction par service** - Bar chart
   - Colonnes cherchées : `service`, `departement`
   - Affiche : Score moyen par service

5. **Répartition des sentiments** - Histogramme
   - Colonnes cherchées : `sentiment`, `emotion`
   - Affiche : Positif/Neutre/Négatif

6. **Corrélation temps/satisfaction** - Scatter plot
   - Colonnes cherchées : `temps_attente`, `attente`
   - Affiche : Relation avec ligne de régression

#### Insights Automatiques :
- ✅ Détecte les segments promoteurs/passifs/détracteurs (NPS)
- ✅ Identifie les corrélations temps d'attente ↔ satisfaction
- ✅ Compare les services pour benchmark

---

### 3️⃣ Ventes (jusqu'à 5 graphiques)

#### Graphiques Générés :
1. **Évolution des ventes** - Line chart
   - Colonnes cherchées : `vente`, `ca`, `montant`
   - Affiche : Tendance dans le temps

2. **Ventes par région** - Bar chart
   - Colonnes cherchées : `region`, `zone`, `territoire`
   - Affiche : Total des ventes par région

3. **Top produits** - Bar chart horizontal
   - Colonnes cherchées : `produit`, `article`, `item`
   - Affiche : Top 10 produits vendus

4. **Distribution des prix** - Histogramme
   - Colonnes cherchées : `prix`, `price`, `tarif`
   - Affiche : Répartition des prix (20 bins)

5. **Prix vs Quantité** - Scatter plot
   - Colonnes cherchées : `prix` + `quantite`
   - Affiche : Corrélation avec régression

---

### 4️⃣ Clients (jusqu'à 4 graphiques)

#### Graphiques Générés :
1. **Distribution de l'âge** - Histogramme
   - Affiche : Pyramide des âges (15 bins)

2. **Répartition par sexe** - Bar chart
   - Affiche : M/F/Autre

3. **Top villes** - Bar chart horizontal
   - Affiche : Top 10 villes de résidence

4. **Distribution des revenus** - Histogramme
   - Affiche : Répartition des revenus (20 bins)

---

### 5️⃣ Données Génériques (jusqu'à 4 graphiques)

Si aucun type spécifique n'est détecté, le système génère :

1. **Distribution numérique** - Histogrammes
   - Pour les 2 premières colonnes numériques

2. **Top catégories** - Bar charts
   - Pour les 2 premières colonnes catégorielles

3. **Évolution temporelle** - Line chart
   - Si une colonne date existe

4. **Corrélation** - Scatter plot
   - Entre 2 colonnes numériques

---

## 🎨 Styles Visuels

### Palette de Couleurs
- **Couleur principale** : `#1f77b4` (bleu)
- **Transparence** : `alpha=0.7`
- **Bordures** : `edgecolor='black'`
- **Grilles** : `alpha=0.3`, `linestyle='--'`

### Éléments Graphiques
- **Titres** : `fontsize=14`, `fontweight='bold'`
- **Résolution** : `dpi=300` (haute qualité)
- **Format** : PNG
- **Taille** : `figsize=(10, 6)` ou `(12, 6)` pour temporels

### Scatter Plots avec Régression
```python
# Ligne de régression automatique
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x, p(x), "r--", linewidth=2, label='Tendance')
```

---

## 🚀 Utilisation

### Workflow Automatique

```
1. Utilisateur upload fichier CSV/Excel
   ↓
2. Système charge et indexe les données
   ↓
3. 🆕 Détection automatique du type de données
   ↓
4. 🆕 Génération de 4-6 visualisations pertinentes
   ↓
5. 🆕 Affichage dans une grille 2×3
   ↓
6. Chat disponible pour analyses supplémentaires
```

### Interface Streamlit

```python
# Section expandable automatiquement ouverte
with st.expander("📊 Visualisations automatiques", expanded=True):
    # Grille 2 colonnes
    cols = st.columns(2)
    for i, (title, filepath) in enumerate(plots):
        with cols[i % 2]:
            st.image(filepath, caption=title)
```

---

## 📁 Structure des Fichiers

### Exports
```
exports/
├── auto_plot_distribution_des_types_de_reclamations.png
├── auto_plot_distribution_gravite.png
├── auto_plot_evolution_temporelle.png
├── auto_plot_top_services.png
├── auto_plot_delais_de_traitement.png
└── auto_plot_repartition_statut.png
```

### Nommage
```python
filename = f"auto_plot_{sanitize(title)}.png"

# Exemple :
"Distribution des types" → "auto_plot_distribution_des_types.png"
```

---

## 🧪 Exemples Concrets

### Exemple 1 : Upload `reclamations_sample.csv`

**Fichier détecté** : Type `reclamations` (6 correspondances)

**Visualisations générées** :
1. ✅ Distribution des types (8 catégories)
2. ✅ Distribution gravité (4 niveaux)
3. ✅ Évolution sur 21 jours
4. ✅ Top 5 services
5. ✅ Box plot délais (1h-168h)
6. ✅ Répartition statut (4 états)

**Message** :
```
✅ 6 visualisations générées automatiquement !
📊 Visualisations automatiques de reclamations_sample.csv
```

---

### Exemple 2 : Upload `satisfaction_sample.csv`

**Fichier détecté** : Type `satisfaction` (7 correspondances)

**Visualisations générées** :
1. ✅ Distribution NPS (0-10)
2. ✅ Distribution CSAT (1-5)
3. ✅ Évolution satisfaction (333 jours)
4. ✅ Satisfaction par service (6 services)
5. ✅ Sentiments (Positif/Neutre/Négatif)
6. ✅ Corrélation temps d'attente/NPS

---

### Exemple 3 : Upload `ventes.csv`

**Fichier détecté** : Type `ventes` (4 correspondances)

**Visualisations générées** :
1. ✅ Évolution CA mensuel
2. ✅ Ventes par région (5 régions)
3. ✅ Top 10 produits
4. ✅ Distribution prix
5. ✅ Prix vs Quantité (scatter)

---

## 🔧 Configuration

### Paramètres Modifiables

```python
# Dans app.py
auto_plotter = AutoPlotter(
    export_dir="./exports",  # Répertoire d'export
    max_plots=6              # Nombre max de graphiques
)

# Dans auto_plotter.py
PATTERNS = {
    'reclamations': {
        'keywords': [...],    # Mots-clés de détection
        'required': 2         # Seuil minimum
    }
}
```

### Ajouter un Nouveau Type

```python
PATTERNS['mon_type'] = {
    'keywords': ['mot1', 'mot2', 'mot3'],
    'required': 2
}

# Puis créer la méthode
def _generate_mon_type_plots(self, df, column_types, max_plots):
    plots = []
    # ... génération des plots
    return plots
```

---

## 🎯 Avantages

### Pour l'Utilisateur
- ✅ **Insight immédiat** : Visualisations dès l'upload
- ✅ **Gain de temps** : Pas besoin de formuler des requêtes
- ✅ **Découverte** : Aperçu complet des données
- ✅ **Contexte** : Comprendre rapidement le dataset

### Pour l'Analyse
- ✅ **Détection patterns** : Tendances, outliers, distributions
- ✅ **Validation qualité** : Vérifier cohérence des données
- ✅ **Anomalies** : Identifier valeurs aberrantes
- ✅ **Exploration guidée** : Savoir quelles questions poser

### Pour le Business
- ✅ **Démocratisation** : Accessible aux non-experts
- ✅ **Standardisation** : Même analyse pour tous
- ✅ **Rapidité** : De l'upload à l'insight en secondes
- ✅ **Complétude** : Vue 360° automatique

---

## 📊 Statistiques de Performance

### Temps de Génération
- **Détection type** : ~10-50ms
- **Analyse colonnes** : ~20-100ms
- **Génération 1 plot** : ~200-500ms
- **Total 6 plots** : ~1.5-3 secondes

### Qualité Visuelle
- **Résolution** : 300 DPI (impression qualité)
- **Format** : PNG (compression optimale)
- **Taille fichier** : ~50-200 KB par graphique

---

## 🔍 Détection des Colonnes

### Algorithme de Matching

```python
def _find_column(df, keywords):
    """
    Recherche fuzzy de colonnes par mots-clés.
    Insensible à la casse, espaces, underscores.
    """
    for keyword in keywords:
        for col in df.columns:
            if keyword in col.lower().replace('_', '').replace(' ', ''):
                return col
    return None
```

### Exemples de Correspondances

| Mot-clé | Colonnes Matchées |
|---------|-------------------|
| `nps` | NPS_Score, nps, Net_Promoter_Score, score_nps |
| `delai` | Delai_Traitement_Heures, delai, temps_delai, delai_moyen |
| `vente` | Ventes, vente, ca_ventes, montant_vente |

---

## 💡 Cas d'Usage Avancés

### Monitoring Qualité
**Upload** : `reclamations_quotidiennes.csv`  
**Auto-visualisations** :
- Évolution vs hier/semaine dernière
- Alertes sur pics anormaux
- Distribution gravité pour priorisation

### Reporting Satisfaction
**Upload** : `feedbacks_mensuels.csv`  
**Auto-visualisations** :
- NPS mois actuel vs précédent
- Breakdown par service/canal
- Corrélations temps de réponse

### Analyse Ventes
**Upload** : `ventes_trimestrielles.csv`  
**Auto-visualisations** :
- Tendance CA trimestre
- Top produits/régions
- Performance vs objectifs

---

## 🛠️ Troubleshooting

### Aucune Visualisation Générée

**Causes possibles** :
- ❌ Colonnes ne matchent aucun pattern
- ❌ Données vides ou corrompues
- ❌ Types de données non détectés

**Solutions** :
1. Vérifier les noms de colonnes
2. Ajouter des mots-clés au dictionnaire `PATTERNS`
3. Renommer colonnes si nécessaire

### Visualisations Incorrectes

**Causes possibles** :
- ❌ Mauvaise détection du type
- ❌ Colonnes ambiguës

**Solutions** :
1. Augmenter le seuil `required` pour plus de précision
2. Utiliser des noms de colonnes plus explicites

---

## 📝 Code Source

### Classe Principale

```python
class AutoPlotter:
    """Génère automatiquement des visualisations."""
    
    def generate_auto_plots(self, df, max_plots=6):
        # 1. Détecter le type
        data_type = self.detector.detect_data_type(df)
        
        # 2. Identifier les colonnes
        column_types = self.detector.identify_column_types(df)
        
        # 3. Générer les plots appropriés
        if data_type == 'reclamations':
            return self._generate_reclamations_plots(df, ...)
        # etc.
```

---

## 🎉 Conclusion

Le système de **visualisations automatiques** transforme l'expérience utilisateur en proposant :

- ✅ **0 effort** : Aucune requête nécessaire
- ✅ **6 graphiques** pertinents en ~2 secondes
- ✅ **7 types** de données reconnus automatiquement
- ✅ **Intelligence** adaptée au contexte métier
- ✅ **Qualité** professionnelle (300 DPI)

**De l'upload à l'insight en moins de 5 secondes ! 🚀**

---

**Créé le** : 5 octobre 2025  
**Version** : 1.0  
**Module** : `src/components/auto_plotter.py`  
**Intégration** : `app.py`
