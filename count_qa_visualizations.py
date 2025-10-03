"""
Script pour compter toutes les visualisations dans le système
"""
import json
from pathlib import Path

def count_qa_visualizations():
    """Compte les visualisations Q&A stockées"""
    
    print("=" * 70)
    print("📊 ANALYSE DES VISUALISATIONS Q&A")
    print("=" * 70)
    
    qa_viz_dir = Path("qa_visualizations")
    
    if not qa_viz_dir.exists():
        print("❌ Dossier qa_visualizations non trouvé")
        return
    
    # Lire les statistiques de génération
    stats_file = qa_viz_dir / "generation_stats.json"
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        print(f"\n📈 STATISTIQUES GLOBALES")
        print("=" * 70)
        print(f"Total de paires Q&A: {stats.get('total_pairs', 0)}")
        print(f"Méthode: {stats.get('method', 'N/A')}")
        print(f"Date de génération: {stats.get('generation_date', 'N/A')}")
        
        datasets = stats.get('datasets', [])
        if datasets:
            print(f"\n📁 Datasets couverts ({len(datasets)}):")
            for ds in datasets:
                print(f"  • {ds}")
        
        viz_types = stats.get('viz_types', [])
        if viz_types:
            print(f"\n📊 Types de visualisations ({len(viz_types)}):")
            for vt in viz_types:
                print(f"  • {vt}")
    
    # Lire l'index des types de visualisations
    viz_type_file = qa_viz_dir / "viz_type_index.json"
    if viz_type_file.exists():
        with open(viz_type_file, 'r', encoding='utf-8') as f:
            viz_type_index = json.load(f)
        
        print(f"\n📊 RÉPARTITION PAR TYPE")
        print("=" * 70)
        
        total = 0
        counts = {}
        for viz_type, qa_list in viz_type_index.items():
            count = len(qa_list)
            counts[viz_type] = count
            total += count
        
        for viz_type, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 5)
            print(f"  {viz_type:10s} : {count:3d} ({percentage:5.1f}%) {bar}")
        
        print(f"\n  {'TOTAL':10s} : {total:3d} (100.0%)")
    
    # Lire le catalogue Q&A
    catalog_file = qa_viz_dir / "qa_catalog.json"
    if catalog_file.exists():
        with open(catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        
        print(f"\n📚 CATALOGUE Q&A")
        print("=" * 70)
        
        # Le catalogue peut être soit une liste soit un dictionnaire
        if isinstance(catalog, list):
            print(f"Nombre d'entrées dans le catalogue: {len(catalog)}")
            
            if len(catalog) > 0:
                print("\nExemples de questions:")
                for i, entry in enumerate(catalog[:5], 1):
                    question = entry.get('question', 'N/A')
                    viz_type = entry.get('viz_type', 'N/A')
                    dataset = entry.get('dataset', 'N/A')
                    print(f"\n  {i}. {question}")
                    print(f"     Type: {viz_type} | Dataset: {dataset}")
        else:
            print(f"Nombre d'entrées dans le catalogue: {len(catalog)}")
            
            if len(catalog) > 0:
                print("\nExemples de questions:")
                for i, (question, data) in enumerate(list(catalog.items())[:5], 1):
                    viz_type = data.get('viz_type', 'N/A')
                    dataset = data.get('dataset', 'N/A')
                    print(f"\n  {i}. {question}")
                    print(f"     Type: {viz_type} | Dataset: {dataset}")
    
    # Lire l'index des datasets
    dataset_file = qa_viz_dir / "dataset_index.json"
    if dataset_file.exists():
        with open(dataset_file, 'r', encoding='utf-8') as f:
            dataset_index = json.load(f)
        
        print(f"\n📁 RÉPARTITION PAR DATASET")
        print("=" * 70)
        
        total = 0
        ds_counts = {}
        for dataset, qa_list in dataset_index.items():
            count = len(qa_list)
            ds_counts[dataset] = count
            total += count
        
        for dataset, count in sorted(ds_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 5)
            print(f"  {dataset:15s} : {count:3d} ({percentage:5.1f}%) {bar}")
    
    # Vérifier le dossier exports
    exports_dir = Path("exports")
    print(f"\n📂 DOSSIER EXPORTS")
    print("=" * 70)
    
    if exports_dir.exists():
        png_files = list(exports_dir.glob("*.png"))
        print(f"Fichiers PNG exportés: {len(png_files)}")
        
        if png_files:
            print("\nDerniers fichiers exportés:")
            for png_file in sorted(png_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                size_kb = png_file.stat().st_size / 1024
                print(f"  • {png_file.name} ({size_kb:.1f} KB)")
    else:
        print("Le dossier 'exports' n'existe pas ou est vide")
    
    # Résumé final
    print(f"\n" + "=" * 70)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 70)
    
    total_qa = stats.get('total_pairs', 0) if stats_file.exists() else 0
    total_exports = len(png_files) if exports_dir.exists() and png_files else 0
    
    print(f"✅ Visualisations Q&A stockées (métadonnées): {total_qa}")
    print(f"📁 Visualisations exportées (fichiers PNG): {total_exports}")
    print(f"📦 Collections ChromaDB: 1 (data_collection)")
    print(f"📄 Documents dans ChromaDB: 6")
    
    print(f"\n💡 CONCLUSION")
    print("=" * 70)
    print(f"Le système contient {total_qa} paires question-réponse avec visualisations")
    print(f"préparées pour 4 datasets (ventes, financier, clients, satisfaction).")
    print(f"Les visualisations sont générées à la demande lors des requêtes.")

if __name__ == "__main__":
    count_qa_visualizations()
