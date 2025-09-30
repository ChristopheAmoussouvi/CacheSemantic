"""
Test simple de l'anonymiseur avec spaCy intégré.
Focus sur la détection des noms du Maghreb et arabes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_spacy_anonymizer():
    """Test de l'anonymiseur avec spaCy."""
    
    print("🚀 TEST DE L'ANONYMISEUR AVEC SPACY")
    print("=" * 60)
    
    try:
        from src.utils.spacy_enhanced_anonymizer import SpacyEnhancedDataAnonymizer
        anonymizer = SpacyEnhancedDataAnonymizer()
        print("✅ Anonymiseur spaCy initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return
    
    # Jeu de test focalisé sur les noms du Maghreb/Arabes
    test_cases = [
        # Noms avec capitalisation
        ("Mohamed Ben Ali", "🇲🇦 Nom marocain classique"),
        ("Fatima Al-Zahra", "🇮🇶 Prénom féminin avec Al-"),
        ("Ahmed El Mansouri", "🇹🇳 Nom avec particule El"),
        ("Omar Ibn Khaldoun", "🏛️ Nom historique avec Ibn"),
        ("Aisha Bint Rashid", "👩 Nom féminin avec Bint"),
        ("Sidi Mohamed", "👑 Nom avec titre Sidi"),
        ("Lalla Fatima Zahra", "👸 Nom avec titre féminin"),
        
        # Noms SANS capitalisation (test critique)
        ("mohamed ben ali", "🔽 Sans capitalisation - marocain"),
        ("fatima al-zahra", "🔽 Sans capitalisation - féminin"),
        ("ahmed el mansouri", "🔽 Sans capitalisation - particule"),
        ("aisha bint rashid", "🔽 Sans capitalisation - féminin"),
        ("sidi mohamed", "🔽 Sans capitalisation - titre"),
        ("abu bakr al-razi", "🔽 Sans capitalisation - historique"),
        
        # Noms berbères
        ("Tamazight Amellal", "🏔️ Nom berbère"),
        ("tamazight amellal", "🔽 Berbère sans capitalisation"),
        
        # Contrôles négatifs
        ("bonjour monde", "❌ Phrase simple"),
        ("123456", "❌ Chiffres"),
        ("test@email.com", "❌ Email"),
    ]
    
    print(f"\n📊 ANALYSE DE {len(test_cases)} CAS DE TEST")
    print("=" * 60)
    
    detected_count = 0
    capitalized_detected = 0
    lowercase_detected = 0
    capitalized_total = 0
    lowercase_total = 0
    
    for i, (test_text, description) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. {test_text}")
        print(f"    📝 {description}")
        
        try:
            # Vérifier si la méthode exists
            if hasattr(anonymizer, 'is_name_like_advanced'):
                is_name, score, reasons = anonymizer.is_name_like_advanced(test_text)
            elif hasattr(anonymizer, 'detect_name_patterns'):
                is_name, score, reasons = anonymizer.detect_name_patterns(test_text)
            else:
                # Méthode de fallback
                is_name = anonymizer.is_sensitive_data(test_text, 'name')
                score = 0.5 if is_name else 0.0
                reasons = ['fallback_detection']
            
            status = "✅ DÉTECTÉ" if is_name else "❌ IGNORÉ"
            print(f"    🎯 {status} (score: {score:.3f})")
            
            if reasons and len(reasons) > 0:
                print(f"    🔍 Raisons: {reasons}")
            
            # Statistiques
            if is_name:
                detected_count += 1
            
            # Compter par type de capitalisation
            if test_text[0].isupper():
                capitalized_total += 1
                if is_name:
                    capitalized_detected += 1
            else:
                lowercase_total += 1
                if is_name:
                    lowercase_detected += 1
                    
        except Exception as e:
            print(f"    ❌ ERREUR: {e}")
    
    # Résumé des statistiques
    print(f"\n\n📈 RÉSUMÉ DES RÉSULTATS")
    print("=" * 40)
    print(f"Total détecté: {detected_count}/{len(test_cases)} ({100*detected_count/len(test_cases):.1f}%)")
    
    if capitalized_total > 0:
        print(f"Avec capitalisation: {capitalized_detected}/{capitalized_total} ({100*capitalized_detected/capitalized_total:.1f}%)")
    
    if lowercase_total > 0:
        print(f"Sans capitalisation: {lowercase_detected}/{lowercase_total} ({100*lowercase_detected/lowercase_total:.1f}%)")
    
    # Test des capacités spaCy
    print(f"\n🧠 TEST DES CAPACITÉS SPACY")
    print("-" * 30)
    
    try:
        # Vérifier si spaCy est disponible
        if hasattr(anonymizer, 'nlp_models') and anonymizer.nlp_models:
            print("✅ Modèles spaCy chargés:")
            for model_name, model in anonymizer.nlp_models.items():
                if model:
                    print(f"   📚 {model_name}: {model}")
                else:
                    print(f"   ❌ {model_name}: Non disponible")
        
        # Test NER spaCy sur une phrase complexe
        test_sentence = "Mohamed Ben Ali travaille avec Fatima Al-Zahra à Paris."
        print(f"\n🔍 Test NER sur: '{test_sentence}'")
        
        if hasattr(anonymizer, 'extract_entities_with_spacy'):
            entities = anonymizer.extract_entities_with_spacy(test_sentence)
            if entities:
                print(f"   Entités détectées: {entities}")
            else:
                print("   Aucune entité détectée")
        else:
            print("   Méthode d'extraction NER non disponible")
            
    except Exception as e:
        print(f"   Erreur lors du test spaCy: {e}")
    
    print(f"\n✅ TEST TERMINÉ")
    print("=" * 60)


if __name__ == "__main__":
    test_spacy_anonymizer()