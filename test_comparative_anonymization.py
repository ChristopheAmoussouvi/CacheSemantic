"""
Test comparatif entre l'anonymiseur enhanced et l'anonymiseur avec spaCy.
Évalue les performances de détection sur différents types de noms.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.enhanced_anonymizer import EnhancedDataAnonymizer, EnhancedAnonymizationConfig

def test_comparative_anonymization():
    """Test comparatif des deux anonymiseurs."""
    
    print("🔍 COMPARAISON DES ANONYMISEURS")
    print("=" * 80)
    
    # Initialisation des anonymiseurs
    print("\n📚 Initialisation des modules...")
    enhanced_config = EnhancedAnonymizationConfig(
        name_threshold_strict=0.7,
        name_threshold_loose=0.5,
        name_entropy_threshold=2.0,
        detect_uncommon_names=True
    )
    enhanced_anonymizer = EnhancedDataAnonymizer(enhanced_config)
    
    try:
        from src.utils.spacy_enhanced_anonymizer import SpacyEnhancedAnonymizer
        spacy_anonymizer = SpacyEnhancedAnonymizer()
        spacy_available = True
        print("✅ Anonymiseur spaCy initialisé avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation spaCy: {e}")
        spacy_available = False
        return
    
    print("✅ Anonymiseur enhanced initialisé avec succès")
    
    # Jeu de test diversifié
    test_cases = [
        # Noms français classiques
        ("Marie Dubois", "Nom français féminin classique"),
        ("Jean-Pierre Martin", "Nom composé français"),
        ("Dr. Philippe Durand", "Nom avec titre"),
        
        # Noms arabes/maghrébins avec capitalisation
        ("Mohamed Ben Ali", "Nom marocain classique"),
        ("Fatima Al-Zahra", "Prénom féminin avec Al-"),
        ("Ahmed El Mansouri", "Nom avec particule El"),
        ("Omar Ibn Khaldoun", "Nom historique avec Ibn"),
        ("Aisha Bint Rashid", "Nom féminin avec Bint"),
        ("Sidi Mohamed", "Nom avec titre Sidi"),
        ("Lalla Fatima Zahra", "Nom avec titre féminin"),
        ("Moulay Hassan", "Nom royal"),
        
        # Noms arabes/maghrébins SANS capitalisation (test critique)
        ("mohamed ben ali", "Sans capitalisation - marocain"),
        ("fatima al-zahra", "Sans capitalisation - féminin"),
        ("ahmed el mansouri", "Sans capitalisation - particule"),
        ("omar ibn khaldoun", "Sans capitalisation - historique"),
        ("aisha bint rashid", "Sans capitalisation - féminin"),
        ("sidi mohamed", "Sans capitalisation - titre"),
        ("abu bakr al-razi", "Sans capitalisation - historique"),
        ("moulay hassan", "Sans capitalisation - royal"),
        
        # Noms berbères/amazighs
        ("Tamazight Amellal", "Nom berbère"),
        ("tamazight amellal", "Berbère sans capitalisation"),
        
        # Noms internationaux
        ("Vladimir Putin", "Nom russe"),
        ("Xi Jinping", "Nom chinois"),
        ("Nelson Mandela", "Nom africain"),
        
        # Cas limite et non-noms
        ("bonjour monde", "Phrase simple"),
        ("123456", "Chiffres"),
        ("test@email.com", "Email"),
        ("ABC-123", "Code"),
        ("Paris France", "Lieux (peut être détecté comme nom)")
    ]
    
    print(f"\n📊 ANALYSE COMPARATIVE SUR {len(test_cases)} CAS DE TEST")
    print("=" * 80)
    
    results_enhanced = []
    results_spacy = []
    
    for i, (test_text, description) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. Test: '{test_text}' ({description})")
        print("-" * 60)
        
        # Test avec Enhanced Anonymizer
        try:
            is_name_enh, score_enh, reasons_enh = enhanced_anonymizer.is_name_like_advanced(test_text)
            enhanced_result = {
                'detected': is_name_enh,
                'score': score_enh,
                'reasons': reasons_enh,
                'error': None
            }
            status_enh = "✅ DÉTECTÉ" if is_name_enh else "❌ IGNORÉ"
            print(f"    Enhanced: {status_enh} (score: {score_enh:.3f})")
            if reasons_enh:
                print(f"              Raisons: {reasons_enh}")
        except Exception as e:
            enhanced_result = {'detected': False, 'score': 0.0, 'reasons': [], 'error': str(e)}
            print(f"    Enhanced: ❌ ERREUR ({e})")
        
        results_enhanced.append(enhanced_result)
        
        # Test avec SpaCy Anonymizer
        if spacy_available:
            try:
                is_name_sp, score_sp, reasons_sp = spacy_anonymizer.is_name_like_advanced(test_text)
                spacy_result = {
                    'detected': is_name_sp,
                    'score': score_sp,
                    'reasons': reasons_sp,
                    'error': None
                }
                status_sp = "✅ DÉTECTÉ" if is_name_sp else "❌ IGNORÉ"
                print(f"    spaCy:    {status_sp} (score: {score_sp:.3f})")
                if reasons_sp:
                    print(f"              Raisons: {reasons_sp}")
                
                # Comparaison
                if is_name_enh == is_name_sp:
                    print(f"    🎯 ACCORD: Les deux anonymiseurs sont d'accord")
                else:
                    print(f"    ⚠️  DÉSACCORD: Enhanced={is_name_enh}, spaCy={is_name_sp}")
                    
            except Exception as e:
                spacy_result = {'detected': False, 'score': 0.0, 'reasons': [], 'error': str(e)}
                print(f"    spaCy:    ❌ ERREUR ({e})")
        else:
            spacy_result = {'detected': False, 'score': 0.0, 'reasons': [], 'error': 'spaCy non disponible'}
        
        results_spacy.append(spacy_result)
    
    # Analyse des résultats
    print("\n\n📈 ANALYSE STATISTIQUE DES RÉSULTATS")
    print("=" * 80)
    
    # Compter les détections
    enhanced_detections = sum(1 for r in results_enhanced if r['detected'] and not r['error'])
    spacy_detections = sum(1 for r in results_spacy if r['detected'] and not r['error'])
    
    # Compter les accords/désaccords
    agreements = 0
    disagreements = 0
    
    for enh, sp in zip(results_enhanced, results_spacy):
        if not enh['error'] and not sp['error']:
            if enh['detected'] == sp['detected']:
                agreements += 1
            else:
                disagreements += 1
    
    print(f"\n🎯 DÉTECTIONS:")
    print(f"   Enhanced Anonymizer: {enhanced_detections}/{len(test_cases)} ({100*enhanced_detections/len(test_cases):.1f}%)")
    print(f"   spaCy Anonymizer:    {spacy_detections}/{len(test_cases)} ({100*spacy_detections/len(test_cases):.1f}%)")
    
    print(f"\n🤝 CONCORDANCE:")
    print(f"   Accords:     {agreements}")
    print(f"   Désaccords:  {disagreements}")
    if agreements + disagreements > 0:
        concordance = 100 * agreements / (agreements + disagreements)
        print(f"   Taux de concordance: {concordance:.1f}%")
    
    # Analyse spécifique pour les noms du Maghreb
    print(f"\n🌍 ANALYSE SPÉCIFIQUE - NOMS DU MAGHREB/ARABES:")
    print("-" * 50)
    
    maghreb_cases = [
        (i, case) for i, case in enumerate(test_cases) 
        if any(keyword in case[1].lower() for keyword in ['marocain', 'arabe', 'maghreb', 'berbère', 'féminin', 'historique', 'royal'])
    ]
    
    maghreb_enhanced = sum(1 for i, _ in maghreb_cases if results_enhanced[i]['detected'] and not results_enhanced[i]['error'])
    maghreb_spacy = sum(1 for i, _ in maghreb_cases if results_spacy[i]['detected'] and not results_spacy[i]['error'])
    
    print(f"   Cas du Maghreb/Arabes: {len(maghreb_cases)} tests")
    print(f"   Enhanced: {maghreb_enhanced}/{len(maghreb_cases)} ({100*maghreb_enhanced/len(maghreb_cases):.1f}%)")
    print(f"   spaCy:    {maghreb_spacy}/{len(maghreb_cases)} ({100*maghreb_spacy/len(maghreb_cases):.1f}%)")
    
    # Test sans capitalisation
    lowercase_cases = [(i, case) for i, case in enumerate(test_cases) if case[0].islower()]
    
    if lowercase_cases:
        print(f"\n📝 ANALYSE SPÉCIFIQUE - NOMS SANS CAPITALISATION:")
        print("-" * 50)
        
        lowercase_enhanced = sum(1 for i, _ in lowercase_cases if results_enhanced[i]['detected'] and not results_enhanced[i]['error'])
        lowercase_spacy = sum(1 for i, _ in lowercase_cases if results_spacy[i]['detected'] and not results_spacy[i]['error'])
        
        print(f"   Cas sans capitalisation: {len(lowercase_cases)} tests")
        print(f"   Enhanced: {lowercase_enhanced}/{len(lowercase_cases)} ({100*lowercase_enhanced/len(lowercase_cases):.1f}%)")
        print(f"   spaCy:    {lowercase_spacy}/{len(lowercase_cases)} ({100*lowercase_spacy/len(lowercase_cases):.1f}%)")
    
    # Statistiques des modules
    print(f"\n📊 STATISTIQUES DES MODULES:")
    print("-" * 40)
    
    try:
        enh_stats = enhanced_anonymizer.get_statistics()
        print("\n🔧 Enhanced Anonymizer:")
        for key, value in enh_stats.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"   Erreur récupération stats Enhanced: {e}")
    
    if spacy_available:
        try:
            sp_stats = spacy_anonymizer.get_statistics()
            print("\n🚀 spaCy Anonymizer:")
            for key, value in sp_stats.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"   Erreur récupération stats spaCy: {e}")
    
    print(f"\n✅ ANALYSE COMPARATIVE TERMINÉE")
    print("=" * 80)


if __name__ == "__main__":
    test_comparative_anonymization()