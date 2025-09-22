"""
Script pour générer les visualisations des Q&A.
À exécuter quand l'environnement NumPy est stabilisé.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import json
import os

def generate_visualizations():
    """Génère toutes les visualisations manquantes."""
    
    # Charger le catalogue
    with open("qa_visualizations/qa_catalog.json", 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)
    
    print(f"🎨 Génération de {len(qa_pairs)} visualisations...")
    
    # Pour chaque Q&A, créer une visualisation placeholder
    for i, qa in enumerate(qa_pairs):
        plt.figure(figsize=(10, 6))
        
        # Créer un graphique simple basé sur le type
        viz_type = qa.get("viz_type", "bar")
        
        if viz_type == "bar":
            # Graphique en barres exemple
            categories = ["A", "B", "C", "D", "E"]
            values = np.random.randint(10, 100, 5)
            plt.bar(categories, values)
            plt.ylabel("Valeurs")
            
        elif viz_type == "line":
            # Graphique linéaire exemple
            x = range(12)
            y = np.random.randint(50, 150, 12) + np.sin(np.array(x)) * 20
            plt.plot(x, y, marker='o')
            plt.xlabel("Temps")
            plt.ylabel("Valeurs")
            
        elif viz_type == "scatter":
            # Nuage de points exemple
            x = np.random.normal(50, 15, 100)
            y = x * 1.2 + np.random.normal(0, 10, 100)
            plt.scatter(x, y, alpha=0.6)
            plt.xlabel("Variable X")
            plt.ylabel("Variable Y")
            
        elif viz_type == "hist":
            # Histogramme exemple
            data = np.random.normal(100, 15, 1000)
            plt.hist(data, bins=20, alpha=0.7)
            plt.xlabel("Valeurs")
            plt.ylabel("Fréquence")
            
        elif viz_type == "box":
            # Box plot exemple
            data = [np.random.normal(0, std, 100) for std in range(1, 4)]
            plt.boxplot(data)
            plt.ylabel("Valeurs")
            
        elif viz_type == "heatmap":
            # Heatmap exemple
            data = np.random.rand(5, 5)
            sns.heatmap(data, annot=True, cmap='viridis')
        
        plt.title(qa["question"])
        plt.tight_layout()
        
        # Sauvegarder
        viz_path = qa["visualization_path"]
        os.makedirs(os.path.dirname(viz_path), exist_ok=True)
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        if (i + 1) % 10 == 0:
            print(f"  ✅ {i+1}/{len(qa_pairs)} visualisations créées")
    
    print("🎨 Toutes les visualisations ont été générées !")

if __name__ == "__main__":
    generate_visualizations()
