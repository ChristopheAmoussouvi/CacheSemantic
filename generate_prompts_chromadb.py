"""
Générateur de prompts et réponses pour le chat de visualisation de données.
Crée des paires question-réponse stockées dans ChromaDB pour améliorer le système.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import json
from datetime import datetime
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from src.components.data_manager import DataManager
from src.components.ai_agent import LocalAIAgent
from src.components.simple_cache import SimpleCache

class PromptResponseGenerator:
    """Génère des prompts et réponses pour enrichir ChromaDB."""
    
    def __init__(self):
        """Initialise le générateur."""
        self.data_manager = DataManager(db_path="./chroma_db")
        self.simple_cache = SimpleCache(cache_dir="./cache")
        self.ai_agent = LocalAIAgent(
            data_manager=self.data_manager,
            simple_cache=self.simple_cache
        )
        
        # Catégories de prompts
        self.prompt_categories = {
            'resume': self._generate_summary_prompts,
            'visualisation': self._generate_visualization_prompts,
            'analyse': self._generate_analysis_prompts,
            'filtres': self._generate_filter_prompts,
            'statistiques': self._generate_statistics_prompts,
            'comparaison': self._generate_comparison_prompts,
            'tendances': self._generate_trend_prompts,
            'reclamations': self._generate_reclamations_prompts,
            'satisfaction': self._generate_satisfaction_prompts
        }
    
    def _generate_summary_prompts(self) -> List[str]:
        """Génère des prompts pour les résumés de données."""
        return [
            "Donne-moi un résumé des données",
            "Peux-tu me montrer un aperçu général ?",
            "Quelles sont les statistiques principales ?",
            "Affiche-moi les informations sur les données",
            "Montre-moi un overview des données disponibles",
            "Résume les colonnes et leur contenu",
            "Quelles données avons-nous ?",
            "Décris-moi les données chargées",
            "Présente-moi un aperçu statistique",
            "Combien de lignes et de colonnes avons-nous ?",
            "Quelles sont les variables disponibles ?",
            "Montre-moi les types de données",
            "Y a-t-il des valeurs manquantes ?",
            "Quel est le volume de données ?",
            "Fais-moi une description générale"
        ]
    
    def _generate_visualization_prompts(self) -> List[str]:
        """Génère des prompts pour les visualisations."""
        return [
            # Histogrammes
            "Crée un histogramme des ventes",
            "Montre-moi la distribution des prix",
            "Visualise la répartition des quantités",
            "Affiche un graphique de distribution des scores",
            "Fais un histogram des valeurs",
            
            # Scatter plots
            "Montre la corrélation entre prix et ventes",
            "Crée un scatter plot prix vs quantité",
            "Y a-t-il une relation entre score et performance ?",
            "Affiche le nuage de points ventes/budget",
            "Visualise la relation entre deux variables",
            
            # Bar charts
            "Quelles sont les ventes par région ?",
            "Montre-moi un graphique des ventes par catégorie",
            "Compare les performances entre les régions",
            "Affiche les moyennes par groupe",
            "Crée un bar chart des totaux par mois",
            "Visualise les ventes par vendeur",
            "Montre les revenus par département",
            
            # Line charts
            "Comment évoluent les ventes dans le temps ?",
            "Montre-moi la tendance des prix",
            "Affiche l'évolution temporelle des quantités",
            "Trace la courbe des ventes mensuelles",
            "Visualise la progression des scores",
            "Quelle est la tendance sur l'année ?",
            
            # Heatmaps
            "Montre-moi une heatmap des corrélations",
            "Crée une matrice de corrélation",
            "Affiche les relations entre toutes les variables",
            "Visualise les corrélations entre colonnes",
            "Quelles variables sont corrélées ?",
            
            # Boxplots
            "Crée un boxplot des ventes",
            "Montre-moi la distribution avec outliers",
            "Affiche les quartiles des prix",
            "Y a-t-il des valeurs aberrantes ?",
            "Visualise la dispersion des données"
        ]
    
    def _generate_analysis_prompts(self) -> List[str]:
        """Génère des prompts pour les analyses."""
        return [
            "Quelle est la moyenne des ventes ?",
            "Calcule la médiane des prix",
            "Quel est le total des quantités vendues ?",
            "Quelle région a les meilleures performances ?",
            "Qui est le meilleur vendeur ?",
            "Quel produit se vend le mieux ?",
            "Quelle est la variance des scores ?",
            "Calcule l'écart-type des ventes",
            "Quelle est la somme totale des revenus ?",
            "Quel est le chiffre d'affaires moyen ?",
            "Identifie les top 5 produits",
            "Quels sont les 3 meilleures régions ?",
            "Calcule le taux de croissance",
            "Quelle est la performance globale ?",
            "Analyse les données par segment"
        ]
    
    def _generate_filter_prompts(self) -> List[str]:
        """Génère des prompts pour les filtres."""
        return [
            "Montre-moi uniquement les ventes supérieures à 1000",
            "Filtre les données pour la région Nord",
            "Affiche seulement les produits de catégorie A",
            "Sélectionne les ventes de janvier",
            "Montre les scores supérieurs à 80",
            "Filtre par vendeur Martin",
            "Affiche les données du trimestre 1",
            "Sélectionne les prix entre 50 et 100",
            "Montre uniquement les valeurs positives",
            "Filtre les données récentes"
        ]
    
    def _generate_statistics_prompts(self) -> List[str]:
        """Génère des prompts pour les statistiques."""
        return [
            "Quelle est la distribution des ventes ?",
            "Calcule les percentiles des prix",
            "Montre-moi les statistiques descriptives",
            "Quelle est l'amplitude des données ?",
            "Y a-t-il une asymétrie dans les distributions ?",
            "Calcule le coefficient de variation",
            "Quelle est la fréquence de chaque catégorie ?",
            "Montre-moi les valeurs min et max",
            "Quelle est l'étendue des données ?",
            "Calcule le coefficient de corrélation"
        ]
    
    def _generate_comparison_prompts(self) -> List[str]:
        """Génère des prompts pour les comparaisons."""
        return [
            "Compare les ventes entre Nord et Sud",
            "Quelle région performe mieux ?",
            "Compare les prix de 2024 vs 2025",
            "Qui vend plus : Martin ou Dupont ?",
            "Compare les performances par trimestre",
            "Quelle catégorie est la plus rentable ?",
            "Compare les moyennes par groupe",
            "Quelle période a les meilleures ventes ?",
            "Compare les distributions entre segments",
            "Quelle est la différence entre A et B ?"
        ]
    
    def _generate_trend_prompts(self) -> List[str]:
        """Génère des prompts pour les tendances."""
        return [
            "Quelle est la tendance des ventes ?",
            "Les prix augmentent-ils ou diminuent-ils ?",
            "Y a-t-il une saisonnalité dans les données ?",
            "Observe-t-on une croissance ?",
            "La performance s'améliore-t-elle ?",
            "Quelle est l'évolution sur 6 mois ?",
            "Les ventes sont-elles en hausse ?",
            "Détecte-t-on une tendance baissière ?",
            "Y a-t-il des cycles dans les données ?",
            "Quelle est la trajectoire future probable ?"
        ]
    
    def _generate_reclamations_prompts(self) -> List[str]:
        """Génère des prompts pour l'analyse de réclamations."""
        return [
            # Distribution et types
            "Montre-moi la distribution des types de réclamations",
            "Crée un histogramme des réclamations par catégorie",
            "Quelle est la répartition des motifs de plainte ?",
            "Affiche un graphique des réclamations par gravité",
            "Visualise la fréquence des réclamations par service",
            
            # Tendances temporelles
            "Quelle est l'évolution des réclamations dans le temps ?",
            "Montre-moi la tendance mensuelle des plaintes",
            "Y a-t-il une saisonnalité dans les réclamations ?",
            "Compare les réclamations sur 6 mois",
            "Affiche la courbe d'évolution des incidents",
            
            # Analyse et top
            "Quels sont les 5 motifs de réclamation les plus fréquents ?",
            "Quel service génère le plus de réclamations ?",
            "Quels produits ont le plus de plaintes ?",
            "Identifie les principales causes de réclamation",
            "Quelles sont les réclamations critiques récurrentes ?",
            
            # Résolution et performance
            "Quel est le taux de résolution des réclamations ?",
            "Calcule le délai moyen de traitement",
            "Combien de réclamations sont en attente ?",
            "Montre le temps de résolution par type",
            "Quelle équipe résout le plus vite les réclamations ?",
            "Est-ce que le SLA est respecté ?",
            
            # Corrélations
            "Y a-t-il un lien entre délai et satisfaction ?",
            "Corrélation entre type de réclamation et résolution",
            "Relation entre canal de contact et réclamations"
        ]
    
    def _generate_satisfaction_prompts(self) -> List[str]:
        """Génère des prompts pour l'analyse de satisfaction client."""
        return [
            # Scores et distribution
            "Affiche la distribution des scores de satisfaction",
            "Crée un histogramme des notes clients",
            "Quelle est la répartition du NPS ?",
            "Montre-moi les scores CSAT par service",
            "Visualise la distribution des évaluations",
            "Combien de promoteurs vs détracteurs ?",
            
            # Évolution temporelle
            "Comment évolue la satisfaction client dans le temps ?",
            "Montre-moi la tendance du NPS sur 12 mois",
            "La satisfaction s'améliore-t-elle ?",
            "Affiche l'évolution du CSAT par trimestre",
            "Y a-t-il des cycles dans la satisfaction ?",
            
            # Comparaisons
            "Compare la satisfaction entre services",
            "Quel canal a la meilleure satisfaction ?",
            "Satisfaction par segment de clientèle",
            "Compare les scores avant et après amélioration",
            "Quelle agence a le meilleur NPS ?",
            "Performance de satisfaction par équipe",
            
            # Corrélations et insights
            "Corrélation entre temps d'attente et satisfaction",
            "Lien entre satisfaction et fidélité client",
            "Impact du nombre de contacts sur la satisfaction",
            "Relation entre prix et satisfaction",
            "Quels facteurs influencent le plus le NPS ?",
            
            # KPI et alertes
            "Quel est le score NPS actuel ?",
            "Quelle est la moyenne CSAT ?",
            "Taux de recommandation client ?",
            "Y a-t-il des services en alerte satisfaction ?",
            "Identifie les baisses anormales de satisfaction",
            "Quels clients sont à risque de churn ?"
        ]
    
    def generate_all_prompts(self) -> Dict[str, List[str]]:
        """Génère tous les prompts par catégorie."""
        all_prompts = {}
        for category, generator in self.prompt_categories.items():
            all_prompts[category] = generator()
        return all_prompts
    
    def create_sample_datasets(self) -> Dict[str, pd.DataFrame]:
        """Crée des datasets d'exemple pour tester les prompts."""
        np.random.seed(42)
        
        datasets = {}
        
        # Dataset 1: Ventes
        datasets['ventes'] = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=365, freq='D'),
            'Region': np.random.choice(['Nord', 'Sud', 'Est', 'Ouest', 'Centre'], 365),
            'Vendeur': np.random.choice(['Martin', 'Dupont', 'Bernard', 'Dubois', 'Leroy'], 365),
            'Produit': np.random.choice(['Produit A', 'Produit B', 'Produit C', 'Produit D'], 365),
            'Categorie': np.random.choice(['Cat1', 'Cat2', 'Cat3'], 365),
            'Ventes': np.random.randint(500, 5000, 365),
            'Quantite': np.random.randint(1, 100, 365),
            'Prix': np.random.uniform(10, 200, 365),
            'Score': np.random.uniform(0, 100, 365)
        })
        
        # Dataset 2: Clients
        datasets['clients'] = pd.DataFrame({
            'ID': range(1, 201),
            'Age': np.random.randint(18, 80, 200),
            'Sexe': np.random.choice(['M', 'F'], 200),
            'Ville': np.random.choice(['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'], 200),
            'Revenus': np.random.randint(20000, 100000, 200),
            'Satisfaction': np.random.uniform(1, 5, 200),
            'Anciennete': np.random.randint(0, 20, 200),
            'Achats_Total': np.random.randint(0, 50000, 200)
        })
        
        # Dataset 3: Finances
        datasets['finances'] = pd.DataFrame({
            'Mois': pd.date_range('2024-01-01', periods=12, freq='MS'),
            'Revenus': np.random.randint(50000, 150000, 12),
            'Depenses': np.random.randint(30000, 100000, 12),
            'Marge': np.random.uniform(0.1, 0.4, 12),
            'Budget': np.random.randint(40000, 120000, 12),
            'CA': np.random.randint(60000, 180000, 12)
        })
        
        # Dataset 4: Réclamations
        n_reclamations = 500
        datasets['reclamations'] = pd.DataFrame({
            'Date_Reclamation': pd.date_range('2024-01-01', periods=n_reclamations, freq='12H'),
            'ID_Client': np.random.randint(1000, 9999, n_reclamations),
            'Type_Reclamation': np.random.choice([
                'Produit défectueux', 'Livraison retardée', 'Service client',
                'Facturation', 'Qualité', 'Remboursement', 'Technique', 'Autre'
            ], n_reclamations),
            'Gravite': np.random.choice(['Faible', 'Moyenne', 'Elevée', 'Critique'], n_reclamations, 
                                       p=[0.3, 0.4, 0.2, 0.1]),
            'Service': np.random.choice(['Ventes', 'Support', 'Technique', 'Logistique', 'Finance'], n_reclamations),
            'Canal': np.random.choice(['Email', 'Téléphone', 'Chat', 'Courrier', 'Agence'], n_reclamations),
            'Statut': np.random.choice(['Ouverte', 'En cours', 'Résolue', 'Fermée'], n_reclamations,
                                      p=[0.15, 0.25, 0.45, 0.15]),
            'Delai_Traitement_Heures': np.random.randint(1, 168, n_reclamations),  # 1h à 1 semaine
            'Resolution_Premier_Contact': np.random.choice([True, False], n_reclamations, p=[0.3, 0.7]),
            'Cout_Traitement': np.random.uniform(10, 500, n_reclamations),
            'Satisfaction_Post_Resolution': np.random.uniform(1, 5, n_reclamations)
        })
        
        # Dataset 5: Satisfaction Client
        n_feedbacks = 1000
        datasets['satisfaction'] = pd.DataFrame({
            'Date_Feedback': pd.date_range('2024-01-01', periods=n_feedbacks, freq='8H'),
            'ID_Client': np.random.randint(1000, 9999, n_feedbacks),
            'Type_Interaction': np.random.choice([
                'Achat en ligne', 'Visite agence', 'Appel support', 
                'Chat', 'Email', 'Après-vente'
            ], n_feedbacks),
            'NPS_Score': np.random.randint(0, 11, n_feedbacks),  # 0-10
            'CSAT_Score': np.random.randint(1, 6, n_feedbacks),  # 1-5
            'CES_Score': np.random.randint(1, 8, n_feedbacks),  # 1-7
            'Service_Evalue': np.random.choice([
                'Ventes', 'Support', 'Technique', 'Logistique', 'Finance', 'Marketing'
            ], n_feedbacks),
            'Agent': np.random.choice(['Agent_A', 'Agent_B', 'Agent_C', 'Agent_D', 'Agent_E'], n_feedbacks),
            'Temps_Attente_Minutes': np.random.randint(0, 60, n_feedbacks),
            'Temps_Resolution_Minutes': np.random.randint(5, 120, n_feedbacks),
            'Nombre_Contacts': np.random.randint(1, 5, n_feedbacks),
            'Recommanderait': np.random.choice([True, False], n_feedbacks, p=[0.7, 0.3]),
            'Sentiment': np.random.choice(['Positif', 'Neutre', 'Négatif'], n_feedbacks, p=[0.6, 0.25, 0.15]),
            'Categorie_Client': np.random.choice(['VIP', 'Premium', 'Standard', 'Nouveau'], n_feedbacks,
                                                 p=[0.1, 0.2, 0.5, 0.2])
        })
        
        return datasets
    
    def generate_response(self, prompt: str, dataset_name: str) -> Dict[str, Any]:
        """
        Génère une réponse pour un prompt donné.
        
        Args:
            prompt: Le prompt utilisateur
            dataset_name: Nom du dataset à utiliser
            
        Returns:
            Dictionnaire avec la réponse et les métadonnées
        """
        try:
            # Charger le dataset approprié
            datasets = self.create_sample_datasets()
            if dataset_name not in datasets:
                return {
                    'success': False,
                    'error': f'Dataset {dataset_name} non trouvé'
                }
            
            df = datasets[dataset_name]
            
            # Sauvegarder temporairement le dataset
            temp_file = f"temp_{dataset_name}.csv"
            df.to_csv(temp_file, index=False)
            
            # Charger dans l'agent
            self.data_manager.load_data_file(temp_file)
            self.ai_agent.load_data_for_analysis(temp_file)
            
            # Générer la réponse
            response = self.ai_agent.process_query(prompt, use_cache=False)
            
            return {
                'success': True,
                'prompt': prompt,
                'response': response,
                'dataset': dataset_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'prompt': prompt,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_and_store_batch(self, num_prompts: int = 100) -> Dict[str, Any]:
        """
        Génère et stocke un lot de prompts/réponses dans ChromaDB.
        
        Args:
            num_prompts: Nombre de prompts à générer
            
        Returns:
            Statistiques de génération
        """
        print("=" * 70)
        print("🚀 GÉNÉRATION DE PROMPTS ET RÉPONSES POUR CHROMADB")
        print("=" * 70)
        
        all_prompts = self.generate_all_prompts()
        datasets = self.create_sample_datasets()
        
        # Calculer le nombre de prompts par catégorie
        total_available = sum(len(prompts) for prompts in all_prompts.values())
        print(f"\n📊 {total_available} prompts disponibles")
        print(f"🎯 Objectif: {num_prompts} prompts à générer\n")
        
        # Sélectionner les prompts à générer
        selected_prompts = []
        for category, prompts in all_prompts.items():
            # Prendre un échantillon de chaque catégorie
            sample_size = min(len(prompts), num_prompts // len(all_prompts))
            selected = np.random.choice(prompts, size=sample_size, replace=False)
            for prompt in selected:
                # Assigner un dataset aléatoire
                dataset = np.random.choice(list(datasets.keys()))
                selected_prompts.append((category, prompt, dataset))
        
        # Limiter au nombre demandé
        selected_prompts = selected_prompts[:num_prompts]
        
        # Générer les réponses
        results = {
            'total': len(selected_prompts),
            'success': 0,
            'errors': 0,
            'by_category': {},
            'by_dataset': {},
            'responses': []
        }
        
        print("🔄 Génération en cours...\n")
        for i, (category, prompt, dataset) in enumerate(selected_prompts, 1):
            print(f"[{i}/{len(selected_prompts)}] {category} - {dataset[:20]}...")
            
            response_data = self.generate_response(prompt, dataset)
            results['responses'].append(response_data)
            
            if response_data['success']:
                results['success'] += 1
                results['by_category'][category] = results['by_category'].get(category, 0) + 1
                results['by_dataset'][dataset] = results['by_dataset'].get(dataset, 0) + 1
                print(f"    ✅ Succès")
            else:
                results['errors'] += 1
                print(f"    ❌ Erreur: {response_data.get('error', 'Unknown')}")
        
        # Sauvegarder les résultats
        self._save_results(results)
        
        return results
    
    def _save_results(self, results: Dict[str, Any]):
        """Sauvegarde les résultats dans un fichier JSON."""
        output_dir = Path("generated_prompts")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"prompts_responses_{timestamp}.json"
        
        # Créer une version sérialisable
        serializable_results = {
            'total': results['total'],
            'success': results['success'],
            'errors': results['errors'],
            'by_category': results['by_category'],
            'by_dataset': results['by_dataset'],
            'responses': [
                {
                    'success': r['success'],
                    'prompt': r.get('prompt', ''),
                    'dataset': r.get('dataset', ''),
                    'response_summary': str(r.get('response', {}).get('response', ''))[:200],
                    'timestamp': r.get('timestamp', '')
                }
                for r in results['responses']
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés: {output_file}")
    
    def display_statistics(self, results: Dict[str, Any]):
        """Affiche les statistiques de génération."""
        print("\n" + "=" * 70)
        print("📊 STATISTIQUES DE GÉNÉRATION")
        print("=" * 70)
        
        print(f"\n✅ Total généré: {results['total']}")
        print(f"✅ Succès: {results['success']} ({results['success']/results['total']*100:.1f}%)")
        print(f"❌ Erreurs: {results['errors']} ({results['errors']/results['total']*100:.1f}%)")
        
        print(f"\n📂 Par catégorie:")
        for category, count in sorted(results['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {category:15s}: {count:3d} prompts")
        
        print(f"\n📊 Par dataset:")
        for dataset, count in sorted(results['by_dataset'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {dataset:15s}: {count:3d} prompts")
        
        print("\n" + "=" * 70)

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🎯 GÉNÉRATEUR DE PROMPTS POUR CHROMADB")
    print("=" * 70)
    
    generator = PromptResponseGenerator()
    
    # Afficher les catégories disponibles
    all_prompts = generator.generate_all_prompts()
    print(f"\n📋 Catégories disponibles:")
    for category, prompts in all_prompts.items():
        print(f"  • {category:15s}: {len(prompts):3d} prompts")
    
    total_prompts = sum(len(prompts) for prompts in all_prompts.values())
    print(f"\n📊 Total: {total_prompts} prompts disponibles")
    
    # Demander combien générer
    print("\n" + "=" * 70)
    try:
        num_prompts = int(input("Combien de prompts voulez-vous générer ? (défaut: 50) ") or "50")
    except ValueError:
        num_prompts = 50
    
    print(f"\n🚀 Génération de {num_prompts} prompts/réponses...\n")
    
    # Générer et stocker
    results = generator.generate_and_store_batch(num_prompts)
    
    # Afficher les statistiques
    generator.display_statistics(results)
    
    print("\n🎉 GÉNÉRATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 70)

if __name__ == "__main__":
    main()
