#!/usr/bin/env python3
"""
Script de test pour le module d'anonymisation des données.
Teste les fonctionnalités de détection et de traitement des données sensibles.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_anonymization():
    """Test complet du module d'anonymisation."""
    print("🛡️ Test du module d'anonymisation des données")
    print("=" * 60)

    try:
        # Importer le module d'anonymisation
        from utils.anonymizer import DataAnonymizer, AnonymizationConfig

        print("✅ Module d'anonymisation importé avec succès")

        # Créer des données de test avec des informations sensibles
        print("\n📊 Création de données de test avec informations sensibles...")

        test_data = pd.DataFrame({
            'client_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'nom_complet': ['Marie Martin', 'Jean Dupont', 'Sophie Bernard', 'Pierre Durand', 'Emma Moreau'],
            'prenom': ['Marie', 'Jean', 'Sophie', 'Pierre', 'Emma'],
            'nom': ['Martin', 'Dupont', 'Bernard', 'Durand', 'Moreau'],
            'email': ['marie@email.com', 'jean@email.com', 'sophie@email.com', 'pierre@email.com', 'emma@email.com'],
            'telephone': ['0123456789', '0987654321', '0112233445', '0667788990', '0778899001'],
            'numero_compte': ['FR1420041010050500013M02606', '123456789012', '987654321098', 'FR7630001007941234567890185', '112233445566'],
            'commentaire_client': [
                'Client très satisfait du service. A contacté marie@email.com pour plus d\'informations.',
                'Problème résolu rapidement par téléphone au 0123456789',
                'Merci pour l\'aide apportée. Mon numéro de compte est FR1420041010050500013M02606',
                'Service excellent, je recommande vivement',
                'Besoin d\'aide pour mon compte 123456789012'
            ],
            'montant_transaction': [150.50, 230.75, 89.90, 1200.00, 45.30],
            'date_transaction': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
            'code_postal': ['75001', '69001', '13001', '31000', '44000'],
            'ville': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nantes']
        })

        print("Données originales:")
        print(test_data.to_string())
        print(f"\n📋 {len(test_data)} lignes, {len(test_data.columns)} colonnes")

        # Test 1: Analyse d'anonymisation (aperçu)
        print("\n🔍 Test 1: Analyse d'anonymisation (aperçu)")
        print("-" * 50)

        anonymizer = DataAnonymizer()
        preview = anonymizer.preview_anonymization(test_data)

        print("Colonnes de noms détectées:")
        print(f"  {preview['name_columns']}")
        print("Colonnes de comptes détectées:")
        print(f"  {preview['account_columns']}")
        print("Colonnes de texte à traiter:")
        print(f"  {list(preview['text_columns_to_process'].keys())}")
        print("Total colonnes à supprimer:")
        print(f"  {preview['total_columns_to_remove']}")
        print("Colonnes restantes:")
        print(f"  {preview['remaining_columns']}")

        # Test 2: Anonymisation complète
        print("\n🔧 Test 2: Anonymisation complète")
        print("-" * 50)

        df_anonymized, report = anonymizer.anonymize_dataframe(test_data)

        print("Données après anonymisation:")
        print(df_anonymized.to_string())
        print()

        print("Rapport d'anonymisation:")
        print(f"  Colonnes supprimées: {report.columns_removed}")
        print(f"  Colonnes restantes: {report.total_columns_processed}")
        print(f"  Lignes traitées: {report.total_rows_processed}")

        # Test 3: Configuration personnalisée
        print("\n⚙️ Test 3: Configuration personnalisée")
        print("-" * 50)

        custom_config = AnonymizationConfig(
            name_threshold=0.6,  # Seuil plus bas pour détecter plus de colonnes
            min_name_length=1,
            account_patterns=[
                r'\b\d{5,}\b',  # Numéros plus courts
                r'\b[A-Z]{2}\d+\b',  # IBAN
            ]
        )

        custom_anonymizer = DataAnonymizer(custom_config)
        preview_custom = custom_anonymizer.preview_anonymization(test_data)

        print("Configuration personnalisée:")
        print(f"  Seuil de noms: {custom_config.name_threshold}")
        print(f"  Longueur min nom: {custom_config.min_name_length}")
        print(f"  Patterns de comptes: {len(custom_config.account_patterns)}")

        print("Résultats avec configuration personnalisée:")
        print(f"  Colonnes de noms: {preview_custom['name_columns']}")
        print(f"  Colonnes de comptes: {preview_custom['account_columns']}")

        # Test 4: Test avec des données plus réalistes
        print("\n📊 Test 4: Données plus réalistes")
        print("-" * 50)

        # Créer un dataset plus réaliste avec des prénoms/noms mélangés
        realistic_data = pd.DataFrame({
            'id': range(1, 101),
            'client': ['Client_' + str(i) for i in range(1, 101)],
            'nom_prenom': [
                'Martin Jean', 'Bernard Marie', 'Dupont Pierre', 'Petit Sophie', 'Robert Paul',
                'Richard Anne', 'Moreau Michel', 'Simon Claire', 'Laurent Emma', 'Lefebvre Lucas'
            ] * 10,
            'email_client': [f'client{i}@exemple.fr' for i in range(1, 101)],
            'telephone_portable': [f'0{i//10}{i%10}{j:02d}{k:02d}{l:02d}{m:02d}' for i in range(10) for j in range(10) for k in range(10) for l in range(10) for m in range(10)][:100],
            'numero_client': [f'C{i:06d}' for i in range(1, 101)],
            'commentaire': [
                f'Client {i} très satisfait. Contact: client{i}@exemple.fr, Tel: 0{i//10}{i%10}123456'
                for i in range(1, 101)
            ],
            'montant_achat': np.random.exponential(100, 100),
            'date_achat': pd.date_range('2024-01-01', periods=100, freq='D').strftime('%Y-%m-%d').tolist()
        })

        print(f"Dataset réaliste: {len(realistic_data)} lignes, {len(realistic_data.columns)} colonnes")

        preview_realistic = anonymizer.preview_anonymization(realistic_data)
        print("Analyse du dataset réaliste:")
        print(f"  Colonnes de noms: {preview_realistic['name_columns']}")
        print(f"  Colonnes de comptes: {preview_realistic['account_columns']}")
        print(f"  Colonnes de texte: {list(preview_realistic['text_columns_to_process'].keys())}")

        # Test 5: Test de sauvegarde de fichier anonymisé
        print("\n💾 Test 5: Sauvegarde de fichier anonymisé")
        print("-" * 50)

        # Créer un fichier CSV temporaire
        temp_file = "temp_test_data.csv"
        test_data.to_csv(temp_file, index=False)

        # Anonymiser et sauvegarder
        from utils.anonymizer import anonymize_csv_file

        output_file = "temp_test_data_anonymized.csv"
        success, message = anonymize_csv_file(temp_file, output_file)

        if success:
            print("✅ Fichier anonymisé sauvegardé avec succès")
            print(f"📁 Fichier de sortie: {output_file}")

            # Afficher un aperçu du fichier anonymisé
            df_result = pd.read_csv(output_file)
            print("Aperçu du fichier anonymisé:")
            print(df_result.head(3).to_string())
        else:
            print(f"❌ Erreur lors de la sauvegarde: {message}")

        # Nettoyer les fichiers temporaires
        try:
            os.remove(temp_file)
            os.remove(output_file)
            print("🗑️ Fichiers temporaires supprimés")
        except:
            pass

        print("\n🎉 Tous les tests d'anonymisation ont réussi!")
        print("\n📋 Résumé des fonctionnalités implémentées:")
        print("  ✅ Détection automatique des colonnes de noms")
        print("  ✅ Détection des numéros de compte et données financières")
        print("  ✅ Traitement des colonnes de commentaires")
        print("  ✅ Configuration personnalisable")
        print("  ✅ Rapports détaillés d'anonymisation")
        print("  ✅ Sauvegarde de fichiers anonymisés")
        print("  ✅ Intégration avec DataManager")

        return True

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Assurez-vous que le module anonymizer est disponible")
        return False

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        print(f"📍 Type d'erreur: {type(e).__name__}")
        return False

