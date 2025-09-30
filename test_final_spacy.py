"""
Test final de l'anonymiseur avec spaCy.
Validation des améliorations pour les noms du Maghreb et arabes.
"""

def test_final_spacy_anonymizer():
    """Test final simplifié de l'anonymiseur avec spaCy."""
    
    print("🚀 TEST FINAL - ANONYMISEUR AVEC SPACY")
    print("=" * 60)
    
    try:
        from src.utils.spacy_enhanced_anonymizer import SpacyEnhancedDataAnonymizer
        anonymizer = SpacyEnhancedDataAnonymizer()
        print("✅ Anonymiseur spaCy initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return
    
    # Cas de test critiques pour les noms du Maghreb/Arabes
    test_cases = [
        # Avec capitalisation
        ("Mohamed Ben Ali", "🇲🇦 Nom marocain"),
        ("Fatima Al-Zahra", "🇮🇶 Prénom féminin"),
        ("Ahmed El Mansouri", "🇹🇳 Particule El"),
        ("Sidi Mohamed", "👑 Titre Sidi"),
        
        # SANS capitalisation (défi principal)
        ("mohamed ben ali", "🔽 Sans capitalisation"),
        ("fatima al-zahra", "🔽 Sans capitalisation"),
        ("ahmed el mansouri", "🔽 Sans capitalisation"),
        ("sidi mohamed", "🔽 Sans capitalisation"),
        
        # Contrôles
        ("bonjour monde", "❌ Phrase"),
        ("123456", "❌ Chiffres"),
    ]
    
    print(f"\n📊 TEST SUR {len(test_cases)} CAS")
    print("-" * 40)
    
    results = []
    
    for i, (text, desc) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. {text}")
        print(f"    📝 {desc}")
        
        try:
            is_name, score, reasons = anonymizer.is_name_like_advanced_spacy(text)
            status = "✅ DÉTECTÉ" if is_name else "❌ IGNORÉ"
            print(f"    🎯 {status} (score: {score:.3f})")
            
            # Afficher quelques raisons principales
            if reasons and len(reasons) > 0:
                main_reasons = reasons[:3]  # Prendre les 3 premières
                print(f"    🔍 Raisons: {main_reasons}")
            
            results.append((text, is_name, score, desc))
            
        except Exception as e:
            print(f"    ❌ ERREUR: {e}")
            results.append((text, False, 0.0, desc))
    
    # Analyse des résultats
    print(f"\n\n📈 RÉSULTATS FINAUX")
    print("=" * 40)
    
    detected = [r for r in results if r[1]]  # is_name = True
    
    # Compter par catégorie
    with_caps = [r for r in results if r[0][0].isupper()]
    without_caps = [r for r in results if r[0][0].islower()]
    
    with_caps_detected = [r for r in with_caps if r[1]]
    without_caps_detected = [r for r in without_caps if r[1]]
    
    print(f"Total détecté: {len(detected)}/{len(results)} ({100*len(detected)/len(results):.1f}%)")
    
    if with_caps:
        print(f"Avec capitalisation: {len(with_caps_detected)}/{len(with_caps)} ({100*len(with_caps_detected)/len(with_caps):.1f}%)")
    
    if without_caps:
        print(f"Sans capitalisation: {len(without_caps_detected)}/{len(without_caps)} ({100*len(without_caps_detected)/len(without_caps):.1f}%)")
    
    # Vérification spécifique des noms du Maghreb
    maghreb_names = [r for r in results if any(x in r[3] for x in ['🇲🇦', '🇮🇶', '🇹🇳', '👑', '🔽'])]
    maghreb_detected = [r for r in maghreb_names if r[1]]
    
    if maghreb_names:
        print(f"Noms du Maghreb/Arabes: {len(maghreb_detected)}/{len(maghreb_names)} ({100*len(maghreb_detected)/len(maghreb_names):.1f}%)")
    
    # Statut final
    if len(detected) >= 8:  # Au moins 80% des cas réels détectés
        print(f"\n🎉 SUCCÈS: L'anonymiseur détecte efficacement les noms du Maghreb!")
    else:
        print(f"\n⚠️  AMÉLIORATION NÉCESSAIRE: Détection insuffisante")
    
    print(f"\n✅ TEST TERMINÉ")
    print("=" * 60)


if __name__ == "__main__":
    test_final_spacy_anonymizer()