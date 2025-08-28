"""
Tests de validation pour l'Agent IA d'Analyse de Données
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.components.semantic_cache import SemanticCache
from src.components.data_manager import DataManager


class TestSemanticCache(unittest.TestCase):
    """Tests pour le cache sémantique."""
    
    def setUp(self):
        """Configuration des tests."""
        self.cache = SemanticCache(
            threshold=0.8,
            cache_dir="./test_cache",
            max_cache_size=10
        )
    
    def test_cache_initialization(self):
        """Test d'initialisation du cache."""
        self.assertEqual(self.cache.threshold, 0.8)
        self.assertEqual(self.cache.max_cache_size, 10)
        self.assertIsNotNone(self.cache.embedding_model)
    
    def test_add_and_query(self):
        """Test d'ajout et de requête."""
        # Ajouter une entrée
        self.cache.add("Quelle est la somme des ventes?", "42000 euros")
        
        # Tester une requête similaire
        result = self.cache.query("Quel est le total des ventes?")
        self.assertIsNotNone(result)
    
    def test_cache_stats(self):
        """Test des statistiques du cache."""
        stats = self.cache.get_stats()
        self.assertIn('total_entries', stats)
        self.assertIn('threshold', stats)
    
    def tearDown(self):
        """Nettoyage après tests."""
        if hasattr(self, 'cache'):
            self.cache.clear()


class TestDataManager(unittest.TestCase):
    """Tests pour le gestionnaire de données."""
    
    def setUp(self):
        """Configuration des tests."""
        self.data_manager = DataManager(
            db_path="./test_chroma_db",
            collection_name="test_collection"
        )
    
    def test_initialization(self):
        """Test d'initialisation."""
        self.assertIsNotNone(self.data_manager.client)
        self.assertIsNotNone(self.data_manager.collection)
    
    def test_get_stats(self):
        """Test des statistiques de la base."""
        stats = self.data_manager.get_stats()
        self.assertIn('total_documents', stats)
        self.assertIn('loaded_files', stats)
    
    def test_list_files(self):
        """Test de la liste des fichiers."""
        files = self.data_manager.list_files()
        self.assertIsInstance(files, list)
    
    def tearDown(self):
        """Nettoyage après tests."""
        if hasattr(self, 'data_manager'):
            self.data_manager.reset_database()


class TestIntegration(unittest.TestCase):
    """Tests d'intégration des composants."""
    
    def test_component_compatibility(self):
        """Test de compatibilité entre composants."""
        cache = SemanticCache(cache_dir="./test_integration_cache")
        data_manager = DataManager(db_path="./test_integration_db")
        
        # Vérifier que les composants peuvent coexister
        self.assertIsNotNone(cache.get_stats())
        self.assertIsNotNone(data_manager.get_stats())
        
        # Nettoyage
        cache.clear()
        data_manager.reset_database()


def run_validation_tests():
    """Exécute tous les tests de validation."""
    print("🧪 Exécution des tests de validation...")
    print("=" * 50)
    
    # Configuration du runner de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests
    suite.addTest(loader.loadTestsFromTestCase(TestSemanticCache))
    suite.addTest(loader.loadTestsFromTestCase(TestDataManager))
    suite.addTest(loader.loadTestsFromTestCase(TestIntegration))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ Tous les tests sont passés avec succès !")
    else:
        print("❌ Certains tests ont échoué.")
        print(f"Échecs: {len(result.failures)}")
        print(f"Erreurs: {len(result.errors)}")
    
    return result.wasSuccessful()


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées."""
    print("🔍 Vérification des dépendances...")
    
    required_modules = [
        'streamlit',
        'langchain',
        'chromadb',
        'faiss',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'sentence_transformers'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MANQUANT")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Modules manquants: {', '.join(missing_modules)}")
        print("Installez-les avec: pip install -r requirements.txt")
        return False
    
    print("\n✅ Toutes les dépendances sont installées !")
    return True


def check_configuration():
    """Vérifie la configuration de l'application."""
    print("⚙️  Vérification de la configuration...")
    
    # Vérifier le fichier .env
    if os.path.exists('.env'):
        print("✅ Fichier .env trouvé")
        
        # Vérifier la clé API OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            print("✅ Clé API OpenAI configurée")
        else:
            print("⚠️  Clé API OpenAI manquante ou non configurée")
            print("Éditez le fichier .env et ajoutez votre clé API")
            return False
    else:
        print("❌ Fichier .env manquant")
        print("Copiez .env.example vers .env et configurez-le")
        return False
    
    # Vérifier les répertoires
    directories = ['data', 'cache', 'chroma_db', 'exports']
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Répertoire {directory}")
        else:
            print(f"⚠️  Répertoire {directory} sera créé automatiquement")
    
    print("\n✅ Configuration validée !")
    return True


if __name__ == "__main__":
    print("🚀 Validation de l'Agent IA d'Analyse de Données")
    print("=" * 60)
    
    # Étapes de validation
    steps = [
        ("Dépendances", check_dependencies),
        ("Configuration", check_configuration),
        ("Tests unitaires", run_validation_tests)
    ]
    
    all_passed = True
    
    for step_name, step_function in steps:
        print(f"\n📋 {step_name}")
        print("-" * 30)
        
        try:
            success = step_function()
            if not success:
                all_passed = False
        except Exception as e:
            print(f"❌ Erreur dans {step_name}: {e}")
            all_passed = False
    
    # Résultat final
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 Validation complète réussie !")
        print("Votre application est prête à être utilisée.")
        print("\nPour démarrer l'application :")
        print("  - Exécutez: start.bat")
        print("  - Ou: streamlit run app.py")
    else:
        print("❌ Validation échouée.")
        print("Corrigez les erreurs avant de démarrer l'application.")
    
    print("=" * 60)
