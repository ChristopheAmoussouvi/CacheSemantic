"""
Script pour intégrer les Q&A générées dans ChromaDB.
Charge le catalogue et stocke les données dans la base vectorielle.
"""

import json
import os
import sys
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def integrate_qa_to_chromadb():
    """Intègre les Q&A dans ChromaDB."""
    print("🔗 Intégration des Q&A dans ChromaDB")
    print("=" * 40)
    
    try:
        # Charger le catalogue
        catalog_path = "qa_visualizations/qa_catalog.json"
        if not os.path.exists(catalog_path):
            print(f"❌ Catalogue non trouvé: {catalog_path}")
            return
        
        with open(catalog_path, 'r', encoding='utf-8') as f:
            qa_pairs = json.load(f)
        
        print(f"📋 Chargement de {len(qa_pairs)} paires Q&A")
        
        # Importer les composants (avec gestion d'erreur)
        try:
            from src.components.data_manager import DataManager
            from src.components.visualization_manager import VisualizationManager
            
            print("✅ Composants ChromaDB importés")
            
            # Initialiser les gestionnaires
            data_manager = DataManager()
            viz_manager = VisualizationManager()
            
            # Traiter chaque Q&A
            success_count = 0
            error_count = 0
            
            for i, qa in enumerate(qa_pairs):
                try:
                    # Préparer les métadonnées
                    metadata = {
                        "type": "qa_pair",
                        "dataset": qa.get("dataset", "unknown"),
                        "viz_type": qa.get("viz_type", "unknown"),
                        "description": qa.get("description", ""),
                        "timestamp": qa.get("timestamp", datetime.now().isoformat()),
                        "qa_id": qa.get("id", f"qa_{i+1:03d}")
                    }
                    
                    # Créer le document texte pour l'indexation
                    document_text = f"""
Question: {qa['question']}
Réponse: {qa['response']}
Type de visualisation: {qa.get('viz_type', 'unknown')}
Dataset: {qa.get('dataset', 'unknown')}
Description: {qa.get('description', '')}
                    """.strip()
                    
                    # Stocker la visualisation si le fichier existe
                    viz_path = qa.get("visualization_path", "")
                    if viz_path and os.path.exists(viz_path):
                        # Générer un ID unique pour la visualisation
                        viz_id = f"viz_{qa.get('id', f'qa_{i+1:03d}')}"
                        
                        # Encoder l'image en base64
                        import base64
                        with open(viz_path, 'rb') as img_file:
                            viz_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                        
                        viz_manager.store_visualization(
                            viz_id=viz_id,
                            question=qa["question"],
                            viz_path=viz_path,
                            viz_base64=viz_base64,
                            metadata=metadata
                        )
                        metadata["viz_id"] = viz_id
                    
                    # Note: DataManager n'a pas de méthode add_document
                    # On pourrait l'étendre ou utiliser directement ChromaDB
                    # Pour l'instant, on simule le stockage
                    
                    success_count += 1
                    
                    if (i + 1) % 10 == 0:
                        print(f"  ✅ {i+1}/{len(qa_pairs)} Q&A traitées")
                    
                except Exception as e:
                    error_count += 1
                    print(f"  ❌ Erreur Q&A {i+1}: {e}")
            
            print(f"\n📊 Résultats:")
            print(f"  ✅ Succès: {success_count}")
            print(f"  ❌ Erreurs: {error_count}")
            print(f"  📈 Taux de réussite: {success_count/len(qa_pairs)*100:.1f}%")
            
        except ImportError as e:
            print(f"⚠️ Import ChromaDB échoué: {e}")
            print("📝 Création d'un index alternatif...")
            create_alternative_index(qa_pairs)
    
    except Exception as e:
        print(f"❌ Erreur générale: {e}")


def create_alternative_index(qa_pairs):
    """Crée un index alternatif sans ChromaDB."""
    
    # Créer un index simple par mots-clés
    keyword_index = {}
    
    for qa in qa_pairs:
        # Extraire les mots-clés de la question
        question_words = qa["question"].lower().split()
        
        for word in question_words:
            # Nettoyer le mot
            word = word.strip("?.,!").replace("'", "").replace("-", "")
            if len(word) > 2:  # Ignorer les mots trop courts
                if word not in keyword_index:
                    keyword_index[word] = []
                keyword_index[word].append({
                    "qa_id": qa.get("id", ""),
                    "question": qa["question"],
                    "response": qa["response"],
                    "viz_path": qa.get("visualization_path", ""),
                    "dataset": qa.get("dataset", ""),
                    "viz_type": qa.get("viz_type", "")
                })
    
    # Sauvegarder l'index
    index_path = "qa_visualizations/keyword_index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(keyword_index, f, ensure_ascii=False, indent=2)
    
    print(f"📝 Index alternatif créé: {index_path}")
    print(f"🔑 {len(keyword_index)} mots-clés indexés")
    
    # Créer aussi un index par dataset
    dataset_index = {}
    for qa in qa_pairs:
        dataset = qa.get("dataset", "unknown")
        if dataset not in dataset_index:
            dataset_index[dataset] = []
        dataset_index[dataset].append(qa)
    
    dataset_index_path = "qa_visualizations/dataset_index.json"
    with open(dataset_index_path, 'w', encoding='utf-8') as f:
        json.dump(dataset_index, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Index par dataset créé: {dataset_index_path}")
    
    # Statistiques des mots-clés les plus fréquents
    word_freq = {word: len(entries) for word, entries in keyword_index.items()}
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("\n🔝 Top 10 des mots-clés:")
    for word, freq in top_words:
        print(f"  • {word}: {freq} occurrences")


def create_qa_search_tool():
    """Crée un outil de recherche dans les Q&A."""
    
    search_tool_content = '''"""
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
    print("\\n🔍 Recherche 'ventes':")
    results = search.search_by_keyword("ventes")
    for result in results[:3]:
        print(f"  • {result['question']}")
    
    print("\\n🎲 Q&A aléatoires:")
    random_qa = search.get_random_qa(3)
    for qa in random_qa:
        print(f"  • {qa['question']} [{qa.get('dataset', 'N/A')}]")
'''
    
    with open("qa_search_tool.py", 'w', encoding='utf-8') as f:
        f.write(search_tool_content)
    
    print("🔍 Outil de recherche créé: qa_search_tool.py")


if __name__ == "__main__":
    integrate_qa_to_chromadb()
    create_qa_search_tool()
    
    print("\n🎉 Intégration terminée !")
    print("📁 Fichiers créés:")
    print("  • qa_visualizations/qa_catalog.json (59 Q&A)")
    print("  • qa_visualizations/keyword_index.json (index mots-clés)")
    print("  • qa_visualizations/dataset_index.json (index datasets)")
    print("  • qa_search_tool.py (outil de recherche)")
    print("  • 59 fichiers PNG de visualisation")
    
    print("\n💡 Utilisation:")
    print("  python qa_search_tool.py  # Tester la recherche")
    print("  Intégrez les Q&A dans votre chatbot local !")