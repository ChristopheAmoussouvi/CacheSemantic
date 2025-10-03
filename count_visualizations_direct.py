"""
Script pour analyser directement la base ChromaDB SQLite
"""
import sqlite3
import json
from pathlib import Path

def analyze_chroma_db():
    """Analyse directe de la base SQLite ChromaDB"""
    
    db_path = Path(__file__).parent / "chroma_db" / "chroma.sqlite3"
    
    if not db_path.exists():
        print(f"❌ Base de données non trouvée: {db_path}")
        return
    
    print("=" * 70)
    print("📊 ANALYSE DIRECTE DE LA BASE CHROMADB")
    print("=" * 70)
    print(f"\n📁 Base de données: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Lister les tables
        print("\n" + "=" * 70)
        print("📋 TABLES DISPONIBLES")
        print("=" * 70)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  • {table[0]}")
        
        # Analyser la table collections
        print("\n" + "=" * 70)
        print("📦 COLLECTIONS")
        print("=" * 70)
        cursor.execute("SELECT * FROM collections")
        collections = cursor.fetchall()
        print(f"Nombre de collections: {len(collections)}")
        
        if collections:
            cursor.execute("PRAGMA table_info(collections)")
            col_info = cursor.fetchall()
            col_names = [info[1] for info in col_info]
            print(f"\nColonnes: {', '.join(col_names)}")
            
            for i, coll in enumerate(collections, 1):
                print(f"\n--- Collection {i} ---")
                for j, col_name in enumerate(col_names):
                    value = coll[j]
                    if col_name == 'metadata' and value:
                        try:
                            metadata = json.loads(value)
                            print(f"  {col_name}: {json.dumps(metadata, indent=4, ensure_ascii=False)}")
                        except:
                            print(f"  {col_name}: {value}")
                    else:
                        print(f"  {col_name}: {value}")
        
        # Analyser la table embeddings
        print("\n" + "=" * 70)
        print("📊 EMBEDDINGS (DOCUMENTS)")
        print("=" * 70)
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        total_docs = cursor.fetchone()[0]
        print(f"Nombre total de documents: {total_docs}")
        
        # Compter les visualisations
        print("\n" + "=" * 70)
        print("📈 ANALYSE DES VISUALISATIONS")
        print("=" * 70)
        
        # D'abord, voir la structure de embedding_metadata
        cursor.execute("PRAGMA table_info(embedding_metadata)")
        metadata_cols = cursor.fetchall()
        print("\nColonnes de embedding_metadata:")
        for col in metadata_cols:
            print(f"  • {col[1]} ({col[2]})")
        
        # Chercher les métadonnées contenant des infos de visualisation
        cursor.execute("SELECT key, string_value FROM embedding_metadata WHERE string_value IS NOT NULL")
        metadata_records = cursor.fetchall()
        
        viz_count = 0
        viz_types = {}
        
        print(f"\nNombre d'enregistrements de métadonnées: {len(metadata_records)}")
        
        # Analyser les clés pour trouver des visualisations
        viz_keywords = ['visualization', 'chart', 'graph', 'plot', 'viz']
        viz_related_keys = []
        
        for key, value in metadata_records:
            # Vérifier si la clé ou la valeur contient des mots-clés de visualisation
            key_lower = key.lower() if key else ""
            value_lower = value.lower() if value else ""
            
            if any(keyword in key_lower or keyword in value_lower for keyword in viz_keywords):
                viz_related_keys.append((key, value))
                
                # Essayer de parser si c'est du JSON
                try:
                    if value and (value.startswith('{') or value.startswith('[')):
                        parsed = json.loads(value)
                        if isinstance(parsed, dict):
                            if 'viz_type' in parsed or 'chart_type' in parsed:
                                viz_count += 1
                                viz_type = parsed.get('viz_type') or parsed.get('chart_type')
                                if viz_type:
                                    viz_types[viz_type] = viz_types.get(viz_type, 0) + 1
                except:
                    pass
        
        print(f"\n✅ Métadonnées liées aux visualisations: {len(viz_related_keys)}")
        if viz_related_keys:
            print("\nExemples de métadonnées trouvées:")
            for key, value in viz_related_keys[:5]:  # Afficher les 5 premières
                print(f"  • {key}: {value[:100]}..." if len(value) > 100 else f"  • {key}: {value}")
        
        print(f"\n✅ Visualisations identifiées: {viz_count}")
        
        if viz_types:
            print("\n📊 Répartition par type:")
            for viz_type, count in sorted(viz_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {viz_type}: {count}")
        
        # Chercher dans les documents aussi
        print("\n" + "=" * 70)
        print("🔍 RECHERCHE DANS LES DOCUMENTS")
        print("=" * 70)
        
        # Voir la structure de la table embeddings
        cursor.execute("PRAGMA table_info(embeddings)")
        emb_cols = cursor.fetchall()
        print("\nColonnes de embeddings:")
        for col in emb_cols:
            print(f"  • {col[1]} ({col[2]})")
        
        # Chercher le contenu textuel
        # Essayer différentes colonnes possibles
        text_columns = ['document', 'documents', 'text', 'content']
        text_col_found = None
        
        for col_name in text_columns:
            try:
                cursor.execute(f"SELECT {col_name} FROM embeddings LIMIT 1")
                text_col_found = col_name
                print(f"\n✅ Colonne texte trouvée: {col_name}")
                break
            except:
                continue
        
        viz_docs = []
        if text_col_found:
            cursor.execute(f"SELECT {text_col_found} FROM embeddings WHERE {text_col_found} LIKE '%visualization%' OR {text_col_found} LIKE '%chart%' OR {text_col_found} LIKE '%graph%'")
            viz_docs = cursor.fetchall()
            print(f"Documents mentionnant des visualisations: {len(viz_docs)}")
            
            if viz_docs:
                print("\nExemples de documents avec visualisations:")
                for doc in viz_docs[:3]:
                    text = doc[0] if doc[0] else ""
                    print(f"  • {text[:150]}..." if len(text) > 150 else f"  • {text}")
        else:
            print("\n⚠️ Aucune colonne texte trouvée")
            
            # Lire quelques embeddings pour voir le contenu
            cursor.execute("SELECT * FROM embeddings LIMIT 2")
            sample_records = cursor.fetchall()
            if sample_records:
                print("\nExemple d'enregistrement embeddings:")
                for i, record in enumerate(sample_records, 1):
                    print(f"\n  Enregistrement {i}:")
                    for j, col in enumerate(emb_cols):
                        value = record[j]
                        col_name = col[1]
                        if isinstance(value, bytes):
                            print(f"    {col_name}: <bytes: {len(value)} octets>")
                        elif isinstance(value, str) and len(value) > 100:
                            print(f"    {col_name}: {value[:100]}...")
                        else:
                            print(f"    {col_name}: {value}")
        
        # Statistiques finales
        print("\n" + "=" * 70)
        print("📈 RÉSUMÉ FINAL")
        print("=" * 70)
        print(f"📦 Collections: {len(collections)}")
        print(f"📄 Documents totaux: {total_docs}")
        print(f"📊 Visualisations identifiées dans métadonnées: {viz_count}")
        print(f"📝 Documents mentionnant visualisations: {len(viz_docs) if viz_docs else 0}")
        print(f"🎨 Types de visualisations: {len(viz_types)}")
        
        # Conclusion
        print("\n" + "=" * 70)
        print("💡 CONCLUSION")
        print("=" * 70)
        
        if viz_count == 0 and len(viz_docs) == 0:
            print("⚠️  Aucune visualisation n'a été stockée dans ChromaDB pour le moment.")
            print("    Les visualisations sont probablement stockées dans le dossier 'exports/'")
            print("    et référencées dans la session Streamlit sans être persistées dans ChromaDB.")
        else:
            print(f"✅ Total de visualisations détectées: {viz_count + len(viz_docs)}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_chroma_db()
