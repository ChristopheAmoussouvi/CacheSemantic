"""
Script pour créer les index des Q&A générées.
"""

import json
import os

def create_indexes():
    """Crée les index pour les Q&A."""
    print("📊 Création des index Q&A")
    
    # Charger le catalogue
    with open('qa_visualizations/qa_catalog.json', 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)
    
    print(f"📋 Chargement de {len(qa_pairs)} Q&A")
    
    # Créer un index par mots-clés
    keyword_index = {}
    for qa in qa_pairs:
        question_words = qa['question'].lower().split()
        for word in question_words:
            word = word.strip('?.,!').replace("'", '').replace('-', '').replace(':', '')
            if len(word) > 2 and word not in ['les', 'des', 'par', 'sur', 'dans', 'une', 'est', 'sont', 'avec']:
                if word not in keyword_index:
                    keyword_index[word] = []
                keyword_index[word].append({
                    'qa_id': qa.get('id', ''),
                    'question': qa['question'],
                    'response': qa['response'],
                    'viz_path': qa.get('visualization_path', ''),
                    'dataset': qa.get('dataset', ''),
                    'viz_type': qa.get('viz_type', '')
                })
    
    # Sauvegarder l'index des mots-clés
    with open('qa_visualizations/keyword_index.json', 'w', encoding='utf-8') as f:
        json.dump(keyword_index, f, ensure_ascii=False, indent=2)
    
    print(f"🔑 Index mots-clés créé: {len(keyword_index)} mots")
    
    # Créer un index par dataset
    dataset_index = {}
    for qa in qa_pairs:
        dataset = qa.get('dataset', 'unknown')
        if dataset not in dataset_index:
            dataset_index[dataset] = []
        dataset_index[dataset].append(qa)
    
    with open('qa_visualizations/dataset_index.json', 'w', encoding='utf-8') as f:
        json.dump(dataset_index, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Index dataset créé: {list(dataset_index.keys())}")
    
    # Créer un index par type de visualisation
    viz_type_index = {}
    for qa in qa_pairs:
        viz_type = qa.get('viz_type', 'unknown')
        if viz_type not in viz_type_index:
            viz_type_index[viz_type] = []
        viz_type_index[viz_type].append(qa)
    
    with open('qa_visualizations/viz_type_index.json', 'w', encoding='utf-8') as f:
        json.dump(viz_type_index, f, ensure_ascii=False, indent=2)
    
    print(f"🎨 Index visualisation créé: {list(viz_type_index.keys())}")
    
    # Statistiques des mots-clés les plus fréquents
    word_freq = {word: len(entries) for word, entries in keyword_index.items()}
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
    
    print("\n🔝 Top 15 des mots-clés:")
    for word, freq in top_words:
        print(f"  • {word}: {freq} occurrences")
    
    # Statistiques par dataset
    print("\n📊 Répartition par dataset:")
    for dataset, qas in dataset_index.items():
        print(f"  • {dataset}: {len(qas)} Q&A")
    
    # Statistiques par type de visualisation
    print("\n🎨 Répartition par type de visualisation:")
    for viz_type, qas in viz_type_index.items():
        print(f"  • {viz_type}: {len(qas)} Q&A")
    
    print("\n✅ Index créés avec succès !")
    return keyword_index, dataset_index, viz_type_index

if __name__ == "__main__":
    create_indexes()