"""
Script simple pour générer et stocker rapidement des prompts/réponses.
Version automatique sans interaction utilisateur.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

def generate_quick_prompts_batch():
    """Génère rapidement un batch de 200+ prompts variés."""
    
    print("=" * 70)
    print("⚡ GÉNÉRATION RAPIDE DE PROMPTS POUR CHROMADB")
    print("=" * 70)
    
    # Catégories de prompts avec variations
    prompts_database = {
        'resume_general': [
            "Résume les données",
            "Donne-moi un aperçu",
            "Montre-moi les statistiques principales",
            "Quelles données avons-nous ?",
            "Affiche un overview",
            "Présente les informations disponibles",
            "Décris les données chargées",
            "Combien de lignes et colonnes ?",
            "Quels types de données ?",
            "Y a-t-il des valeurs manquantes ?"
        ],
        
        'visualisation_distribution': [
            "Crée un histogramme des ventes",
            "Montre la distribution des prix",
            "Affiche la répartition des quantités",
            "Fais un graphique de distribution",
            "Visualise les fréquences",
            "Histogramme des scores",
            "Distribution par catégorie",
            "Répartition des valeurs",
            "Graphique de densité",
            "Montre les distributions"
        ],
        
        'visualisation_correlation': [
            "Corrélation entre prix et ventes",
            "Scatter plot prix vs quantité",
            "Relation entre deux variables",
            "Nuage de points ventes/budget",
            "Y a-t-il un lien entre X et Y ?",
            "Montre la relation entre variables",
            "Affiche les corrélations",
            "Crée un scatter des données",
            "Visualise les dépendances",
            "Graphique de corrélation"
        ],
        
        'visualisation_comparaison': [
            "Ventes par région",
            "Compare les performances entre groupes",
            "Graphique des moyennes par catégorie",
            "Affiche les totaux par mois",
            "Ventes par vendeur",
            "Revenus par département",
            "Bar chart des ventes",
            "Compare les régions",
            "Performance par équipe",
            "Totaux par segment"
        ],
        
        'visualisation_temporelle': [
            "Évolution des ventes dans le temps",
            "Tendance des prix",
            "Courbe temporelle",
            "Progression mensuelle",
            "Évolution annuelle",
            "Tendance sur 6 mois",
            "Line chart temporel",
            "Série chronologique",
            "Graphique d'évolution",
            "Analyse temporelle"
        ],
        
        'visualisation_matrice': [
            "Heatmap des corrélations",
            "Matrice de corrélation",
            "Relations entre toutes les variables",
            "Carte de chaleur",
            "Corrélations multiples",
            "Visualisation matricielle",
            "Heatmap complète",
            "Toutes les corrélations",
            "Matrice de covariance",
            "Graphique de corrélation multiple"
        ],
        
        'visualisation_dispersion': [
            "Boxplot des ventes",
            "Distribution avec outliers",
            "Quartiles des prix",
            "Valeurs aberrantes",
            "Dispersion des données",
            "Boîte à moustaches",
            "Analyse des outliers",
            "Graphique de dispersion",
            "Distribution statistique",
            "Variabilité des données"
        ],
        
        'analyse_statistiques': [
            "Moyenne des ventes",
            "Médiane des prix",
            "Total des quantités",
            "Écart-type",
            "Variance",
            "Percentiles",
            "Statistiques descriptives",
            "Valeurs min et max",
            "Amplitude des données",
            "Coefficient de variation"
        ],
        
        'analyse_top': [
            "Top 5 produits",
            "Meilleurs vendeurs",
            "Meilleures régions",
            "Produits les plus vendus",
            "Top performers",
            "Classement des ventes",
            "Top 10 clients",
            "Meilleures performances",
            "Ranking par ventes",
            "Leaders du marché"
        ],
        
        'analyse_filtres': [
            "Ventes supérieures à 1000",
            "Filtre région Nord",
            "Données de janvier",
            "Scores supérieurs à 80",
            "Prix entre 50 et 100",
            "Sélectionne catégorie A",
            "Filtre par vendeur",
            "Données récentes",
            "Valeurs positives uniquement",
            "Période spécifique"
        ],
        
        'analyse_comparaison': [
            "Compare Nord et Sud",
            "Quelle région performe mieux ?",
            "Différence entre A et B",
            "Comparaison temporelle",
            "Avant vs après",
            "Groupe 1 vs Groupe 2",
            "Performance relative",
            "Écart entre régions",
            "Meilleur que la moyenne ?",
            "Qui est en tête ?"
        ],
        
        'analyse_tendances': [
            "Tendance des ventes",
            "Croissance ou décroissance ?",
            "Y a-t-il une saisonnalité ?",
            "Performance s'améliore ?",
            "Évolution sur 6 mois",
            "Ventes en hausse ?",
            "Tendance baissière ?",
            "Cycles dans les données",
            "Trajectoire future",
            "Pattern temporel"
        ],
        
        'analyse_agrégation': [
            "Somme par groupe",
            "Moyenne par catégorie",
            "Total par région",
            "Agrégation mensuelle",
            "Groupement par segment",
            "Consolidation des données",
            "Résumé par période",
            "Totaux par type",
            "Moyennes groupées",
            "Agrégation temporelle"
        ],
        
        'questions_specifiques': [
            "Quel est le chiffre d'affaires ?",
            "Combien de clients avons-nous ?",
            "Quelle est la marge moyenne ?",
            "Volume total des ventes ?",
            "Taux de satisfaction ?",
            "Budget disponible ?",
            "Revenus du mois ?",
            "Performance globale ?",
            "Objectifs atteints ?",
            "ROI actuel ?"
        ],
        
        'questions_business': [
            "Quelle stratégie recommandes-tu ?",
            "Où investir en priorité ?",
            "Quels produits développer ?",
            "Quelles régions cibler ?",
            "Opportunités de croissance ?",
            "Points d'amélioration ?",
            "Risques identifiés ?",
            "Forces et faiblesses ?",
            "Plan d'action ?",
            "KPI à surveiller ?"
        ],
        
        # 🆕 RÉCLAMATIONS & SATISFACTION CLIENT
        'reclamations_distribution': [
            "Distribution des types de réclamations",
            "Histogramme des réclamations par catégorie",
            "Répartition des motifs de plainte",
            "Fréquence des réclamations par type",
            "Graphique des catégories de réclamations",
            "Distribution des réclamations par gravité",
            "Répartition des incidents par service",
            "Histogramme des réclamations mensuelles",
            "Distribution des délais de traitement",
            "Fréquence des réclamations par canal"
        ],
        
        'reclamations_temporelles': [
            "Évolution des réclamations dans le temps",
            "Tendance mensuelle des plaintes",
            "Courbe des réclamations sur 6 mois",
            "Progression des incidents par semaine",
            "Série temporelle des réclamations",
            "Évolution du volume de plaintes",
            "Tendance des réclamations critiques",
            "Graphique d'évolution des incidents",
            "Analyse temporelle des réclamations",
            "Saisonnalité des plaintes clients"
        ],
        
        'reclamations_analyse': [
            "Top 5 motifs de réclamation",
            "Principales causes de plaintes",
            "Réclamations les plus fréquentes",
            "Services avec le plus de réclamations",
            "Produits générant le plus de plaintes",
            "Catégories de réclamations prioritaires",
            "Points de friction majeurs",
            "Incidents critiques récurrents",
            "Taux de réclamations par service",
            "Analyse des réclamations non résolues"
        ],
        
        'reclamations_resolution': [
            "Taux de résolution des réclamations",
            "Délai moyen de traitement",
            "Temps de résolution par type",
            "Performance de résolution par équipe",
            "Réclamations résolues vs en attente",
            "Comparaison des délais de traitement",
            "Efficacité du service réclamation",
            "Graphique de résolution par gravité",
            "SLA respecté pour les réclamations",
            "Évolution du taux de résolution"
        ],
        
        'satisfaction_scores': [
            "Distribution des scores de satisfaction",
            "Histogramme des notes clients",
            "Répartition des NPS (Net Promoter Score)",
            "Distribution des évaluations",
            "Graphique des scores CSAT",
            "Fréquence des notes de 1 à 5",
            "Répartition promoteurs/détracteurs",
            "Distribution des feedbacks positifs/négatifs",
            "Scores de satisfaction par service",
            "Histogramme des évaluations clients"
        ],
        
        'satisfaction_temporelle': [
            "Évolution de la satisfaction client",
            "Tendance du NPS dans le temps",
            "Progression des scores mensuels",
            "Courbe de satisfaction sur 12 mois",
            "Évolution du CSAT par trimestre",
            "Tendance des avis clients",
            "Série temporelle de satisfaction",
            "Amélioration de la satisfaction",
            "Graphique d'évolution du NPS",
            "Saisonnalité de la satisfaction"
        ],
        
        'satisfaction_comparative': [
            "Satisfaction par service",
            "Comparaison NPS entre agences",
            "Scores par catégorie de produit",
            "Satisfaction par canal de contact",
            "Comparaison avant/après amélioration",
            "Performance par équipe service client",
            "Satisfaction par segment de clientèle",
            "Benchmark des services",
            "Comparaison régionale de satisfaction",
            "Scores par point de contact"
        ],
        
        'satisfaction_correlation': [
            "Corrélation satisfaction et délai de réponse",
            "Relation entre NPS et réclamations",
            "Lien satisfaction et temps d'attente",
            "Impact du nombre de contacts sur satisfaction",
            "Corrélation score et résolution premier contact",
            "Relation entre CSAT et ancienneté client",
            "Scatter plot satisfaction vs qualité service",
            "Corrélation entre canaux et satisfaction",
            "Lien entre formation agents et NPS",
            "Impact prix sur satisfaction"
        ],
        
        'satisfaction_sentiments': [
            "Analyse des sentiments clients",
            "Répartition positif/négatif/neutre",
            "Distribution des émotions dans feedbacks",
            "Mots-clés des avis négatifs",
            "Thématiques dans commentaires positifs",
            "Analyse textuelle des verbatims",
            "Nuage de mots des réclamations",
            "Sentiments par catégorie de service",
            "Évolution du sentiment client",
            "Analyse sémantique des retours"
        ],
        
        'kpi_reclamations': [
            "Taux de réclamations global",
            "Pourcentage de réclamations critiques",
            "Volume moyen mensuel de plaintes",
            "Ratio réclamations/clients",
            "Taux de récurrence des réclamations",
            "Coût moyen d'une réclamation",
            "Taux d'escalade des incidents",
            "Délai moyen de première réponse",
            "Taux de satisfaction post-résolution",
            "Pourcentage SLA respecté"
        ],
        
        'kpi_satisfaction': [
            "Score NPS actuel",
            "Moyenne CSAT sur 3 mois",
            "Taux de recommandation",
            "Pourcentage de promoteurs",
            "Pourcentage de détracteurs",
            "Score CES (Customer Effort Score)",
            "Taux de rétention client",
            "Taux de réponse aux enquêtes",
            "Satisfaction globale par canal",
            "Indice de fidélité client"
        ],
        
        'alertes_qualite': [
            "Réclamations en hausse anormale",
            "Services avec baisse de satisfaction",
            "Alertes sur délais de traitement",
            "Détection d'anomalies dans NPS",
            "Produits avec explosion de plaintes",
            "Canaux performant sous la moyenne",
            "Équipes nécessitant support",
            "Réclamations non traitées urgentes",
            "Clients à risque de churn",
            "Tendances négatives émergentes"
        ],
        
        'tableaux_bord': [
            "Dashboard qualité de service",
            "Vue d'ensemble réclamations/satisfaction",
            "Tableau de bord service client",
            "KPI réclamations consolidés",
            "Synthèse satisfaction client",
            "Rapport hebdomadaire qualité",
            "Indicateurs clés de performance",
            "Vue 360° expérience client",
            "Monitoring temps réel réclamations",
            "Scorecard satisfaction globale"
        ],
        
        'actions_correctives': [
            "Recommandations d'amélioration",
            "Plans d'action pour services critiques",
            "Priorisation des corrections",
            "Opportunités d'amélioration identifiées",
            "Actions pour réduire réclamations",
            "Stratégies d'amélioration satisfaction",
            "Formation nécessaire pour équipes",
            "Processus à optimiser",
            "Investissements prioritaires qualité",
            "Roadmap amélioration expérience client"
        ]
    }
    
    # Générer toutes les variations
    all_prompts = []
    for category, prompts in prompts_database.items():
        for prompt in prompts:
            all_prompts.append({
                'category': category,
                'prompt': prompt,
                'dataset': np.random.choice(['ventes', 'clients', 'finances'])
            })
    
    print(f"\n✅ {len(all_prompts)} prompts générés")
    print(f"📊 {len(prompts_database)} catégories")
    
    # Sauvegarder dans un fichier
    output_dir = Path("generated_prompts")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"prompts_catalogue_{timestamp}.json"
    
    catalogue = {
        'metadata': {
            'total_prompts': len(all_prompts),
            'categories': len(prompts_database),
            'generated_at': datetime.now().isoformat(),
            'version': '1.0'
        },
        'categories': list(prompts_database.keys()),
        'prompts': all_prompts
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(catalogue, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Catalogue sauvegardé: {output_file}")
    
    # Statistiques par catégorie
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES PAR CATÉGORIE")
    print("=" * 70)
    
    for category in prompts_database.keys():
        count = sum(1 for p in all_prompts if p['category'] == category)
        print(f"  • {category:30s}: {count:3d} prompts")
    
    # Statistiques par dataset
    print("\n📂 RÉPARTITION PAR DATASET")
    print("=" * 70)
    
    for dataset in ['ventes', 'clients', 'finances']:
        count = sum(1 for p in all_prompts if p['dataset'] == dataset)
        percentage = count / len(all_prompts) * 100
        print(f"  • {dataset:15s}: {count:3d} prompts ({percentage:.1f}%)")
    
    print("\n" + "=" * 70)
    print("🎉 GÉNÉRATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 70)
    
    return catalogue

def create_indexed_catalogue():
    """Crée un catalogue indexé pour recherche rapide."""
    
    print("\n📚 Création d'index pour recherche rapide...")
    
    catalogue = generate_quick_prompts_batch()
    
    # Créer des index
    indices = {
        'by_category': {},
        'by_dataset': {},
        'by_keywords': {}
    }
    
    # Index par catégorie
    for prompt_data in catalogue['prompts']:
        category = prompt_data['category']
        if category not in indices['by_category']:
            indices['by_category'][category] = []
        indices['by_category'][category].append(prompt_data['prompt'])
    
    # Index par dataset
    for prompt_data in catalogue['prompts']:
        dataset = prompt_data['dataset']
        if dataset not in indices['by_dataset']:
            indices['by_dataset'][dataset] = []
        indices['by_dataset'][dataset].append(prompt_data['prompt'])
    
    # Index par mots-clés
    keywords = ['ventes', 'prix', 'région', 'temps', 'corrélation', 
                'graphique', 'moyenne', 'total', 'tendance', 'compare']
    
    for keyword in keywords:
        indices['by_keywords'][keyword] = []
        for prompt_data in catalogue['prompts']:
            if keyword.lower() in prompt_data['prompt'].lower():
                indices['by_keywords'][keyword].append(prompt_data['prompt'])
    
    # Sauvegarder les index
    output_dir = Path("generated_prompts")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    index_file = output_dir / f"prompts_index_{timestamp}.json"
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(indices, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Index créé: {index_file}")
    print(f"   • Catégories indexées: {len(indices['by_category'])}")
    print(f"   • Datasets indexés: {len(indices['by_dataset'])}")
    print(f"   • Mots-clés indexés: {len(indices['by_keywords'])}")
    
    return indices

if __name__ == "__main__":
    # Génération simple
    catalogue = generate_quick_prompts_batch()
    
    # Création des index
    print("\n")
    indices = create_indexed_catalogue()
    
    print("\n" + "=" * 70)
    print("✨ RÉSUMÉ FINAL")
    print("=" * 70)
    print(f"📊 Total de prompts générés: {catalogue['metadata']['total_prompts']}")
    print(f"📂 Catégories: {catalogue['metadata']['categories']}")
    print(f"🗂️  Index créés: {len(indices)}")
    print(f"📁 Fichiers dans: generated_prompts/")
    print("=" * 70)
