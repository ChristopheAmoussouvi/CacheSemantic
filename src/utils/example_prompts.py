"""
Collection de prompts d'exemples pour tester les fonctionnalités de visualisation.
Organisés par type de données et type de graphique.
"""

from typing import Dict, List, Tuple


class ExamplePrompts:
    """Collection de prompts d'exemples pour tester l'agent IA."""
    
    def __init__(self):
        """Initialise la collection de prompts."""
        self.prompts_by_category = self._build_prompts()
    
    def _build_prompts(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Construit la collection de prompts organisée par catégorie.
        
        Returns:
            Dictionnaire {catégorie: [(titre, prompt), ...]}
        """
        return {
            "📊 Analyses de Ventes": [
                ("Vue d'ensemble des ventes", 
                 "Montre-moi un résumé général des données de ventes"),
                ("Graphique des ventes par région", 
                 "Crée un graphique en barres des ventes par région"),
                ("Évolution du chiffre d'affaires", 
                 "Affiche l'évolution du chiffre d'affaires dans le temps"),
                ("Top 5 des produits", 
                 "Quels sont les 5 produits les plus vendus ?"),
                ("Performance des vendeurs", 
                 "Compare les performances de chaque vendeur"),
                ("Analyse saisonnière", 
                 "Y a-t-il une saisonnalité dans les ventes ?"),
                ("Corrélation prix-quantité", 
                 "Montre la relation entre prix et quantité vendue")
            ],
            
            "👥 Analyses Clients": [
                ("Profil des clients", 
                 "Donne-moi un aperçu du profil de nos clients"),
                ("Répartition par âge", 
                 "Crée un histogramme de la répartition par âge"),
                ("Satisfaction par ville", 
                 "Compare la satisfaction client par ville"),
                ("Segmentation clients", 
                 "Segmente les clients selon leur valeur"),
                ("Relation âge-salaire", 
                 "Montre la relation entre l'âge et le salaire"),
                ("Clients les plus actifs", 
                 "Qui sont nos clients les plus actifs ?"),
                ("Analyse démographique", 
                 "Analyse la répartition hommes/femmes par tranche d'âge")
            ],
            
            "💰 Analyses Financières": [
                ("Tableau de bord financier", 
                 "Crée un tableau de bord des indicateurs financiers"),
                ("Évolution des bénéfices", 
                 "Montre l'évolution des bénéfices sur la période"),
                ("Analyse de la marge", 
                 "Comment évolue notre marge bénéficiaire ?"),
                ("Comparaison trimestrielle", 
                 "Compare les performances par trimestre"),
                ("Tendance des coûts", 
                 "Analyse l'évolution des coûts dans le temps"),
                ("Prévision financière", 
                 "Peux-tu identifier une tendance pour les prochains mois ?"),
                ("Ratio coûts/revenus", 
                 "Montre le ratio entre coûts et revenus")
            ],
            
            "📋 Analyses d'Enquêtes": [
                ("Satisfaction globale", 
                 "Quel est le niveau de satisfaction global ?"),
                ("Satisfaction par service", 
                 "Compare la satisfaction pour chaque service"),
                ("Analyse par tranche d'âge", 
                 "La satisfaction varie-t-elle selon l'âge ?"),
                ("Recommandations clients", 
                 "Quelle proportion de clients nous recommande ?"),
                ("Services à améliorer", 
                 "Quels services ont besoin d'amélioration ?"),
                ("Évolution temporelle", 
                 "Comment évolue la satisfaction dans le temps ?"),
                ("Matrice satisfaction-recommandation", 
                 "Crée une matrice satisfaction vs recommandation")
            ],
            
            "🔍 Analyses Exploratoires": [
                ("Statistiques descriptives", 
                 "Donne-moi les statistiques descriptives principales"),
                ("Détection d'anomalies", 
                 "Y a-t-il des valeurs aberrantes dans les données ?"),
                ("Matrice de corrélation", 
                 "Montre les corrélations entre toutes les variables"),
                ("Distribution des variables", 
                 "Affiche la distribution de chaque variable numérique"),
                ("Analyse des valeurs manquantes", 
                 "Y a-t-il des données manquantes ?"),
                ("Patterns cachés", 
                 "Peux-tu identifier des patterns intéressants ?"),
                ("Clustering automatique", 
                 "Identifie des groupes naturels dans les données")
            ],
            
            "📈 Visualisations Avancées": [
                ("Graphique en aires empilées", 
                 "Crée un graphique en aires empilées du chiffre d'affaires par produit"),
                ("Heatmap des ventes", 
                 "Montre une heatmap des ventes par mois et région"),
                ("Graphique en radar", 
                 "Crée un graphique radar des performances par vendeur"),
                ("Diagramme en violon", 
                 "Affiche la distribution des prix avec un violin plot"),
                ("Graphique de Sankey", 
                 "Montre le flux des ventes par région et produit"),
                ("Bubble chart", 
                 "Crée un nuage de bulles avec 3 dimensions"),
                ("Timeline interactive", 
                 "Affiche une timeline des événements importants")
            ]
        }
    
    def get_categories(self) -> List[str]:
        """Retourne la liste des catégories disponibles."""
        return list(self.prompts_by_category.keys())
    
    def get_prompts_by_category(self, category: str) -> List[Tuple[str, str]]:
        """
        Retourne les prompts d'une catégorie.
        
        Args:
            category: Nom de la catégorie
            
        Returns:
            Liste de tuples (titre, prompt)
        """
        return self.prompts_by_category.get(category, [])
    
    def get_all_prompts(self) -> List[Tuple[str, str, str]]:
        """
        Retourne tous les prompts avec leur catégorie.
        
        Returns:
            Liste de tuples (catégorie, titre, prompt)
        """
        all_prompts = []
        for category, prompts in self.prompts_by_category.items():
            for title, prompt in prompts:
                all_prompts.append((category, title, prompt))
        return all_prompts
    
    def search_prompts(self, keyword: str) -> List[Tuple[str, str, str]]:
        """
        Recherche des prompts contenant un mot-clé.
        
        Args:
            keyword: Mot-clé à rechercher
            
        Returns:
            Liste de tuples (catégorie, titre, prompt) correspondants
        """
        results = []
        keyword_lower = keyword.lower()
        
        for category, prompts in self.prompts_by_category.items():
            for title, prompt in prompts:
                if (keyword_lower in title.lower() or 
                    keyword_lower in prompt.lower() or 
                    keyword_lower in category.lower()):
                    results.append((category, title, prompt))
        
        return results
    
    def get_random_prompt(self) -> Tuple[str, str, str]:
        """
        Retourne un prompt aléatoire.
        
        Returns:
            Tuple (catégorie, titre, prompt)
        """
        import random
        all_prompts = self.get_all_prompts()
        return random.choice(all_prompts)
    
    def get_beginner_prompts(self) -> List[Tuple[str, str, str]]:
        """
        Retourne une sélection de prompts pour débutants.
        
        Returns:
            Liste de prompts simples et explicatifs
        """
        beginner_keywords = [
            "résumé", "aperçu", "montre", "affiche", "donne-moi",
            "vue d'ensemble", "profil", "tableau de bord"
        ]
        
        beginner_prompts = []
        for keyword in beginner_keywords:
            results = self.search_prompts(keyword)
            beginner_prompts.extend(results[:2])  # Max 2 par mot-clé
        
        # Déduplication
        seen = set()
        unique_prompts = []
        for prompt in beginner_prompts:
            if prompt[2] not in seen:
                seen.add(prompt[2])
                unique_prompts.append(prompt)
        
        return unique_prompts[:10]  # Top 10
    
    def get_advanced_prompts(self) -> List[Tuple[str, str, str]]:
        """
        Retourne une sélection de prompts avancés.
        
        Returns:
            Liste de prompts pour utilisateurs expérimentés
        """
        advanced_keywords = [
            "corrélation", "clustering", "anomalies", "patterns",
            "prévision", "segmentation", "matrice", "tendance"
        ]
        
        advanced_prompts = []
        for keyword in advanced_keywords:
            results = self.search_prompts(keyword)
            advanced_prompts.extend(results)
        
        # Déduplication et tri par complexité
        seen = set()
        unique_prompts = []
        for prompt in advanced_prompts:
            if prompt[2] not in seen:
                seen.add(prompt[2])
                unique_prompts.append(prompt)
        
        return unique_prompts


if __name__ == "__main__":
    # Test des prompts
    prompts = ExamplePrompts()
    print("Catégories disponibles:")
    for cat in prompts.get_categories():
        print(f"- {cat}")
    
    print(f"\nNombre total de prompts: {len(prompts.get_all_prompts())}")
    
    print("\nRecherche 'graphique':")
    for cat, title, prompt in prompts.search_prompts("graphique")[:3]:
        print(f"  [{cat}] {title}: {prompt}")