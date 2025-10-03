"""
Script pour compter le nombre de visualisations dans la base de données ChromaDB.
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def count_visualizations():
    """Compte les visualisations stockées dans ChromaDB."""
    
    print("=" * 70)
    print("📊 ANALYSE DE LA BASE DE DONNÉES CHROMADB")
    print("=" * 70)
    
    try:
        import chromadb
        from pathlib import Path
        
        # Chemin vers la base de données
        db_path = Path("./chroma_db")
        
        if not db_path.exists():
            print("\n❌ La base de données ChromaDB n'existe pas encore.")
            print(f"   Chemin recherché: {db_path.absolute()}")
            return
        
        print(f"\n📁 Base de données trouvée: {db_path.absolute()}")
        
        # Initialiser le client ChromaDB
        client = chromadb.PersistentClient(path=str(db_path))
        
        # Lister toutes les collections
        collections = client.list_collections()
        
        print(f"\n📚 Collections trouvées: {len(collections)}")
        print("-" * 70)
        
        total_documents = 0
        total_visualizations = 0
        
        for collection in collections:
            print(f"\n🗂️  Collection: '{collection.name}'")
            
            # Récupérer le nombre d'éléments
            count = collection.count()
            total_documents += count
            
            print(f"   📄 Nombre total de documents: {count}")
            
            if count > 0:
                # Récupérer un échantillon pour analyser les métadonnées
                sample = collection.get(limit=min(5, count), include=['metadatas'])
                
                # Compter les visualisations
                viz_count = 0
                viz_types = set()
                
                if sample and 'metadatas' in sample:
                    for metadata in sample['metadatas']:
                        if metadata:
                            # Vérifier si c'est une visualisation
                            if 'viz_type' in metadata or 'visualization' in metadata:
                                viz_count += 1
                                if 'viz_type' in metadata:
                                    viz_types.add(metadata['viz_type'])
                
                if viz_count > 0:
                    # Estimer le nombre total de visualisations
                    estimated_viz = int((viz_count / len(sample['metadatas'])) * count)
                    total_visualizations += estimated_viz
                    
                    print(f"   📈 Visualisations estimées: {estimated_viz}")
                    if viz_types:
                        print(f"   🎨 Types trouvés dans l'échantillon: {', '.join(viz_types)}")
                else:
                    print(f"   ℹ️  Pas de visualisations détectées dans l'échantillon")
                
                # Afficher quelques exemples de métadonnées
                if sample and 'metadatas' in sample and sample['metadatas']:
                    print(f"\n   📋 Exemple de métadonnées:")
                    first_meta = sample['metadatas'][0]
                    for key, value in list(first_meta.items())[:5]:
                        print(f"      • {key}: {value}")
        
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ GLOBAL")
        print("=" * 70)
        print(f"   📚 Collections: {len(collections)}")
        print(f"   📄 Documents totaux: {total_documents}")
        print(f"   📈 Visualisations estimées: {total_visualizations}")
        
        # Vérifier spécifiquement la collection de Q&A
        print("\n" + "=" * 70)
        print("🔍 RECHERCHE SPÉCIFIQUE - QUESTIONS/RÉPONSES AVEC VISUALISATIONS")
        print("=" * 70)
        
        for collection in collections:
            if 'qa' in collection.name.lower() or 'question' in collection.name.lower():
                print(f"\n📊 Analyse détaillée de '{collection.name}':")
                
                # Récupérer tous les documents
                all_docs = collection.get(include=['metadatas', 'documents'])
                
                if all_docs and 'metadatas' in all_docs:
                    viz_with_type = {}
                    questions_with_viz = 0
                    
                    for metadata in all_docs['metadatas']:
                        if metadata and 'viz_type' in metadata:
                            questions_with_viz += 1
                            viz_type = metadata['viz_type']
                            viz_with_type[viz_type] = viz_with_type.get(viz_type, 0) + 1
                    
                    print(f"\n   ✅ Questions avec visualisations: {questions_with_viz}")
                    
                    if viz_with_type:
                        print(f"\n   📊 Répartition par type de visualisation:")
                        for viz_type, count in sorted(viz_with_type.items(), key=lambda x: x[1], reverse=True):
                            percentage = (count / questions_with_viz) * 100
                            print(f"      • {viz_type}: {count} ({percentage:.1f}%)")
        
        print("\n" + "=" * 70)
        print("✅ ANALYSE TERMINÉE")
        print("=" * 70)
        
    except ImportError as e:
        print(f"\n❌ Erreur d'import: {e}")
        print("   Installez ChromaDB avec: pip install chromadb")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    count_visualizations()
