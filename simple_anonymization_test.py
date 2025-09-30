#!/usr/bin/env python3
"""
Test simple du module d'anonymisation
"""

import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🛡️ Test simple d'anonymisation")

    # Create test data
    test_data = pd.DataFrame({
        'nom': ['Marie Martin', 'Jean Dupont', 'Sophie Bernard'],
        'email': ['marie@email.com', 'jean@email.com', 'sophie@email.com'],
        'compte': ['FR1420041010050500013M02606', '123456789012', '987654321098'],
        'commentaire': [
            'Client satisfait. Email: marie@email.com',
            'Problème résolu',
            'Merci pour l\'aide'
        ],
        'montant': [100, 200, 150]
    })

    print("Données originales:")
    print(test_data)
    print()

    try:
        from utils.anonymizer import DataAnonymizer

        anonymizer = DataAnonymizer()
        preview = anonymizer.preview_anonymization(test_data)

        print("Analyse:")
        print(f"Colonnes de noms: {preview['name_columns']}")
        print(f"Colonnes de comptes: {preview['account_columns']}")
        print()

        df_anonymized, report = anonymizer.anonymize_dataframe(test_data)

        print("Données anonymisées:")
        print(df_anonymized)
        print()

        print("Rapport:")
        print(f"Colonnes supprimées: {report.columns_removed}")
        print(f"Colonnes restantes: {report.total_columns_processed}")

        print("\n✅ Test réussi!")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
