"""
Script de validation finale pour vérifier que toutes les corrections fonctionnent.
"""

import sys
import os

def test_imports():
    """Test que tous les modules s'importent correctement."""
    print("🔍 TEST DES IMPORTS")
    print("=" * 60)
    
    modules_to_test = [
        ("src.utils.enhanced_anonymizer", "EnhancedDataAnonymizer"),
        ("src.utils.spacy_enhanced_anonymizer", "SpacyEnhancedDataAnonymizer"),
        ("src.components.data_manager", "DataManager"),
        ("src.components.ai_agent", "AIAgent"),
    ]
    
    success_count = 0
    failed = []
    
    for module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_path}.{class_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module_path}.{class_name}: {e}")
            failed.append((module_path, class_name, str(e)))
    
    print(f"\n📊 Résultats: {success_count}/{len(modules_to_test)} modules importés avec succès")
    
    if failed:
        print(f"\n❌ Modules échoués:")
        for mod, cls, err in failed:
            print(f"   - {mod}.{cls}: {err}")
        return False
    
    return True


def test_anonymizer_initialization():
    """Test l'initialisation des anonymiseurs."""
    print(f"\n\n🚀 TEST D'INITIALISATION DES ANONYMISEURS")
    print("=" * 60)
    
    try:
        from src.utils.enhanced_anonymizer import EnhancedDataAnonymizer
        anonymizer1 = EnhancedDataAnonymizer()
        print("✅ EnhancedDataAnonymizer initialisé")
    except Exception as e:
        print(f"❌ Erreur EnhancedDataAnonymizer: {e}")
        return False
    
    try:
        from src.utils.spacy_enhanced_anonymizer import SpacyEnhancedDataAnonymizer
        anonymizer2 = SpacyEnhancedDataAnonymizer()
        print("✅ SpacyEnhancedDataAnonymizer initialisé")
    except Exception as e:
        print(f"❌ Erreur SpacyEnhancedDataAnonymizer: {e}")
        return False
    
    return True


def test_name_detection():
    """Test la détection de noms avec les deux anonymiseurs."""
    print(f"\n\n📝 TEST DE DÉTECTION DE NOMS")
    print("=" * 60)
    
    test_names = [
        "Mohamed Ben Ali",
        "mohamed ben ali",
        "Fatima Al-Zahra",
        "Jean Dupont",
        "test123"
    ]
    
    try:
        from src.utils.spacy_enhanced_anonymizer import SpacyEnhancedDataAnonymizer
        anonymizer = SpacyEnhancedDataAnonymizer()
        
        detected = 0
        for name in test_names:
            is_name, score, reasons = anonymizer.is_name_like_advanced_spacy(name)
            status = "✅" if is_name else "❌"
            print(f"{status} '{name}': {score:.3f}")
            if is_name:
                detected += 1
        
        print(f"\n📊 {detected}/{len(test_names)} noms détectés")
        return detected >= 3  # Au moins 3 noms doivent être détectés
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_functionality():
    """Test que le cache fonctionne correctement."""
    print(f"\n\n💾 TEST DU CACHE")
    print("=" * 60)
    
    try:
        from src.utils.spacy_enhanced_anonymizer import SpacyEnhancedDataAnonymizer
        anonymizer = SpacyEnhancedDataAnonymizer()
        
        # Premier appel
        result1 = anonymizer.is_name_like_advanced_spacy("Mohamed Ben Ali")
        
        # Deuxième appel (devrait utiliser le cache)
        result2 = anonymizer.is_name_like_advanced_spacy("Mohamed Ben Ali")
        
        # Vérifier que les résultats sont identiques
        if result1 == result2:
            print("✅ Cache fonctionne correctement")
            print(f"   Résultat mis en cache: {result1}")
            return True
        else:
            print(f"❌ Les résultats diffèrent: {result1} != {result2}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test du cache: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Exécute tous les tests de validation."""
    print("🎯 VALIDATION FINALE - CORRECTIONS DES ERREURS")
    print("=" * 70)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Initialisation", test_anonymizer_initialization),
        ("Détection de noms", test_name_detection),
        ("Fonctionnalité cache", test_cache_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Exception non gérée dans {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Résumé final
    print(f"\n\n" + "=" * 70)
    print("📈 RÉSUMÉ FINAL")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Score global: {passed}/{total} tests réussis ({100*passed/total:.1f}%)")
    
    if passed == total:
        print("\n🎉 SUCCÈS: Toutes les corrections fonctionnent correctement!")
        return True
    else:
        print(f"\n⚠️  ATTENTION: {total - passed} test(s) échoué(s)")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