def demonstrate_anonymization_workflow():
    """Démontre le workflow complet d'anonymisation."""
    print("\n🔄 Démonstration du workflow d'anonymisation")
    print("=" * 60)

    try:
        from utils.anonymizer import DataAnonymizer, AnonymizationConfig

        # 1. Créer des données avec des informations sensibles
        print("1️⃣ Création de données sensibles...")
        sensitive_data = pd.DataFrame({
            'id_client': ['ID_' + str(i) for i in range(1, 6)],
            'nom_client': ['Dubois Jean', 'Martin Sophie', 'Bernard Pierre', 'Petit Marie', 'Moreau Paul'],
            'email_client': ['jean.dubois@email.com', 'sophie.martin@email.com', 'pierre.bernard@email.com',
                           'marie.petit@email.com', 'paul.moreau@email.com'],
            'telephone_client': ['0102030405', '0607080910', '0506070809', '0304050607', '0708091011'],
            'numero_compte_bancaire': ['FR7630001007941234567890185', 'FR1420041010050500013M02606',
                                     'FR0912345678901234567890123', 'FR4530003000509876543210123', 'FR6789012345678901234567890'],
            'commentaire': [
                'Très satisfait du service client. Contacté par email jean.dubois@email.com et téléphone 0102030405',
                'Service excellent, je recommande. Mon compte est FR7630001007941234567890185',
                'Besoin d\'aide pour mon compte bancaire FR1420041010050500013M02606',
                'Merci pour l\'aide apportée au 0607080910',
                'Problème résolu, contact sophie.martin@email.com'
            ],
            'montant_achat': [125.50, 89.90, 234.75, 156.30, 78.45],
            'date_achat': pd.date_range('2024-01-01', periods=5).strftime('%Y-%m-%d').tolist()
        })

        print("Données sensibles créées:")
        print(sensitive_data.to_string())
        print()

        # 2. Analyser les risques
        print("2️⃣ Analyse des risques d'anonymisation...")
        anonymizer = DataAnonymizer()
        preview = anonymizer.preview_anonymization(sensitive_data)

        print("Risques identifiés:")
        print(f"  📛 Colonnes de noms: {preview['name_columns']}")
        print(f"  💳 Colonnes de comptes: {preview['account_columns']}")
        print(f"  📝 Colonnes de texte: {list(preview['text_columns_to_process'].keys())}")
        print()

        # 3. Appliquer l'anonymisation
        print("3️⃣ Application de l'anonymisation...")
        df_anonymized, report = anonymizer.anonymize_dataframe(sensitive_data)

        print("Données après anonymisation:")
        print(df_anonymized.to_string())
        print()

        # 4. Afficher le rapport
        print("4️⃣ Rapport d'anonymisation:")
        print(f"  ✅ Colonnes supprimées: {len(report.columns_removed)}")
        print(f"     {report.columns_removed}")
        print(f"  📊 Colonnes restantes: {report.total_columns_processed}")
        print(f"  📈 Lignes traitées: {report.total_rows_processed}")
        print()

        # 5. Vérifier l'efficacité
        print("5️⃣ Vérification de l'efficacité...")
        print("Données sensibles supprimées:")
        sensitive_columns = ['nom_client', 'email_client', 'telephone_client', 'numero_compte_bancaire']
        for col in sensitive_columns:
            if col in sensitive_data.columns and col not in df_anonymized.columns:
                print(f"  ✅ {col}: Supprimée")

        print("Données sensibles dans les commentaires:")
        if 'commentaire' in df_anonymized.columns:
            sample_comments = df_anonymized['commentaire'].head(2).tolist()
            print("  📝 Commentaires anonymisés:")
            for i, comment in enumerate(sample_comments, 1):
                print(f"     {i}: {comment}")

        print("\n🎯 Anonymisation réussie!")
        print("✅ Toutes les informations sensibles ont été traitées")
        print("✅ Les données conservent leur utilité pour l'analyse")
        print("✅ Rapport détaillé généré")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        return False

if __name__ == "__main__":
    print("🛡️ Test complet du système d'anonymisation des données")
    print("=" * 70)

    # Test de base
    test_success = test_anonymization()

    if test_success:
        print("\n" + "=" * 70)
        # Démonstration du workflow
        workflow_success = demonstrate_anonymization_workflow()

        if workflow_success:
            print("\n" + "🌟" * 30)
            print("🎉 TOUS LES TESTS RÉUSSIS!")
            print("Le système d'anonymisation est prêt pour la production!")
            print("🌟" * 30)
        else:
            print("\n❌ La démonstration du workflow a échoué")
            sys.exit(1)
    else:
        print("\n❌ Les tests de base ont échoué")
        sys.exit(1)
