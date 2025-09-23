"""
Collection de prompts d'exemples pour tester les fonctionnalités de visualisation.
Organisés par type de données et type de graphique.
"""

from typing import Dict, List, Tuple, Optional, Any
import json
import os

CUSTOM_PROMPTS_FILE = "custom_prompts.json"


class ExamplePrompts:
    """Collection de prompts d'exemples pour tester l'agent IA."""
    
    def __init__(self):
        """Initialise la collection de prompts (statique + personnalisés)."""
        self.prompts_by_category = self._build_prompts()
        self.custom_prompts_by_category: Dict[str, List[Tuple[str, str]]] = {}
        self.custom_metadata: Dict[str, Dict[str, Any]] = {}  # key: (category|title) -> metadata
        self._load_custom_prompts()

    # -------------------- Persistence --------------------
    def _load_custom_prompts(self) -> None:
        """Charge les prompts personnalisés depuis le fichier JSON."""
        if not os.path.exists(CUSTOM_PROMPTS_FILE):
            return
        try:
            with open(CUSTOM_PROMPTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.custom_prompts_by_category = {
                cat: [(item['title'], item['prompt']) for item in items]
                for cat, items in data.get('prompts', {}).items()
            }
            self.custom_metadata = data.get('metadata', {})
        except (OSError, json.JSONDecodeError):
            # Fichier absent ou corrompu -> on ignore
            self.custom_prompts_by_category = {}
            self.custom_metadata = {}

    def _save_custom_prompts(self) -> None:
        """Sauvegarde les prompts personnalisés dans le fichier JSON."""
        try:
            serializable = {
                'prompts': {
                    cat: [
                        {
                            'title': title,
                            'prompt': prompt,
                            **(self.custom_metadata.get(f"{cat}|{title}") or {})
                        }
                        for title, prompt in items
                    ] for cat, items in self.custom_prompts_by_category.items()
                },
                'metadata': self.custom_metadata
            }
            with open(CUSTOM_PROMPTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
        except OSError:
            # Ecriture impossible (permissions, etc.) -> on ignore
            pass

    # -------------------- Dynamic operations --------------------
    def add_prompt(self, category: str, prompt_title: str, prompt_text: str,
                   viz_type: Optional[str] = None,
                   columns: Optional[Dict[str, str]] = None) -> bool:
        """Ajoute un prompt personnalisé et le persiste.

        Args:
            category: Catégorie existante ou nouvelle
            prompt_title: Titre lisible
            prompt_text: Texte du prompt
            viz_type: Type de visualisation suggéré (optionnel)
            columns: Mapping de colonnes suggéré (optionnel)
        Returns:
            True si ajouté
        """
        category = (category or "Autres").strip()
        new_title = (prompt_title or "").strip()
        body = (prompt_text or "").strip()
        if not new_title or not body:
            return False
        self.custom_prompts_by_category.setdefault(category, [])
        if any(t == new_title for t, _ in self.custom_prompts_by_category[category]):
            return False
        self.custom_prompts_by_category[category].append((new_title, body))
        meta_key = f"{category}|{new_title}"
        self.custom_metadata[meta_key] = {
            'viz_type': viz_type,
            'columns': columns or {}
        }
        self._save_custom_prompts()
        return True
    
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
        # Fusionne catégories statiques + custom
        categories = set(self.prompts_by_category.keys()) | set(self.custom_prompts_by_category.keys())
        return sorted(categories)
    
    def get_prompts_by_category(self, category: str) -> List[Tuple[str, str]]:
        """
        Retourne les prompts d'une catégorie.
        
        Args:
            category: Nom de la catégorie
            
        Returns:
            Liste de tuples (titre, prompt)
        """
        base = self.prompts_by_category.get(category, [])
        custom = self.custom_prompts_by_category.get(category, [])
        return base + custom
    
    def get_all_prompts(self) -> List[Tuple[str, str, str]]:
        """
        Retourne tous les prompts avec leur catégorie.
        
        Returns:
            Liste de tuples (catégorie, titre, prompt)
        """
        all_prompts = []
        # Inclure prompts dynamiques
        merged = self.get_categories()
        for category in merged:
            cat_prompts = self.get_prompts_by_category(category)
            for p_title, p_text in cat_prompts:
                all_prompts.append((category, p_title, p_text))
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
        
        merged = self.get_categories()
        for category in merged:
            cat_prompts = self.get_prompts_by_category(category)
            for p_title, p_text in cat_prompts:
                if (keyword_lower in p_title.lower() or 
                    keyword_lower in p_text.lower() or 
                    keyword_lower in category.lower()):
                    results.append((category, p_title, p_text))
        
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
        for bp in beginner_prompts:
            if bp[2] not in seen:
                seen.add(bp[2])
                unique_prompts.append(bp)
        
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
        for ap in advanced_prompts:
            if ap[2] not in seen:
                seen.add(ap[2])
                unique_prompts.append(ap)
        
        return unique_prompts

    # -------------------- Helpers dynamiques --------------------
    def is_custom(self, category: str, title: str) -> bool:
        """Indique si un prompt (catégorie, titre) est personnalisé."""
        return any(t == title for t, _ in self.custom_prompts_by_category.get(category, []))

    def get_metadata(self, category: str, title: str) -> Optional[Dict[str, Any]]:
        """Retourne les métadonnées d'un prompt custom."""
        if not self.is_custom(category, title):
            return None
        return self.custom_metadata.get(f"{category}|{title}")

    def update_prompt(self, category: str, old_title: str, new_title: str,
                      new_text: str, viz_type: Optional[str] = None,
                      columns: Optional[Dict[str, Any]] = None) -> bool:
        """Met à jour un prompt personnalisé.

        Règles:
        - Uniquement pour prompts custom
        - Empêche les doublons de titre dans la même catégorie
        - Conserve métadonnées si non fournies
        """
        if not self.is_custom(category, old_title):
            return False
        new_title = (new_title or "").strip()
        new_text = (new_text or "").strip()
        if not new_title or not new_text:
            return False
        prompts_list = self.custom_prompts_by_category.get(category, [])
        # Vérifier doublon si titre changé
        if old_title != new_title and any(t == new_title for t, _ in prompts_list):
            return False
        # Mettre à jour la liste
        for idx, (t, p) in enumerate(prompts_list):
            if t == old_title:
                prompts_list[idx] = (new_title, new_text)
                break
        # Mettre à jour métadonnées
        old_key = f"{category}|{old_title}"
        new_key = f"{category}|{new_title}"
        existing_meta = self.custom_metadata.get(old_key, {})
        updated_meta = existing_meta.copy()
        if viz_type is not None:
            updated_meta['viz_type'] = viz_type
        if columns is not None:
            updated_meta['columns'] = columns
        # Nettoyer anciennes clés si titre changé
        if old_key != new_key and old_key in self.custom_metadata:
            del self.custom_metadata[old_key]
        self.custom_metadata[new_key] = updated_meta
        self._save_custom_prompts()
        return True

    def delete_prompt(self, category: str, title: str) -> bool:
        """Supprime un prompt personnalisé et ses métadonnées."""
        if not self.is_custom(category, title):
            return False
        prompts_list = self.custom_prompts_by_category.get(category, [])
        new_list = [(t, p) for t, p in prompts_list if t != title]
        self.custom_prompts_by_category[category] = new_list
        meta_key = f"{category}|{title}"
        if meta_key in self.custom_metadata:
            del self.custom_metadata[meta_key]
        # Retirer catégorie si vide et non présente dans prompts statiques
        if not new_list and category not in self.prompts_by_category:
            del self.custom_prompts_by_category[category]
        self._save_custom_prompts()
        return True

    def validate_columns(self, dataframe, columns: Dict[str, str]) -> Dict[str, List[str]]:
        """Valide les colonnes proposées par rapport au DataFrame courant.

        Returns:
            dict avec keys: valid, invalid
        """
        if dataframe is None or not columns:
            return {"valid": [], "invalid": []}
        df_cols = set(dataframe.columns)
        used = set([c for c in columns.values() if c])
        valid = sorted([c for c in used if c in df_cols])
        invalid = sorted([c for c in used if c not in df_cols])
        return {"valid": valid, "invalid": invalid}

    def suggest_viz_type(self, dataframe, columns: Dict[str, str]) -> Tuple[str, str]:
        """Suggère un type de visualisation à partir du DataFrame et du mapping de colonnes.

        Heuristiques simples :
        - x & y numériques -> scatter
        - x date/datetime & y numérique -> line_chart
        - x catégorielle & y numérique -> bar_chart
        - seulement y numérique -> histogram
        - mapping 'columns' (liste) > 2 numériques -> heatmap
        - y numérique seul -> boxplot (alternative)
        """
        try:
            if dataframe is None or not columns:
                return "", "Pas assez d'informations"
            import pandas as pd  # local import
            # Collecte
            x = columns.get('x')
            y = columns.get('y')
            cols_list = columns.get('columns') if isinstance(columns.get('columns'), list) else None
            # Heatmap candidate
            if cols_list:
                numeric = [c for c in cols_list if c in dataframe.columns and pd.api.types.is_numeric_dtype(dataframe[c])]
                if len(numeric) >= 3:
                    return "heatmap", "Plusieurs colonnes numériques pour corrélation"
            # x & y présents
            if x and y and x in dataframe.columns and y in dataframe.columns:
                x_dtype = dataframe[x].dtype
                y_dtype = dataframe[y].dtype
                if pd.api.types.is_datetime64_any_dtype(x_dtype):
                    if pd.api.types.is_numeric_dtype(y_dtype):
                        return "line_chart", "Série temporelle détectée (x temporel, y numérique)"
                if pd.api.types.is_numeric_dtype(x_dtype) and pd.api.types.is_numeric_dtype(y_dtype):
                    return "scatter", "Deux variables numériques (x,y)"
                if (not pd.api.types.is_numeric_dtype(x_dtype)) and pd.api.types.is_numeric_dtype(y_dtype):
                    return "bar_chart", "x catégoriel et y numérique"
            # Seulement y
            if y and y in dataframe.columns and pd.api.types.is_numeric_dtype(dataframe[y]):
                return "histogram", "Une seule variable numérique"
            # Dernier recours
            return "boxplot", "Fallback - distribution d'une variable"
        except Exception as e:  # pragma: no cover
            return "", f"Aucune suggestion ({e})"


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