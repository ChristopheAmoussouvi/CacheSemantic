# 🚀 Guide d'Utilisation - Analyse Réclamations & Satisfaction Client

## 📋 Table des Matières
1. [Démarrage Rapide](#démarrage-rapide)
2. [Charger les Données](#charger-les-données)
3. [Exemples de Requêtes](#exemples-de-requêtes)
4. [Visualisations Disponibles](#visualisations-disponibles)
5. [Cas d'Usage Avancés](#cas-dusage-avancés)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Démarrage Rapide

### 1. Lancer l'Application
```bash
# Méthode 1 : Script Windows
start.bat

# Méthode 2 : PowerShell
.\start.ps1

# Méthode 3 : Streamlit direct
streamlit run app.py
```

### 2. Accéder à l'Interface
Ouvrez votre navigateur : **http://localhost:8501**

---

## 📁 Charger les Données

### Fichiers Exemples Disponibles

#### 1️⃣ Réclamations Client
**Fichier** : `data/reclamations_sample.csv`  
**Lignes** : 500  
**Colonnes** : 11

| Colonne | Type | Description |
|---------|------|-------------|
| Date_Reclamation | DateTime | Date et heure de la réclamation |
| ID_Client | Integer | Identifiant unique du client |
| Type_Reclamation | String | Produit défectueux, Livraison, Service, etc. |
| Gravite | String | Faible, Moyenne, Élevée, Critique |
| Service | String | Service concerné (Ventes, Support, etc.) |
| Canal | String | Email, Téléphone, Chat, Courrier, Agence |
| Statut | String | Ouverte, En cours, Résolue, Fermée |
| Delai_Traitement_Heures | Integer | Temps de traitement (1-168h) |
| Resolution_Premier_Contact | Boolean | Résolu au premier contact ? |
| Cout_Traitement | Float | Coût du traitement (10-500€) |
| Satisfaction_Post_Resolution | Float | Score 1-5 après résolution |

#### 2️⃣ Satisfaction Client
**Fichier** : `data/satisfaction_sample.csv`  
**Lignes** : 1000  
**Colonnes** : 14

| Colonne | Type | Description |
|---------|------|-------------|
| Date_Feedback | DateTime | Date du feedback |
| ID_Client | Integer | Identifiant client |
| Type_Interaction | String | Achat, Visite agence, Support, etc. |
| NPS_Score | Integer | Net Promoter Score (0-10) |
| CSAT_Score | Integer | Customer Satisfaction Score (1-5) |
| CES_Score | Integer | Customer Effort Score (1-7) |
| Service_Evalue | String | Service évalué |
| Agent | String | Agent ayant traité |
| Temps_Attente_Minutes | Integer | Temps d'attente (0-60 min) |
| Temps_Resolution_Minutes | Integer | Temps de résolution (5-120 min) |
| Nombre_Contacts | Integer | Nombre de contacts (1-5) |
| Recommanderait | Boolean | Recommanderait le service ? |
| Sentiment | String | Positif, Neutre, Négatif |
| Categorie_Client | String | VIP, Premium, Standard, Nouveau |

### Comment Charger

1. **Dans la barre latérale** (Sidebar) de l'application Streamlit
2. Cliquez sur **"📁 Charger des données"**
3. Sélectionnez le fichier : `reclamations_sample.csv` ou `satisfaction_sample.csv`
4. Attendez la confirmation : ✅ **"Données chargées avec succès"**

---

## 💬 Exemples de Requêtes

### 🔴 Réclamations - Distribution

#### Basique
```
Montre-moi la distribution des types de réclamations
```
**Résultat** : Histogramme avec les 8 types de réclamations

#### Intermédiaire
```
Crée un graphique des réclamations par gravité et par service
```
**Résultat** : Bar chart groupé montrant gravité par service

#### Avancé
```
Affiche la répartition des réclamations avec un focus 
sur les critiques et élevées par canal de contact
```
**Résultat** : Stacked bar chart filtré

---

### 📈 Réclamations - Évolution Temporelle

#### Basique
```
Quelle est l'évolution des réclamations dans le temps ?
```
**Résultat** : Line chart de l'évolution quotidienne/hebdomadaire

#### Intermédiaire
```
Montre-moi la tendance mensuelle des plaintes 
avec distinction par type
```
**Résultat** : Multiple line charts par type

#### Avancé
```
Y a-t-il une saisonnalité dans les réclamations ? 
Compare sur 6 mois avec moyenne mobile
```
**Résultat** : Line chart avec trend line et moyenne mobile

---

### 🏆 Réclamations - Top & Analyse

#### Basique
```
Quels sont les 5 motifs de réclamation les plus fréquents ?
```
**Résultat** : Bar chart horizontal des top 5

#### Intermédiaire
```
Quel service génère le plus de réclamations critiques ?
```
**Résultat** : Analyse filtrée + bar chart

#### Avancé
```
Identifie les patterns récurrents : quels produits 
+ services + canaux génèrent des réclamations critiques répétées ?
```
**Résultat** : Analyse multi-critères + visualisations croisées

---

### ⏱️ Réclamations - Résolution

#### Basique
```
Quel est le délai moyen de traitement ?
```
**Résultat** : KPI + distribution des délais

#### Intermédiaire
```
Compare les temps de résolution par type de réclamation
```
**Résultat** : Box plot comparatif

#### Avancé
```
Analyse la performance : taux de résolution, SLA, 
et corrélation délai/satisfaction post-résolution
```
**Résultat** : Dashboard multi-KPI + scatter plot corrélation

---

### 😊 Satisfaction - Scores

#### Basique
```
Affiche la distribution des scores de satisfaction
```
**Résultat** : Histogramme NPS/CSAT/CES

#### Intermédiaire
```
Quel est le NPS actuel et comment se répartissent 
promoteurs, passifs et détracteurs ?
```
**Résultat** : Gauge chart + stacked bar chart

#### Avancé
```
Crée un dashboard satisfaction : NPS global, 
distribution CSAT par service, et évolution 3 mois
```
**Résultat** : Dashboard multi-panels

---

### 📊 Satisfaction - Évolution

#### Basique
```
Comment évolue la satisfaction client dans le temps ?
```
**Résultat** : Line chart NPS/CSAT temporel

#### Intermédiaire
```
Montre-moi la tendance du NPS sur 12 mois 
avec identification des pics et creux
```
**Résultat** : Line chart annoté avec markers

#### Avancé
```
Analyse l'évolution : tendance globale, variation par service, 
détection d'anomalies, et prévision 3 mois
```
**Résultat** : Multiple line charts + anomaly detection + forecast

---

### 🔄 Satisfaction - Comparaisons

#### Basique
```
Compare la satisfaction entre les différents services
```
**Résultat** : Bar chart comparatif

#### Intermédiaire
```
Quel canal a la meilleure satisfaction ? 
Montre NPS et CSAT par canal
```
**Résultat** : Grouped bar chart multi-métriques

#### Avancé
```
Benchmark complet : satisfaction par service, agent, 
canal et segment client avec ranking
```
**Résultat** : Heatmap + multiple bar charts + tables

---

### 🔍 Corrélations & Insights

#### Basique
```
Y a-t-il un lien entre temps d'attente et satisfaction ?
```
**Résultat** : Scatter plot avec ligne de régression

#### Intermédiaire
```
Analyse l'impact du nombre de contacts sur la satisfaction
```
**Résultat** : Box plot + correlation statistics

#### Avancé
```
Quels facteurs influencent le plus le NPS : temps d'attente, 
temps de résolution, nombre de contacts, ou catégorie client ?
```
**Résultat** : Multiple scatter plots + heatmap + feature importance

---

### 🚨 Alertes & Monitoring

#### Basique
```
Y a-t-il des services avec une baisse de satisfaction ?
```
**Résultat** : Liste + bar chart comparatif période actuelle vs précédente

#### Intermédiaire
```
Identifie les réclamations en hausse anormale et les services en alerte
```
**Résultat** : Anomaly detection + alertes colorées

#### Avancé
```
Dashboard alertes qualité : services critiques, 
tendances négatives, clients à risque, SLA non respecté
```
**Résultat** : Multi-panel alert dashboard avec traffic lights

---

## 🎨 Visualisations Disponibles

### Histogrammes
- **Distribution des types de réclamations**
- **Scores de satisfaction (NPS, CSAT, CES)**
- **Fréquence des gravités**

**Prompt exemple** :
```
Crée un histogramme de la distribution des réclamations par type
```

---

### Bar Charts
- **Top motifs de réclamation**
- **Satisfaction par service**
- **Comparaisons entre groupes**

**Prompt exemple** :
```
Montre-moi un bar chart des 10 principaux motifs de réclamation
```

---

### Line Charts
- **Évolution temporelle des réclamations**
- **Tendance du NPS/CSAT**
- **Séries chronologiques**

**Prompt exemple** :
```
Affiche l'évolution mensuelle de la satisfaction sur 12 mois
```

---

### Scatter Plots
- **Corrélation temps/satisfaction**
- **Relation NPS vs nombre de contacts**
- **Analyse multi-variables**

**Prompt exemple** :
```
Scatter plot : corrélation entre délai de traitement et satisfaction
```

---

### Box Plots
- **Distribution des délais de traitement**
- **Dispersion des scores par service**
- **Identification d'outliers**

**Prompt exemple** :
```
Boxplot des temps de résolution par type de réclamation
```

---

### Heatmaps
- **Corrélations entre variables**
- **Satisfaction par service/période**
- **Matrices de confusion**

**Prompt exemple** :
```
Heatmap des corrélations entre temps d'attente, résolution et satisfaction
```

---

### Stacked Bar Charts
- **Répartition promoteurs/passifs/détracteurs**
- **Statut des réclamations par service**
- **Évolution des sentiments**

**Prompt exemple** :
```
Bar chart empilé : statut des réclamations par service
```

---

### Pie Charts
- **Répartition des canaux de contact**
- **Distribution des sentiments**
- **Parts de marché par service**

**Prompt exemple** :
```
Pie chart de la répartition des canaux de réclamation
```

---

## 💼 Cas d'Usage Avancés

### 📊 Dashboard Manager - Vue d'Ensemble Quotidienne

**Objectif** : Monitoring quotidien de la qualité de service

**Prompts séquentiels** :
```
1. "Dashboard réclamations : volume du jour, top 3 motifs, 
    services en alerte, délai moyen"

2. "Satisfaction du jour : NPS actuel, variation vs hier, 
    top 3 services positifs et négatifs"

3. "Alertes : réclamations critiques non traitées, 
    SLA dépassés, baisses anormales de satisfaction"
```

**Résultat attendu** :
- 3 dashboards complémentaires
- KPI en temps réel
- Alertes actionnables

---

### 🔍 Analyse Root Cause - Baisse de Satisfaction

**Objectif** : Identifier les causes d'une baisse de satisfaction

**Prompts séquentiels** :
```
1. "Évolution du NPS sur 6 mois avec identification des baisses"

2. "Pour le mois avec la plus grosse baisse : 
    quels services, produits, agents sont concernés ?"

3. "Corrélations : cette baisse est-elle liée à une hausse 
    de réclamations, des délais plus longs, ou des changements 
    de processus ?"

4. "Recommendations : actions correctives prioritaires"
```

**Résultat attendu** :
- Identification de la période problématique
- Analyse multi-facteurs
- Plan d'action

---

### 📈 Benchmark Performance Agents

**Objectif** : Évaluer et comparer la performance des agents

**Prompts séquentiels** :
```
1. "Satisfaction moyenne par agent sur 3 mois"

2. "Temps de résolution moyen par agent"

3. "Taux de résolution au premier contact par agent"

4. "Corrélation performance agent et satisfaction client"

5. "Identifie les top performers et les agents nécessitant 
    du support ou de la formation"
```

**Résultat attendu** :
- Ranking des agents
- Identification bonnes pratiques
- Besoins de formation

---

### 🎯 Optimisation SLA

**Objectif** : Améliorer le respect des SLA

**Prompts séquentiels** :
```
1. "Taux de respect du SLA global et par type de réclamation"

2. "Distribution des délais de traitement : 
    où se situent les dépassements ?"

3. "Quels services, types de réclamations, ou canaux 
    génèrent le plus de dépassements SLA ?"

4. "Impact des dépassements SLA sur la satisfaction client"

5. "Recommandations pour améliorer le respect des SLA"
```

**Résultat attendu** :
- Cartographie des dépassements
- Identification goulots d'étranglement
- Plan d'optimisation

---

### 🔮 Prédiction Churn Client

**Objectif** : Identifier les clients à risque de départ

**Prompts séquentiels** :
```
1. "Clients avec satisfaction faible (NPS < 5) et sentiment négatif"

2. "Profil des clients détracteurs : catégorie, historique réclamations, 
    nombre d'interactions"

3. "Corrélation entre nombre de réclamations, délais de résolution, 
    et risque de churn"

4. "Liste priorisée des clients à risque avec actions recommandées"
```

**Résultat attendu** :
- Liste de clients à contacter
- Segmentation par urgence
- Actions de rétention

---

### 📊 Rapport Mensuel Direction

**Objectif** : Préparer le rapport qualité mensuel

**Prompts séquentiels** :
```
1. "KPI du mois : nombre de réclamations, taux de résolution, 
    NPS moyen, CSAT moyen, délai moyen"

2. "Évolution vs mois précédent pour tous les KPI"

3. "Top 5 réussites : services avec amélioration, 
    agents performants, réduction délais"

4. "Top 5 points d'attention : hausses réclamations, 
    baisses satisfaction, dépassements SLA"

5. "Analyse des réclamations : types, gravité, services, 
    avec tendances"

6. "Analyse satisfaction : NPS/CSAT par service, 
    segment client, canal"

7. "Recommandations stratégiques pour le mois prochain"
```

**Résultat attendu** :
- Rapport complet avec visualisations
- Insights actionnables
- Recommandations stratégiques

---

## 🛠️ Troubleshooting

### ❌ Problème : Données non chargées

**Symptôme** : Message "Aucune donnée chargée"

**Solution** :
1. Vérifiez que le fichier CSV existe dans `data/`
2. Utilisez le bouton "📁 Charger des données" dans la sidebar
3. Attendez le message de confirmation

---

### ❌ Problème : Visualisation non générée

**Symptôme** : Message "Aucune visualisation n'a pu être créée"

**Solutions** :
1. **Reformulez la requête** : Soyez plus spécifique
   - ❌ "Montre les données"
   - ✅ "Crée un histogramme des types de réclamations"

2. **Vérifiez les colonnes** : Assurez-vous que les colonnes existent
   ```
   Liste les colonnes disponibles
   ```

3. **Simplifiez** : Décomposez les requêtes complexes
   - ❌ "Montre tout sur les réclamations et la satisfaction"
   - ✅ "Distribution des réclamations" PUIS "Évolution de la satisfaction"

---

### ❌ Problème : Erreur NumPy

**Symptôme** : Warnings NumPy lors du démarrage

**Solution** : Ces warnings sont normaux et n'empêchent pas le fonctionnement
- L'application fonctionne malgré les warnings
- Pour les supprimer : `pip install "numpy<2"` (optionnel)

---

### ❌ Problème : Performance lente

**Symptôme** : Réponses lentes (>30 secondes)

**Solutions** :
1. **Réduire la taille des données** : Filtrez d'abord
   ```
   Filtre les données de janvier uniquement
   ```
   Puis lancez votre analyse

2. **Utiliser le cache** : Répétez une question similaire
   - Le système met en cache les réponses similaires
   - 2ème exécution = quasi-instantanée

3. **Simplifier les visualisations** : 
   - Une visualisation à la fois
   - Évitez les dashboards multi-panels complexes initialement

---

### ❌ Problème : Résultat inattendu

**Symptôme** : La visualisation ne correspond pas à la demande

**Solutions** :
1. **Reformulez** avec plus de détails
   ```
   Avant : "Montre les réclamations"
   Après : "Crée un histogramme montrant la distribution 
            des réclamations par type, avec comptage exact"
   ```

2. **Spécifiez le type de graphique**
   ```
   "Bar chart des top 5 motifs de réclamation"
   "Line chart de l'évolution mensuelle du NPS"
   "Scatter plot délai vs satisfaction"
   ```

3. **Utilisez le contexte des données**
   ```
   "Avec les données de réclamations, montre..."
   "Sur la base du fichier satisfaction, analyse..."
   ```

---

## 📚 Ressources Supplémentaires

### Documentation Complète
- **README.md** : Vue d'ensemble du projet
- **QUICKSTART.md** : Guide de démarrage
- **NOUVEAUX_PROMPTS_RECLAMATIONS_SATISFACTION.md** : Catalogue complet des prompts

### Fichiers Générés
- **generated_prompts/prompts_catalogue_[timestamp].json** : 290 prompts exemples
- **generated_prompts/prompts_index_[timestamp].json** : Index de recherche

### Support
- Consultez les logs dans le terminal pour diagnostiquer les erreurs
- Les visualisations sont exportées dans `exports/` avec timestamp

---

## 🎓 Bonnes Pratiques

### ✅ DO

1. **Soyez spécifique**
   ```
   ✅ "Histogramme des réclamations par gravité avec pourcentages"
   ❌ "Montre les réclamations"
   ```

2. **Une chose à la fois**
   ```
   ✅ 1. "Distribution des types"
      2. "Évolution temporelle"
   ❌ "Montre distribution, évolution, top 5 et corrélations"
   ```

3. **Explorez progressivement**
   ```
   ✅ Vue générale → Analyse détaillée → Insights spécifiques
   ❌ Directement les insights complexes
   ```

4. **Utilisez le contexte**
   ```
   ✅ "Pour les réclamations critiques, montre..."
   ✅ "Parmi les clients VIP, analyse..."
   ```

### ❌ DON'T

1. **Évitez les requêtes trop vagues**
   ```
   ❌ "Analyse tout"
   ❌ "Montre-moi quelque chose d'intéressant"
   ```

2. **N'oubliez pas de charger les données**
   ```
   ❌ Poser des questions avant de charger un fichier
   ✅ Charger d'abord, analyser ensuite
   ```

3. **Ne mélangez pas les datasets**
   ```
   ❌ "Compare réclamations et ventes" (si datasets différents)
   ✅ Analysez un dataset à la fois
   ```

---

## 🎉 Conclusion

Avec ces **290 prompts** et **14 nouvelles catégories**, vous disposez d'un outil puissant pour :

- 📊 **Monitorer** la qualité de service en temps réel
- 🔍 **Analyser** les réclamations et identifier les causes
- 😊 **Mesurer** la satisfaction client (NPS, CSAT, CES)
- 🎯 **Optimiser** les processus et les SLA
- 🚨 **Détecter** les anomalies et alertes
- 💼 **Prendre** des décisions data-driven

**Bon pilotage de votre qualité de service !** 🚀

---

**Dernière mise à jour** : 3 octobre 2025  
**Version** : 1.0  
**Contact** : AI Data Interaction Agent
