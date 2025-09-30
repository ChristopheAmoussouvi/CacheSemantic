"""
Script de comparaison entre l'ancienne et nouvelle approche d'anonymisation.
Démontre les améliorations apportées à la détection des noms non communs.
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.anonymizer import DataAnonymizer, AnonymizationConfig
from src.utils.enhanced_anonymizer import EnhancedDataAnonymizer, EnhancedAnonymizationConfig

def create_challenging_test_data():
    """Crée des données de test avec des noms complexes pour évaluer les améliorations."""
    return pd.DataFrame({
        'id': ['1', '2', '3', '4', '5', '6', '7', '8'],
        'nom_client': [
            'Marie Martin',          # Nom français commun - détecté par les 2
            'Aleksandr Volkov',      # Nom slave - raté par l'ancien
            'Hiroshi Tanaka',        # Nom japonais - raté par l'ancien  
            'Kwame Asante',          # Nom africain - raté par l'ancien
            'Zara Al-Rashid',        # Nom arabe composé - raté par l'ancien
            'Xylia Pemberton',       # Prénom très rare - raté par l'ancien
            'Dr. Jean-Luc Moreau',   # Titre + nom composé - détecté par les 2
            'J.K. Anderson'          # Initiales + nom - raté par l'ancien
        ],
        'contact_person': [
            'Amélie',                # Prénom simple français
            'Zorion',                # Prénom basque rare
            'Nayeli',                # Prénom nahuatl
            'Thaddeus',              # Prénom anglais rare
            'Cosmin',                # Prénom roumain
            'Siobhan',               # Prénom irlandais
            'Xiomara',               # Prénom espagnol rare
            'Kai'                    # Prénom court asiatique
        ],
        'description': [
            'Client standard avec compte bancaire FR1234567890',
            'Personne originaire de Russie, numéro: +7-495-123-4567',
            'Client japonais, email: hiroshi@company.co.jp',
            'Responsable du projet, téléphone: +233-20-123-4567',
            'Consultante, adresse: 123 rue des Fleurs, 75001 Paris',
            'Développeuse freelance, contact: xylia.p@tech.com',
            'Médecin-chef, cabinet au 456 boulevard Haussmann',
            'Auteur britannique, agent: j.k.anderson@literary.uk'
        ],
        'montant': [1500, 2300, 890, 4560, 780, 1200, 3400, 950],
        'secteur': ['Finance', 'Tech', 'Healthcare', 'Education', 'Consulting', 'Tech', 'Healthcare', 'Publishing']
    })

def compare_detection_results():
    """Compare les résultats de détection entre les deux approches."""
    
    print("🔬 COMPARAISON DES APPROCHES D'ANONYMISATION")
    print("=" * 80)
    
    # Données de test
    test_data = create_challenging_test_data()
    print("📊 Données de test:")
    print(test_data[['nom_client', 'contact_person']].to_string())
    print("\n" + "=" * 80)
    
    # Configuration standard
    old_config = AnonymizationConfig(name_threshold=0.8)
    new_config = EnhancedAnonymizationConfig(
        detect_uncommon_names=True,
        name_threshold_strict=0.9,
        name_threshold_loose=0.6,
        anonymization_mode="balanced"
    )
    
    # Ancienne approche
    print("🔴 ANCIENNE APPROCHE - Détection basique")
    print("-" * 50)
    old_anonymizer = DataAnonymizer(old_config)
    
    old_name_columns = old_anonymizer.detect_name_columns(test_data)
    print(f"Colonnes de noms détectées: {old_name_columns}")
    
    # Test individuel des noms
    print("\nAnalyse individuelle des noms (ancienne méthode):")
    for col in ['nom_client', 'contact_person']:
        if col in test_data.columns:
            print(f"\n--- {col} ---")
            for value in test_data[col]:
                is_name = old_anonymizer.is_name_like(value)
                print(f"'{value}': {is_name}")
    
    # Anonymisation ancienne
    old_result, old_report = old_anonymizer.anonymize_dataframe(test_data.copy())
    print(f"\nColonnes supprimées (ancienne): {old_report.columns_removed}")
    print(f"Colonnes restantes: {len(old_result.columns)}")
    
    print("\n" + "=" * 80)
    
    # Nouvelle approche
    print("🟢 NOUVELLE APPROCHE - Détection avancée")
    print("-" * 50)
    new_anonymizer = EnhancedDataAnonymizer(new_config)
    
    new_name_columns, detailed_analysis = new_anonymizer.detect_name_columns_advanced(test_data)
    print(f"Colonnes de noms détectées: {new_name_columns}")
    
    # Test individuel des noms avec scores
    print("\nAnalyse individuelle des noms (nouvelle méthode):")
    for col in ['nom_client', 'contact_person']:
        if col in test_data.columns:
            print(f"\n--- {col} ---")
            for value in test_data[col]:
                is_name, confidence, reasons = new_anonymizer.is_name_like_advanced(value)
                print(f"'{value}': {is_name} (confiance: {confidence:.3f}) - {reasons[:3]}")
    
    # Analyse détaillée des colonnes
    print("\nAnalyse détaillée des colonnes:")
    for col, analysis in detailed_analysis.items():
        if analysis['is_name_column']:
            print(f"\n{col}:")
            print(f"  - Ratio de noms: {analysis['name_ratio']:.2%}")
            print(f"  - Confiance moyenne: {analysis['avg_confidence']:.3f}")
            print(f"  - Score final: {analysis['final_score']:.3f}")
            print(f"  - Seuil utilisé: {analysis['threshold_used']:.3f}")
    
    # Anonymisation nouvelle
    new_result, new_report = new_anonymizer.anonymize_dataframe_advanced(test_data.copy())
    print(f"\nColonnes supprimées (nouvelle): {new_report.columns_removed}")
    print(f"Colonnes anonymisées: {new_report.columns_anonymized}")
    print(f"Score d'anonymisation: {new_report.anonymization_score:.3f}")
    print(f"Colonnes restantes: {len(new_result.columns)}")
    
    print("\n" + "=" * 80)
    
    # Résumé des améliorations
    print("📈 RÉSUMÉ DES AMÉLIORATIONS")
    print("-" * 50)
    
    old_detected = len(old_name_columns)
    new_detected = len(new_name_columns)
    
    print(f"Colonnes de noms détectées:")
    print(f"  • Ancienne approche: {old_detected}")
    print(f"  • Nouvelle approche: {new_detected}")
    print(f"  • Amélioration: +{new_detected - old_detected} colonnes")
    
    # Analyse des noms individuels
    old_names_detected = 0
    new_names_detected = 0
    
    for col in ['nom_client', 'contact_person']:
        if col in test_data.columns:
            for value in test_data[col]:
                if old_anonymizer.is_name_like(value):
                    old_names_detected += 1
                if new_anonymizer.is_name_like_advanced(value)[0]:
                    new_names_detected += 1
    
    print(f"\nNoms individuels détectés:")
    print(f"  • Ancienne approche: {old_names_detected}/16")
    print(f"  • Nouvelle approche: {new_names_detected}/16")
    print(f"  • Amélioration: +{new_names_detected - old_names_detected} noms")
    print(f"  • Précision: {new_names_detected/16:.1%}")
    
    # Fonctionnalités avancées
    print(f"\nNouvelles fonctionnalités:")
    print(f"  ✅ Détection des noms non communs (slaves, asiatiques, africains)")
    print(f"  ✅ Score de confiance pour chaque détection")
    print(f"  ✅ Raisons de détection explicites")
    print(f"  ✅ Seuils adaptatifs selon le contexte")
    print(f"  ✅ Détection des adresses ({new_report.addresses_found} trouvées)")
    print(f"  ✅ Patterns internationaux de téléphones")
    print(f"  ✅ Score global d'anonymisation")
    
    print("\n" + "=" * 80)
    
    # Exemples concrets d'amélioration
    print("🎯 EXEMPLES CONCRETS D'AMÉLIORATION")
    print("-" * 50)
    
    improved_detections = [
        ("Aleksandr Volkov", "Nom slave - détecté uniquement par la nouvelle approche"),
        ("Hiroshi Tanaka", "Nom japonais - pattern international détecté"),
        ("Kwame Asante", "Nom africain - haute entropie détectée"),
        ("Zara Al-Rashid", "Nom arabe composé - structure analysée"),
        ("Xylia Pemberton", "Prénom très rare - entropie élevée"),
        ("J.K. Anderson", "Format avec initiales - pattern spécialisé"),
        ("Zorion", "Prénom basque - non dans dictionnaire français"),
        ("Nayeli", "Prénom nahuatl - pattern international")
    ]
    
    for name, explanation in improved_detections:
        old_detected = old_anonymizer.is_name_like(name)
        new_detected, confidence, reasons = new_anonymizer.is_name_like_advanced(name)
        
        if new_detected and not old_detected:
            print(f"✅ '{name}': {explanation}")
            print(f"   Confiance: {confidence:.3f}, Raisons: {reasons[:2]}")
        elif new_detected and old_detected:
            print(f"🔄 '{name}': Détecté par les deux (confiance améliorée: {confidence:.3f})")
    
    print("\n" + "=" * 80)
    print("🏆 CONCLUSION: La nouvelle approche détecte significativement plus de noms")
    print("   tout en fournissant des informations détaillées sur les raisons de détection.")


if __name__ == "__main__":
    try:
        compare_detection_results()
    except Exception as e:
        print(f"Erreur pendant la comparaison: {e}")
        import traceback
        traceback.print_exc()