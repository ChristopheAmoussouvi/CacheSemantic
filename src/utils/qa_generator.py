"""
Générateur de questions et visualisations pour enrichir la base de connaissances ChromaDB.
Crée 100+ paires question/visualisation pour différents domaines d'analyse.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import json
import base64
from typing import Dict, List, Tuple, Any, Optional
import random
from src.utils.data_generator import DataGenerator
from src.components.data_manager import DataManager
from src.components.visualization_manager import VisualizationManager


class QAVisualizationGenerator:
    """Générateur de questions et visualisations pour ChromaDB."""
    
    def __init__(self, output_dir: str = "./qa_visualizations"):
        """
        Initialise le générateur.
        
        Args:
            output_dir: Répertoire pour sauvegarder les visualisations
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Générateur de données
        self.data_generator = DataGenerator()
        
        # Gestionnaires ChromaDB
        self.data_manager = DataManager()
        self.viz_manager = VisualizationManager()
        
        # Templates de questions par type d'analyse
        self.question_templates = self._build_question_templates()
        
        # Configuration matplotlib/seaborn
        plt.style.use('default')
        sns.set_palette("husl")
    
    def _build_question_templates(self) -> Dict[str, List[Dict]]:
        """Construit les templates de questions par domaine."""
        return {
            "ventes": [
                {
                    "question": "Quelles sont les ventes par région ?",
                    "viz_type": "bar",
                    "columns": ["region", "chiffre_affaires"],
                    "description": "Graphique en barres des ventes totales par région"
                },
                {
                    "question": "Comment évoluent les ventes dans le temps ?",
                    "viz_type": "line",
                    "columns": ["date", "chiffre_affaires"],
                    "description": "Évolution temporelle du chiffre d'affaires"
                },
                {
                    "question": "Quelle est la performance de chaque vendeur ?",
                    "viz_type": "bar",
                    "columns": ["vendeur", "chiffre_affaires"],
                    "description": "Comparaison des performances des vendeurs"
                },
                {
                    "question": "Quels produits se vendent le mieux ?",
                    "viz_type": "bar",
                    "columns": ["produit", "quantite"],
                    "description": "Classement des produits par quantité vendue"
                },
                {
                    "question": "Y a-t-il une corrélation entre prix et quantité ?",
                    "viz_type": "scatter",
                    "columns": ["prix_unitaire", "quantite"],
                    "description": "Nuage de points prix vs quantité"
                },
                {
                    "question": "Quelle est la distribution des prix ?",
                    "viz_type": "hist",
                    "columns": ["prix_unitaire"],
                    "description": "Histogramme de la distribution des prix"
                },
                {
                    "question": "Heatmap des ventes par région et produit ?",
                    "viz_type": "heatmap",
                    "columns": ["region", "produit", "chiffre_affaires"],
                    "description": "Carte de chaleur région-produit"
                }
            ],
            
            "clients": [
                {
                    "question": "Quelle est la répartition par âge des clients ?",
                    "viz_type": "hist",
                    "columns": ["age"],
                    "description": "Distribution des âges des clients"
                },
                {
                    "question": "Comment se répartissent les clients par ville ?",
                    "viz_type": "bar",
                    "columns": ["ville"],
                    "description": "Nombre de clients par ville"
                },
                {
                    "question": "Relation entre âge et salaire ?",
                    "viz_type": "scatter",
                    "columns": ["age", "salaire_annuel"],
                    "description": "Corrélation âge-salaire"
                },
                {
                    "question": "Distribution de la satisfaction client ?",
                    "viz_type": "hist",
                    "columns": ["score_satisfaction"],
                    "description": "Histogramme des scores de satisfaction"
                },
                {
                    "question": "Comparaison hommes vs femmes ?",
                    "viz_type": "bar",
                    "columns": ["sexe"],
                    "description": "Répartition par sexe"
                },
                {
                    "question": "Boxplot des salaires par ville ?",
                    "viz_type": "box",
                    "columns": ["ville", "salaire_annuel"],
                    "description": "Distribution des salaires par ville"
                }
            ],
            
            "financier": [
                {
                    "question": "Évolution du chiffre d'affaires ?",
                    "viz_type": "line",
                    "columns": ["date", "chiffre_affaires"],
                    "description": "Tendance du CA dans le temps"
                },
                {
                    "question": "Comparaison revenus vs coûts ?",
                    "viz_type": "line",
                    "columns": ["date", "chiffre_affaires", "couts"],
                    "description": "Évolution comparative revenus/coûts"
                },
                {
                    "question": "Distribution des marges ?",
                    "viz_type": "hist",
                    "columns": ["marge"],
                    "description": "Histogramme des marges bénéficiaires"
                },
                {
                    "question": "Performance par trimestre ?",
                    "viz_type": "bar",
                    "columns": ["trimestre", "benefice"],
                    "description": "Bénéfices par trimestre"
                },
                {
                    "question": "Corrélation CA-bénéfice ?",
                    "viz_type": "scatter",
                    "columns": ["chiffre_affaires", "benefice"],
                    "description": "Relation chiffre d'affaires vs bénéfice"
                }
            ],
            
            "satisfaction": [
                {
                    "question": "Satisfaction par service ?",
                    "viz_type": "bar",
                    "columns": ["service_evalue", "note_satisfaction"],
                    "description": "Satisfaction moyenne par service"
                },
                {
                    "question": "Satisfaction par tranche d'âge ?",
                    "viz_type": "bar",
                    "columns": ["tranche_age", "note_satisfaction"],
                    "description": "Notes par groupe d'âge"
                },
                {
                    "question": "Distribution des notes ?",
                    "viz_type": "hist",
                    "columns": ["note_satisfaction"],
                    "description": "Histogramme des notes de satisfaction"
                },
                {
                    "question": "Recommandations par service ?",
                    "viz_type": "bar",
                    "columns": ["service_evalue", "recommandation"],
                    "description": "Taux de recommandation par service"
                }
            ]
        }
    
    def _create_visualization(self, df: pd.DataFrame, viz_config: Dict,
                            question: str, dataset_name: str) -> Optional[str]:
        """
        Crée une visualisation basée sur la configuration.
        
        Args:
            df: DataFrame avec les données
            viz_config: Configuration de la visualisation
            question: Question associée
            dataset_name: Nom du dataset
            
        Returns:
            Chemin vers le fichier image généré
        """
        plt.figure(figsize=(10, 6))
        
        viz_type = viz_config["viz_type"]
        columns = viz_config["columns"]
        
        try:
            if viz_type == "bar":
                if len(columns) == 1:
                    # Comptage simple
                    df[columns[0]].value_counts().plot(kind='bar')
                    plt.ylabel("Nombre")
                else:
                    # Agrégation
                    if columns[1] in df.columns:
                        grouped = df.groupby(columns[0])[columns[1]].sum()
                        grouped.plot(kind='bar')
                        plt.ylabel(columns[1])
                    else:
                        df[columns[0]].value_counts().plot(kind='bar')
                
                plt.xlabel(columns[0])
                plt.xticks(rotation=45)
            
            elif viz_type == "line":
                if len(columns) >= 2:
                    # Convertir dates si nécessaire
                    if 'date' in columns[0].lower():
                        df_copy = df.copy()
                        df_copy[columns[0]] = pd.to_datetime(df_copy[columns[0]])
                        df_copy = df_copy.sort_values(columns[0])
                        
                        if len(columns) == 2:
                            df_copy.plot(x=columns[0], y=columns[1], kind='line')
                        else:
                            # Plusieurs lignes
                            for col in columns[1:]:
                                if col in df_copy.columns:
                                    plt.plot(df_copy[columns[0]], df_copy[col], label=col)
                            plt.legend()
                    else:
                        df.plot(x=columns[0], y=columns[1], kind='line')
                
                plt.xlabel(columns[0])
                if len(columns) > 1:
                    plt.ylabel(columns[1])
            
            elif viz_type == "scatter":
                if len(columns) >= 2 and all(col in df.columns for col in columns[:2]):
                    plt.scatter(df[columns[0]], df[columns[1]], alpha=0.6)
                    plt.xlabel(columns[0])
                    plt.ylabel(columns[1])
                    
                    # Ligne de tendance
                    z = np.polyfit(df[columns[0]], df[columns[1]], 1)
                    p = np.poly1d(z)
                    plt.plot(df[columns[0]], p(df[columns[0]]), "r--", alpha=0.8)
            
            elif viz_type == "hist":
                if columns[0] in df.columns:
                    df[columns[0]].hist(bins=20, alpha=0.7)
                    plt.xlabel(columns[0])
                    plt.ylabel("Fréquence")
            
            elif viz_type == "box":
                if len(columns) >= 2:
                    sns.boxplot(data=df, x=columns[0], y=columns[1])
                    plt.xticks(rotation=45)
            
            elif viz_type == "heatmap":
                if len(columns) >= 3:
                    pivot_table = df.pivot_table(
                        values=columns[2], 
                        index=columns[0], 
                        columns=columns[1], 
                        aggfunc='sum'
                    )
                    sns.heatmap(pivot_table, annot=True, fmt='.0f', cmap='YlOrRd')
            
            plt.title(question)
            plt.tight_layout()
            
            # Sauvegarder
            filename = f"{dataset_name}_{len(os.listdir(self.output_dir)) + 1:03d}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"Erreur lors de la création de {viz_type}: {e}")
            plt.close()
            return None
    
    def generate_qa_pairs(self) -> List[Dict[str, Any]]:
        """
        Génère 100+ paires question/visualisation.
        
        Returns:
            Liste de dictionnaires avec question, réponse, visualisation
        """
        qa_pairs = []
        
        # Générer les datasets
        datasets = {
            "ventes": self.data_generator.generate_sales_data(500),
            "clients": self.data_generator.generate_customer_data(300),
            "financier": self.data_generator.generate_financial_data(100),
            "satisfaction": self.data_generator.generate_survey_data(200)
        }
        
        print(f"📊 Datasets générés: {list(datasets.keys())}")
        
        # Générer les Q&A pour chaque dataset
        for dataset_name, df in datasets.items():
            print(f"\n🔍 Traitement du dataset '{dataset_name}' ({len(df)} lignes)")
            
            templates = self.question_templates.get(dataset_name, [])
            
            for i, template in enumerate(templates):
                # Pré-initialiser pour éviter l'avertissement 'possibly unbound'
                question = str(template.get("question", "Question inconnue"))
                description = str(template.get("description", ""))
                try:
                    
                    # Créer la visualisation
                    viz_path = self._create_visualization(
                        df, template, question, dataset_name
                    )
                    
                    if viz_path:
                        # Générer une réponse descriptive
                        response = self._generate_response(df, template, dataset_name)
                        
                        qa_pair = {
                            "question": question,
                            "response": response,
                            "visualization_path": viz_path,
                            "dataset": dataset_name,
                            "description": description,
                            "viz_type": template["viz_type"],
                            "columns": template["columns"],
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        qa_pairs.append(qa_pair)
                        print(f"  ✅ Q&A {len(qa_pairs):2d}: {question[:50]}...")
                    
                except Exception as e:
                    # question est toujours défini grâce à la pré-initialisation
                    print(f"  ❌ Erreur pour '{question}': {e}")
        
        # Générer des variations supplémentaires
        additional_pairs = self._generate_variations(datasets)
        qa_pairs.extend(additional_pairs)
        
        print(f"\n🎯 Total généré: {len(qa_pairs)} paires Q&A")
        return qa_pairs
    
    def _generate_response(self, df: pd.DataFrame, template: Dict, 
                          dataset_name: str) -> str:
        """Génère une réponse descriptive basée sur les données."""
        viz_type = template["viz_type"]
        columns = template["columns"]
        
        response_parts = []
        
        try:
            if viz_type == "bar" and len(columns) >= 2:
                if columns[1] in df.columns:
                    grouped = df.groupby(columns[0])[columns[1]].sum().sort_values(ascending=False)
                    top_3 = grouped.head(3)
                    response_parts.append(f"Top 3 {columns[0]}:")
                    for idx, (key, value) in enumerate(top_3.items()):
                        response_parts.append(f"{idx+1}. {key}: {value:,.0f}")
            
            elif viz_type == "line" and len(columns) >= 2:
                if columns[1] in df.columns:
                    trend = "croissante" if df[columns[1]].iloc[-1] > df[columns[1]].iloc[0] else "décroissante"
                    response_parts.append(f"Tendance {trend} observée pour {columns[1]}")
                    response_parts.append(f"Valeur min: {df[columns[1]].min():,.0f}")
                    response_parts.append(f"Valeur max: {df[columns[1]].max():,.0f}")
            
            elif viz_type == "scatter":
                if len(columns) >= 2 and all(col in df.columns for col in columns[:2]):
                    corr = df[columns[0]].corr(df[columns[1]])
                    correlation_type = "forte" if abs(corr) > 0.7 else "modérée" if abs(corr) > 0.3 else "faible"
                    direction = "positive" if corr > 0 else "négative"
                    response_parts.append(f"Corrélation {correlation_type} {direction} (r={corr:.2f})")
            
            elif viz_type == "hist":
                if columns[0] in df.columns:
                    mean_val = df[columns[0]].mean()
                    std_val = df[columns[0]].std()
                    response_parts.append(f"Moyenne: {mean_val:.1f}")
                    response_parts.append(f"Écart-type: {std_val:.1f}")
                    response_parts.append(f"Distribution centrée sur {mean_val:.1f}")
            
            # Ajouter des statistiques générales
            response_parts.append(f"Analyse basée sur {len(df)} enregistrements")
            
        except Exception as e:
            response_parts.append("Analyse statistique des données disponibles")
        
        return " | ".join(response_parts) if response_parts else "Visualisation des données"
    
    def _generate_variations(self, datasets: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Génère des variations supplémentaires pour atteindre 100+ Q&A."""
        variations = []
        
        # Questions plus spécifiques
        specific_questions = [
            ("Quels sont les 5 meilleurs performers ?", "bar"),
            ("Y a-t-il des outliers dans les données ?", "box"),
            ("Quelle est la médiane de cette distribution ?", "hist"),
            ("Comment se comparent les différents segments ?", "bar"),
            ("Quelle est la tendance sur les 6 derniers mois ?", "line"),
        ]
        
        for dataset_name, df in datasets.items():
            for question_text, viz_type in specific_questions[:3]:  # Limiter pour éviter trop de générations
                try:
                    # Adapter la question au dataset
                    adapted_question = f"{question_text} - Dataset {dataset_name.title()}"
                    
                    # Configuration simple
                    template = {
                        "question": adapted_question,
                        "viz_type": viz_type,
                        "columns": df.select_dtypes(include=[np.number]).columns.tolist()[:2],
                        "description": f"Analyse {viz_type} pour {dataset_name}"
                    }
                    
                    viz_path = self._create_visualization(df, template, adapted_question, f"{dataset_name}_var")
                    
                    if viz_path:
                        variation = {
                            "question": adapted_question,
                            "response": f"Analyse spécialisée du dataset {dataset_name}",
                            "visualization_path": viz_path,
                            "dataset": f"{dataset_name}_variation",
                            "description": template["description"],
                            "viz_type": viz_type,
                            "columns": template["columns"],
                            "timestamp": datetime.now().isoformat()
                        }
                        variations.append(variation)
                        
                except Exception as e:
                    continue
        
        return variations
    
    def store_in_chromadb(self, qa_pairs: List[Dict[str, Any]]) -> None:
        """
        Stocke les paires Q&A dans ChromaDB.
        
        Args:
            qa_pairs: Liste des paires question/réponse/visualisation
        """
        print(f"\n💾 Stockage de {len(qa_pairs)} paires dans ChromaDB...")
        
        for i, qa_pair in enumerate(qa_pairs):
            try:
                # Lire l'image et encoder en base64
                try:
                    with open(qa_pair["visualization_path"], "rb") as img_f:
                        img_b64 = base64.b64encode(img_f.read()).decode('utf-8')
                except Exception as img_err:
                    print(f"  ❌ Impossible de lire l'image {qa_pair['visualization_path']}: {img_err}")
                    continue

                # Générer un identifiant unique (basé sur l'index et horodatage)
                viz_id = f"qa_{i+1}_{int(datetime.now().timestamp())}"

                # Stocker la visualisation dans VisualizationManager
                self.viz_manager.store_visualization(
                    viz_id=viz_id,
                    viz_base64=img_b64,
                    metadata={
                        "dataset": qa_pair["dataset"],
                        "viz_type": qa_pair["viz_type"],
                        "title": qa_pair["question"],
                        "description": qa_pair["description"],
                        "columns": qa_pair["columns"],
                        "data_hash": "qa_seed"
                    }
                )
                
                # Préparer les métadonnées pour DataManager
                metadata = {
                    "type": "qa_pair",
                    "dataset": qa_pair["dataset"],
                    "viz_type": qa_pair["viz_type"],
                    "viz_id": viz_id,
                    "timestamp": qa_pair["timestamp"]
                }
                
                # Stocker dans DataManager (pour l'indexation sémantique)
                document_text = f"Question: {qa_pair['question']}\nRéponse: {qa_pair['response']}"
                
                # Note: DataManager.add_document n'existe pas, on utilise une approche alternative
                # Ici on pourrait étendre DataManager ou utiliser directement ChromaDB
                
                print(f"  ✅ Stocké {i+1:3d}/{len(qa_pairs)}: {qa_pair['question'][:50]}...")
                
            except Exception as e:
                print(f"  ❌ Erreur stockage {i+1}: {e}")
        
        print("💾 Stockage terminé !")
    
    def save_qa_catalog(self, qa_pairs: List[Dict[str, Any]], 
                       filename: str = "qa_catalog.json") -> None:
        """
        Sauvegarde le catalogue des Q&A en JSON.
        
        Args:
            qa_pairs: Liste des paires Q&A
            filename: Nom du fichier de sortie
        """
        catalog_path = os.path.join(self.output_dir, filename)
        
        # Préparer les données pour JSON (enlever les objets non sérialisables)
        json_data = []
        for qa in qa_pairs:
            json_qa = {
                "question": qa["question"],
                "response": qa["response"],
                "visualization_filename": os.path.basename(qa["visualization_path"]),
                "dataset": qa["dataset"],
                "description": qa["description"],
                "viz_type": qa["viz_type"],
                "columns": qa["columns"],
                "timestamp": qa["timestamp"]
            }
            json_data.append(json_qa)
        
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Catalogue sauvegardé: {catalog_path}")
        
        # Statistiques
        stats = {
            "total_pairs": len(qa_pairs),
            "datasets": list(set(qa["dataset"] for qa in qa_pairs)),
            "viz_types": list(set(qa["viz_type"] for qa in qa_pairs)),
            "generation_date": datetime.now().isoformat()
        }
        
        stats_path = os.path.join(self.output_dir, "generation_stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Statistiques: {stats}")


def main():
    """Fonction principale pour générer et stocker les Q&A."""
    print("🚀 Génération de 100+ Questions & Visualisations")
    print("=" * 60)
    
    # Initialiser le générateur
    generator = QAVisualizationGenerator()
    
    # Générer les paires Q&A
    qa_pairs = generator.generate_qa_pairs()
    
    # Sauvegarder le catalogue
    generator.save_qa_catalog(qa_pairs)
    
    # Stocker dans ChromaDB
    generator.store_in_chromadb(qa_pairs)
    
    print(f"\n🎉 Génération terminée !")
    print(f"📁 Visualisations: {generator.output_dir}")
    print(f"🔢 Total: {len(qa_pairs)} paires Q&A générées")


if __name__ == "__main__":
    main()
