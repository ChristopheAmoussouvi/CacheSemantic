# 🚀 Guide de Démarrage Rapide - Nouvelles Fonctionnalités

## 🧪 Données Test et Prompts d'Exemples

L'application dispose maintenant de fonctionnalités avancées pour tester rapidement les capacités de visualisation et d'analyse.

### 📊 Générateur de Données Test

#### Types de données disponibles :
1. **📈 Données de Ventes** - 1000 enregistrements
   - Colonnes : date, région, produit, vendeur, quantité, prix_unitaire, chiffre_affaires
   - Parfait pour : analyses temporelles, comparaisons régionales, performance des vendeurs

2. **👥 Données Clients** - 500 enregistrements  
   - Colonnes : client_id, nom_complet, âge, sexe, ville, salaire_annuel, score_satisfaction, nb_commandes, valeur_client
   - Parfait pour : segmentation client, analyses démographiques, satisfaction

3. **💰 Données Financières** - 200 enregistrements mensuels
   - Colonnes : date, chiffre_affaires, coûts, bénéfice, marge, trimestre
   - Parfait pour : tableaux de bord financiers, analyses de tendances

4. **📋 Enquête de Satisfaction** - 300 réponses
   - Colonnes : répondant_id, service_évalué, tranche_âge, note_satisfaction, recommandation, date_réponse
   - Parfait pour : analyses de satisfaction, NPS, feedback clients

#### Comment utiliser :
1. Dans la sidebar, section "🧪 Données Test"
2. Sélectionner un type de dataset
3. Cliquer sur "📊 Générer et Charger"
4. Les données sont automatiquement chargées et prêtes à analyser

### 💬 Collection de Prompts d'Exemples

#### 42 prompts organisés en 6 catégories :

**📊 Analyses de Ventes (7 prompts)**
- Vue d'ensemble, graphiques par région, évolution temporelle
- Performance vendeurs, saisonnalité, corrélations

**👥 Analyses Clients (7 prompts)**  
- Profils clients, répartition par âge, satisfaction
- Segmentation, relations démographiques

**💰 Analyses Financières (7 prompts)**
- Tableaux de bord, évolution bénéfices, marges
- Comparaisons trimestrielles, prévisions

**📋 Analyses d'Enquêtes (7 prompts)**
- Satisfaction globale, par service, par âge
- Recommandations, services à améliorer

**🔍 Analyses Exploratoires (7 prompts)**
- Statistiques descriptives, anomalies, corrélations
- Distributions, patterns cachés, clustering

**📈 Visualisations Avancées (7 prompts)**
- Graphiques complexes : aires empilées, heatmaps, radar
- Diagrammes violons, Sankey, bubble charts

#### Comment utiliser :
1. Développer la section "💡 Prompts d'Exemples"
2. Choisir une catégorie dans le menu déroulant
3. Cliquer sur un bouton de prompt pour l'utiliser automatiquement
4. Ou utiliser les "Prompts Rapides" pour des analyses basiques

### 🎯 Workflow Recommandé

#### Pour débuter :
1. **Générer des données test** → Choisir "Données de Ventes"
2. **Utiliser un prompt rapide** → Cliquer "📊 Résumé"
3. **Explorer les visualisations** → Essayer "Crée un graphique intéressant"

#### Pour des analyses avancées :
1. **Charger vos propres données** (CSV/Excel)
2. **Utiliser les prompts spécialisés** selon votre domaine
3. **Combiner plusieurs analyses** avec des prompts différents

### 🏠 Mode 100% Local

#### Avantages :
- ✅ **Confidentialité totale** : Aucune donnée envoyée à l'extérieur
- ✅ **Rapidité** : Pas de latence réseau
- ✅ **Coût** : Aucun frais d'API
- ✅ **Fiabilité** : Fonctionne sans connexion internet

#### Architecture :
- **Chatbot** : Arbre de décision déterministe
- **Cache** : Système de cache simple pour optimiser les réponses
- **Visualisations** : Seaborn/Matplotlib avec export PNG
- **Stockage** : ChromaDB local pour persistance

### 🛠 Résolution de Problèmes

#### Si vous voyez des avertissements NumPy :
- **Normal** : Problème de compatibilité connu
- **Solution** : L'application fonctionne malgré ces avertissements
- **Alternative** : Installer `numpy<2.0.0` si nécessaire

#### Si un dataset ne se charge pas :
1. Vérifier que le répertoire `./data` existe
2. Essayer un autre type de dataset
3. Redémarrer l'application si nécessaire

### 📈 Exemples d'Usage

#### Analyse rapide de ventes :
```
1. Générer "Données de Ventes"
2. Prompt: "Montre-moi un résumé des données de ventes"
3. Suivre avec: "Crée un graphique des ventes par région"
4. Analyser avec: "Quelle est la tendance du chiffre d'affaires ?"
```

#### Tableau de bord financier :
```
1. Générer "Données Financières"  
2. Prompt: "Crée un tableau de bord des indicateurs financiers"
3. Approfondir: "Comment évolue notre marge bénéficiaire ?"
4. Comparer: "Compare les performances par trimestre"
```

### 🎨 Personnalisation

Les prompts et types de données peuvent être facilement étendus en modifiant :
- `src/utils/example_prompts.py` pour ajouter des prompts
- `src/utils/data_generator.py` pour créer de nouveaux types de données

---

**Prêt à explorer vos données ? Lancez l'application et commencez par générer un dataset test !** 🚀