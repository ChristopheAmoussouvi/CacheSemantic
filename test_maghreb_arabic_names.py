"""
Test spécifique pour les noms du Maghreb/arabes et les cas sans capitalisation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.utils.enhanced_anonymizer import EnhancedDataAnonymizer, EnhancedAnonymizationConfig
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    print("⚠️ Module enhanced_anonymizer non disponible")

def test_maghreb_arabic_names():
    """Test spécifique pour les noms du Maghreb et arabes."""
    
    print("🧪 TEST SPÉCIFIQUE - NOMS DU MAGHREB ET ARABES")
    print("=" * 60)
    
    # Noms du Maghreb et arabes avec différentes capitalisations
    test_names = [
        # Noms avec capitalisation correcte
        ("Mohamed Ben Ali", "Nom marocain classique"),
        ("Fatima Zahra", "Prénom féminin arabe"),
        ("Ahmed El Mansouri", "Nom avec particule 'El'"),
        ("Khadija Benali", "Nom féminin avec 'Ben'"),
        ("Omar Ibn Khaldoun", "Nom avec 'Ibn'"),
        ("Aisha Al-Zahra", "Nom avec 'Al-'"),
        ("Youssef Ould Mohamed", "Nom mauritanien avec 'Ould'"),
        ("Leila Bint Rashid", "Nom avec 'Bint'"),
        
        # Noms SANS capitalisation (test critique)
        ("mohamed ben ali", "Même nom sans capitalisation"),
        ("fatima zahra", "Prénom féminin sans capitalisation"),
        ("ahmed el mansouri", "Nom avec particule sans capitalisation"),
        ("khadija benali", "Nom féminin sans capitalisation"),
        ("omar ibn khaldoun", "Nom historique sans capitalisation"),
        ("aisha al-zahra", "Nom avec trait d'union sans capitalisation"),
        
        # Noms berbères/amazighs
        ("Tamazight Amellal", "Nom berbère"),
        ("Yemma Gouraya", "Nom kabyle"),
        ("tamazight amellal", "Nom berbère sans capitalisation"),
        
        # Noms composés complexes
        ("Abd El Rahman", "Nom avec 'Abd'"),
        ("Sidi Mohamed", "Nom avec titre 'Sidi'"),
        ("abd el rahman", "Sans capitalisation"),
        ("sidi mohamed", "Sans capitalisation")
    ]
    
    if not ENHANCED_AVAILABLE:
        print("❌ Impossible de tester - module enhanced_anonymizer non disponible")
        return
    
    # Configuration pour mode strict
    config = EnhancedAnonymizationConfig(
        detect_uncommon_names=True,
        name_threshold_strict=0.9,
        name_threshold_loose=0.5,  # Plus permissif pour tester
        anonymization_mode="balanced"
    )
    
    anonymizer = EnhancedDataAnonymizer(config)
    
    print("📊 RÉSULTATS DE DÉTECTION:")
    print("-" * 50)
    
    capitalized_detected = 0
    lowercase_detected = 0
    total_capitalized = 0
    total_lowercase = 0
    
    for name, description in test_names:
        is_name, confidence, reasons = anonymizer.is_name_like_advanced(name)
        
        # Classifier selon la capitalisation
        has_capitals = any(c.isupper() for c in name)
        if has_capitals:
            total_capitalized += 1
            if is_name:
                capitalized_detected += 1
        else:
            total_lowercase += 1
            if is_name:
                lowercase_detected += 1
        
        # Affichage des résultats
        status = "✅ DÉTECTÉ" if is_name else "❌ RATÉ"
        print(f"{status} '{name}' (conf: {confidence:.3f})")
        print(f"    📝 {description}")
        print(f"    🔍 Raisons: {reasons[:3]}")
        print()
    
    print("=" * 60)
    print("📈 STATISTIQUES DE PERFORMANCE:")
    print("-" * 30)
    print(f"Noms avec capitalisation: {capitalized_detected}/{total_capitalized} ({capitalized_detected/total_capitalized*100:.1f}%)")
    print(f"Noms sans capitalisation: {lowercase_detected}/{total_lowercase} ({lowercase_detected/total_lowercase*100:.1f}%)")
    
    # Analyse des problèmes
    print("\n🔍 ANALYSE DES LIMITATIONS ACTUELLES:")
    print("-" * 40)
    
    if lowercase_detected < total_lowercase:
        print("❌ PROBLÈME: Détection faible pour noms sans capitalisation")
        print("   → L'analyse de capitalisation pénalise trop les minuscules")
        
    if capitalized_detected < total_capitalized * 0.8:
        print("❌ PROBLÈME: Détection insuffisante des noms arabes/maghrébins")
        print("   → Patterns internationaux incomplets pour cette région")
    
    print("\n💡 AMÉLIORATIONS NÉCESSAIRES:")
    print("-" * 30)
    print("1. Étendre les patterns internationaux pour le Maghreb/monde arabe")
    print("2. Réduire le poids de la capitalisation dans le scoring")
    print("3. Ajouter un dictionnaire de noms arabes/berbères")
    print("4. Implémenter spaCy pour la reconnaissance d'entités nommées")
    print("5. Ajouter des patterns pour les particules arabes (Al-, El-, Ben-, etc.)")


def test_arabic_patterns():
    """Test des patterns spécifiques aux noms arabes."""
    
    print("\n🕌 TEST DES PATTERNS ARABES SPÉCIFIQUES")
    print("=" * 60)
    
    # Patterns pour détecter les noms arabes
    arabic_patterns = {
        'prefix_al': r'\b(al|el)-[a-zA-ZÀ-ÿ]+\b',
        'prefix_abd': r'\babd\s+(al|el|allah|rahman|aziz)\b',
        'prefix_ben': r'\bben\s+[a-zA-ZÀ-ÿ]+\b',
        'prefix_ibn': r'\bibn\s+[a-zA-ZÀ-ÿ]+\b',
        'prefix_ould': r'\bould\s+[a-zA-ZÀ-ÿ]+\b',
        'prefix_bint': r'\bbint\s+[a-zA-ZÀ-ÿ]+\b',
        'prefix_sidi': r'\bsidi\s+[a-zA-ZÀ-ÿ]+\b'
    }
    
    test_cases = [
        "mohamed ben ali",
        "fatima al-zahra", 
        "abd el rahman",
        "omar ibn khaldoun",
        "youssef ould mohamed",
        "aisha bint rashid",
        "sidi mohamed"
    ]
    
    import re
    
    print("🔍 Analyse des patterns:")
    for name in test_cases:
        matches = []
        for pattern_name, pattern in arabic_patterns.items():
            if re.search(pattern, name.lower()):
                matches.append(pattern_name)
        
        if matches:
            print(f"✅ '{name}' → Patterns: {matches}")
        else:
            print(f"❌ '{name}' → Aucun pattern détecté")


if __name__ == "__main__":
    test_maghreb_arabic_names()
    test_arabic_patterns()