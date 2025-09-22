"""
Outil de recherche dans les Q&A générées.
Permet de trouver des questions/réponses par mots-clés.
"""

import json
import os
from typing import List, Dict, Any

class QASearchTool:
    """Outil de recherche dans la base de Q&A."""
    
    def __init__(self):
        """Initialise l'outil avec les index."""
        self.qa_catalog = self._load_catalog()
        self.keyword_index = self._load_keyword_index()
        self.dataset_index = self._load_dataset_index()
    
    def _load_catalog(self) -> List[Dict]:
        """Charge le catalogue complet."""
        try:
            with open("qa_visualizations/qa_catalog.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _load_keyword_index(self) -> Dict:
        """Charge l'index par mots-clés."""
        try:
            with open("qa_visualizations/keyword_index.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _load_dataset_index(self) -> Dict:
        """Charge l'index par dataset."""
        try:
            with open("qa_visualizations/dataset_index.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """Recherche par mot-clé."""
        keyword = keyword.lower().strip()
        return self.keyword_index.get(keyword, [])
    
    def search_by_dataset(self, dataset: str) -> List[Dict]:
        """Recherche par dataset."""
        dataset = dataset.lower().strip()
        return self.dataset_index.get(dataset, [])
    
    def search_by_viz_type(self, viz_type: str) -> List[Dict]:
        """Recherche par type de visualisation."""
        results = []
        for qa in self.qa_catalog:
            if qa.get("viz_type", "").lower() == viz_type.lower():
                results.append(qa)
        return results
    
    def fuzzy_search(self, query: str) -> List[Dict]:
        """Recherche floue dans les questions."""
        query = query.lower()
        results = []
        
        for qa in self.qa_catalog:
            question = qa["question"].lower()
            response = qa["response"].lower()
            
            # Recherche dans question et réponse
            if query in question or query in response:
                results.append(qa)
        
        return results
    
    def get_random_qa(self, n: int = 5) -> List[Dict]:
        """Retourne des Q&A aléatoires."""
        import random
        return random.sample(self.qa_catalog, min(n, len(self.qa_catalog)))
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques de la base."""
        return {
            "total_qa": len(self.qa_catalog),
            "datasets": list(self.dataset_index.keys()),
            "viz_types": list(set(qa.get("viz_type", "") for qa in self.qa_catalog)),
            "keywords": len(self.keyword_index)
        }

# Exemple d'utilisation
if __name__ == "__main__":
    search = QASearchTool()
    
    print("🔍 Outil de recherche Q&A")
    print("=" * 30)
    
    # Statistiques
    stats = search.get_stats()
    print(f"📊 {stats['total_qa']} Q&A disponibles")
    print(f"📁 Datasets: {', '.join(stats['datasets'])}")
    print(f"🎨 Types de viz: {', '.join(stats['viz_types'])}")
    
    # Recherche d'exemple
    print("\n🔍 Recherche 'ventes':")
    results = search.search_by_keyword("ventes")
    for result in results[:3]:
        print(f"  • {result['question']}")
    
    print("\n🎲 Q&A aléatoires:")
    random_qa = search.get_random_qa(3)
    for qa in random_qa:
        print(f"  • {qa['question']} [{qa.get('dataset', 'N/A')}]")
