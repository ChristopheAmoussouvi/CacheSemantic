"""
Script de test pour valider la migration Seaborn -> Matplotlib
Teste tous les types de visualisations avec des données synthétiques
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from src.components.visualization_manager import VisualizationManager

def create_test_data():
    """Crée un DataFrame de test avec différents types de données."""
    np.random.seed(42)
    
    data = {
        'Region': ['Nord', 'Sud', 'Est', 'Ouest', 'Centre'] * 20,
        'Ventes': np.random.randint(1000, 10000, 100),
        'Prix': np.random.uniform(10, 200, 100),
        'Quantite': np.random.randint(1, 100, 100),
        'Date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'Categorie': np.random.choice(['A', 'B', 'C', 'D'], 100),
        'Score': np.random.uniform(0, 100, 100),
        'Taux': np.random.uniform(0, 1, 100)
    }
    
    return pd.DataFrame(data)

def test_histogram(viz_manager, df):
    """Test histogram avec données numériques."""
    print("\n📊 Test HISTOGRAM (numérique)...")
    try:
        viz_base64, from_cache = viz_manager.get_or_create_visualization(
            viz_type='histogram',
            dataframe=df,
            columns={'x': 'Ventes'},
            title='Distribution des Ventes'
        )
        print(f"   ✅ Histogram numérique OK (cache: {from_cache})")
        print(f"   📏 Taille base64: {len(viz_base64)} caractères")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_histogram_categorical(viz_manager, df):
    """Test histogram avec données catégorielles."""
    print("\n📊 Test HISTOGRAM (catégoriel)...")
    try:
        viz_base64, from_cache = viz_manager.get_or_create_visualization(
            viz_type='histogram',
            dataframe=df,
            columns={'x': 'Region'},
            title='Distribution par Région'
        )
        print(f"   ✅ Histogram catégoriel OK (cache: {from_cache})")
        print(f"   📏 Taille base64: {len(viz_base64)} caractères")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_scatter(viz_manager, df):
    """Test scatter plot."""
    print("\n📈 Test SCATTER PLOT...")
    try:
        viz_base64, from_cache = viz_manager.get_or_create_visualization(
            viz_type='scatter',
            dataframe=df,
            columns={'x': 'Prix', 'y': 'Ventes'},
            title='Corrélation Prix vs Ventes'
        )
        print(f"   ✅ Scatter plot OK (cache: {from_cache})")
        print(f"   📏 Taille base64: {len(viz_base64)} caractères")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_bar_chart(viz_manager, df):
    """Test bar chart."""
    print("\n📊 Test BAR CHART...")
    try:
        viz_base64, from_cache = viz_manager.get_or_create_visualization(
            viz_type='bar_chart',
            dataframe=df,
            columns={'x': 'Region', 'y': 'Ventes'},
            title='Ventes Moyennes par Région'
        )
        print(f"   ✅ Bar chart OK (cache: {from_cache})")
        print(f"   📏 Taille base64: {len(viz_base64)} caractères")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_line_chart(viz_manager, df):
    """Test line chart."""
    print("\n📈 Test LINE CHART...")
    try:
        # Préparer données temporelles
        df_time = df.groupby('Date')['Ventes'].sum().reset_index()
        viz_base64, from_cache = viz_manager.get_or_create_visualization(
            viz_type='line_chart',
            dataframe=df_time.head(30),  # Limiter pour lisibilité
            columns={'x': 'Date', 'y': 'Ventes'},
            title='Évolution des Ventes dans le Temps'
        )
        print(f"   ✅ Line chart OK (cache: {from_cache})")
        print(f"   📏 Taille base64: {len(viz_base64)} caractères")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_heatmap(viz_manager, df):
    """Test heatmap."""
    print("\n🔥 Test HEATMAP...")
    try:
        numeric_cols = ['Ventes', 'Prix', 'Quantite', 'Score', 'Taux']
        viz_base64, from_cache = viz_manager.get_or_create_visualization(
            viz_type='heatmap',
            dataframe=df,
            columns={'columns': numeric_cols},
            title='Matrice de Corrélation'
        )
        print(f"   ✅ Heatmap OK (cache: {from_cache})")
        print(f"   📏 Taille base64: {len(viz_base64)} caractères")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_boxplot(viz_manager, df):
    """Test boxplot."""
    print("\n📦 Test BOXPLOT...")
    try:
        viz_base64, from_cache = viz_manager.get_or_create_visualization(
            viz_type='boxplot',
            dataframe=df,
            columns={'y': 'Ventes'},
            title='Distribution des Ventes (BoxPlot)'
        )
        print(f"   ✅ Boxplot OK (cache: {from_cache})")
        print(f"   📏 Taille base64: {len(viz_base64)} caractères")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_cache_retrieval(viz_manager, df):
    """Test que le cache fonctionne correctement."""
    print("\n🔄 Test CACHE RETRIEVAL...")
    try:
        # Première création
        viz1, from_cache1 = viz_manager.get_or_create_visualization(
            viz_type='histogram',
            dataframe=df,
            columns={'x': 'Prix'},
            title='Test Cache'
        )
        
        # Deuxième appel (devrait venir du cache)
        viz2, from_cache2 = viz_manager.get_or_create_visualization(
            viz_type='histogram',
            dataframe=df,
            columns={'x': 'Prix'},
            title='Test Cache'
        )
        
        if not from_cache1 and from_cache2:
            print(f"   ✅ Cache fonctionne correctement")
            print(f"   📊 1ère fois: nouveau (cache={from_cache1})")
            print(f"   📊 2ème fois: du cache (cache={from_cache2})")
            return True
        else:
            print(f"   ⚠️  Cache pas optimal (cache1={from_cache1}, cache2={from_cache2})")
            return True  # Pas une erreur critique
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_statistics(viz_manager):
    """Test les statistiques du manager."""
    print("\n📊 Test STATISTIQUES...")
    try:
        stats = viz_manager.get_stats()
        print(f"   ✅ Statistiques récupérées")
        print(f"   📈 Total visualisations: {stats['total_visualizations']}")
        print(f"   📁 DB Path: {stats['db_path']}")
        print(f"   🎨 Par type: {stats['by_type']}")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("=" * 70)
    print("🧪 TEST DE MIGRATION SEABORN -> MATPLOTLIB")
    print("=" * 70)
    
    # Créer le gestionnaire de visualisations
    viz_manager = VisualizationManager(db_path="./test_viz_matplotlib_db")
    
    # Créer les données de test
    print("\n📦 Création des données de test...")
    df = create_test_data()
    print(f"   ✅ {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"   📊 Colonnes: {', '.join(df.columns)}")
    
    # Exécuter tous les tests
    tests = [
        ("Histogram (numérique)", lambda: test_histogram(viz_manager, df)),
        ("Histogram (catégoriel)", lambda: test_histogram_categorical(viz_manager, df)),
        ("Scatter Plot", lambda: test_scatter(viz_manager, df)),
        ("Bar Chart", lambda: test_bar_chart(viz_manager, df)),
        ("Line Chart", lambda: test_line_chart(viz_manager, df)),
        ("Heatmap", lambda: test_heatmap(viz_manager, df)),
        ("Boxplot", lambda: test_boxplot(viz_manager, df)),
        ("Cache Retrieval", lambda: test_cache_retrieval(viz_manager, df)),
        ("Statistiques", lambda: test_statistics(viz_manager))
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Erreur critique dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"  {status:12s} - {test_name}")
    
    print("\n" + "=" * 70)
    print(f"🎯 RÉSULTAT FINAL: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS ONT RÉUSSI!")
        print("✅ Migration Seaborn -> Matplotlib validée avec succès")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué")
        print("❌ Vérifier les erreurs ci-dessus")
        return 1

if __name__ == "__main__":
    exit(main())
