"""
Gestionnaire de visualisations utilisant ChromaDB pour stocker des graphiques Seaborn prégénérés.
Remplace le système de génération dynamique par un système de cache de visualisations.
"""

import os
import pickle
import base64
import hashlib
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import chromadb
from chromadb.config import Settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisualizationManager:
    """
    Gestionnaire pour créer, stocker et récupérer des visualisations Seaborn
    dans ChromaDB de manière locale sans dépendance externe.
    """
    
    def __init__(self, db_path: str = "./viz_chroma_db"):
        """
        Initialise le gestionnaire de visualisations.
        
        Args:
            db_path: Chemin vers la base de données ChromaDB pour les visualisations
        """
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        
        # Initialiser ChromaDB
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        
        # Collection pour les visualisations
        try:
            self.viz_collection = self.client.get_collection("visualizations")
            logger.info("Collection de visualisations chargée")
        except Exception:
            self.viz_collection = self.client.create_collection("visualizations")
            logger.info("Nouvelle collection de visualisations créée")
    
    def generate_visualization_id(self, viz_type: str, columns: Dict[str, str], data_hash: str) -> str:
        """Génère un ID unique pour une visualisation."""
        content = f"{viz_type}_{columns}_{data_hash}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_data_hash(self, dataframe: pd.DataFrame) -> str:
        """Génère un hash des données pour détecter les changements."""
        return hashlib.md5(str(dataframe.values.tobytes()).encode()).hexdigest()[:16]
    
    def create_visualization(self, viz_type: str, dataframe: pd.DataFrame, columns: Dict[str, str], title: str) -> str:
        """
        Crée une visualisation Seaborn et la retourne en base64.
        
        Args:
            viz_type: Type de visualisation ('histogram', 'scatter', etc.)
            dataframe: DataFrame pandas
            columns: Dictionnaire des colonnes à utiliser
            title: Titre de la visualisation
            
        Returns:
            Image encodée en base64
        """
        try:
            # Configuration du style Seaborn
            plt.style.use('default')
            sns.set_palette("husl")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if viz_type == 'histogram':
                if columns.get('x') and columns['x'] in dataframe.columns:
                    data = dataframe[columns['x']].dropna()
                    if pd.api.types.is_numeric_dtype(data):
                        sns.histplot(data=dataframe, x=columns['x'], bins=20, ax=ax)
                        ax.set_ylabel('Fréquence')
                    else:
                        # Pour les données catégorielles
                        sns.countplot(data=dataframe, x=columns['x'], ax=ax)
                        plt.xticks(rotation=45)
                        ax.set_ylabel('Nombre')
                        
            elif viz_type == 'scatter':
                if columns.get('x') and columns.get('y'):
                    if (columns['x'] in dataframe.columns and 
                        columns['y'] in dataframe.columns):
                        sns.scatterplot(data=dataframe, x=columns['x'], y=columns['y'], ax=ax)
                        
            elif viz_type == 'bar_chart':
                if columns.get('x') and columns.get('y'):
                    if (columns['x'] in dataframe.columns and 
                        columns['y'] in dataframe.columns):
                        # Grouper les données si nécessaire
                        if dataframe[columns['x']].dtype == 'object':
                            grouped_data = dataframe.groupby(columns['x'])[columns['y']].mean().reset_index()
                            sns.barplot(data=grouped_data, x=columns['x'], y=columns['y'], ax=ax)
                        else:
                            sns.barplot(data=dataframe, x=columns['x'], y=columns['y'], ax=ax)
                        plt.xticks(rotation=45)
                        
            elif viz_type == 'line_chart':
                if columns.get('x') and columns.get('y'):
                    if (columns['x'] in dataframe.columns and 
                        columns['y'] in dataframe.columns):
                        # Trier par x pour une ligne cohérente
                        sorted_data = dataframe.sort_values(columns['x'])
                        sns.lineplot(data=sorted_data, x=columns['x'], y=columns['y'], ax=ax, marker='o')
                        plt.xticks(rotation=45)
                        
            elif viz_type == 'heatmap':
                numeric_columns = columns.get('columns', dataframe.select_dtypes(include=['number']).columns.tolist())
                if len(numeric_columns) > 1:
                    # Limiter à 10 colonnes pour la lisibilité
                    numeric_columns = numeric_columns[:10]
                    correlation_matrix = dataframe[numeric_columns].corr()
                    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
                else:
                    ax.text(0.5, 0.5, 'Pas assez de colonnes numériques\npour une heatmap', 
                           ha='center', va='center', transform=ax.transAxes)
                           
            elif viz_type == 'boxplot':
                if columns.get('y') and columns['y'] in dataframe.columns:
                    if pd.api.types.is_numeric_dtype(dataframe[columns['y']]):
                        sns.boxplot(data=dataframe, y=columns['y'], ax=ax)
                    else:
                        ax.text(0.5, 0.5, f'La colonne {columns["y"]} n\'est pas numérique', 
                               ha='center', va='center', transform=ax.transAxes)
            
            # Ajouter le titre
            ax.set_title(title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            # Convertir en base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return plot_base64
            
        except Exception as e:
            logger.error("Erreur lors de la création de la visualisation: %s", e)
            # Créer une image d'erreur
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, f'Erreur lors de la création\nde la visualisation:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Erreur de visualisation')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return plot_base64
    
    def store_visualization(self, viz_id: str, viz_base64: str, metadata: Dict[str, Any]) -> bool:
        """
        Stocke une visualisation dans ChromaDB.
        
        Args:
            viz_id: ID unique de la visualisation
            viz_base64: Image encodée en base64
            metadata: Métadonnées de la visualisation
            
        Returns:
            True si le stockage a réussi
        """
        try:
            # Préparer les données pour ChromaDB
            document = f"Visualisation {metadata.get('viz_type', 'unknown')} - {metadata.get('title', 'Sans titre')}"
            
            # Stocker dans ChromaDB
            self.viz_collection.add(
                documents=[document],
                metadatas=[{
                    'viz_id': viz_id,
                    'viz_type': metadata.get('viz_type', ''),
                    'title': metadata.get('title', ''),
                    'columns': str(metadata.get('columns', {})),
                    'data_hash': metadata.get('data_hash', ''),
                    'viz_base64': viz_base64
                }],
                ids=[viz_id]
            )
            
            logger.info("Visualisation %s stockée avec succès", viz_id)
            return True
            
        except Exception as e:
            logger.error("Erreur lors du stockage de la visualisation: %s", e)
            return False
    
    def get_visualization(self, viz_id: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Récupère une visualisation depuis ChromaDB.
        
        Args:
            viz_id: ID unique de la visualisation
            
        Returns:
            Tuple (image_base64, metadata) ou None si non trouvé
        """
        try:
            results = self.viz_collection.get(ids=[viz_id])
            
            if results:
                ids = results.get('ids')
                metadatas = results.get('metadatas')
                if ids and metadatas and len(metadatas) > 0:
                    metadata = metadatas[0]
                    viz_base64_raw = metadata.get('viz_base64', '')
                    
                    # Ensure viz_base64 is a string
                    if isinstance(viz_base64_raw, str):
                        viz_base64 = viz_base64_raw
                    else:
                        viz_base64 = str(viz_base64_raw) if viz_base64_raw is not None else ''
                    
                    # Convert ChromaDB metadata to Dict[str, Any]
                    metadata_dict = dict(metadata) if metadata else {}
                    
                    return viz_base64, metadata_dict
            
            return None
            
        except Exception as e:
            logger.error("Erreur lors de la récupération de la visualisation: %s", e)
            return None
    
    def find_similar_visualization(self, viz_type: str, columns: Dict[str, str], data_hash: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Recherche une visualisation similaire existante.
        
        Args:
            viz_type: Type de visualisation
            columns: Colonnes utilisées
            data_hash: Hash des données
            
        Returns:
            Tuple (image_base64, metadata) ou None si non trouvé
        """
        try:
            # Rechercher par métadonnées similaires
            results = self.viz_collection.get(
                where={
                    "viz_type": viz_type,
                    "data_hash": data_hash
                }
            )
            
            if results:
                metadatas = results.get('metadatas') or []
                ids = results.get('ids') or []
                
                # Vérifier que nous avons au moins une metadata valide
                if len(metadatas) > 0 and metadatas[0] is not None:
                    metadata = metadatas[0]
                    
                    # Normaliser la metadata en Dict[str, Any]
                    try:
                        metadata_dict: Dict[str, Any] = dict(metadata) if metadata is not None else {}
                    except Exception:
                        # Si la conversion échoue, conserver une représentation textuelle
                        metadata_dict = {'raw_metadata': str(metadata)}
                    
                    # Extraire et forcer viz_base64 en str
                    viz_base64_raw = metadata_dict.get('viz_base64', '')
                    if isinstance(viz_base64_raw, (bytes, bytearray)):
                        try:
                            viz_base64 = viz_base64_raw.decode()
                        except Exception:
                            viz_base64 = base64.b64encode(viz_base64_raw).decode()
                    else:
                        viz_base64 = str(viz_base64_raw) if viz_base64_raw is not None else ''
                    
                    logger.info("Visualisation similaire trouvée: %s", ids[0] if ids else 'unknown')
                    return viz_base64, metadata_dict
            
            return None
            
        except Exception as e:
            logger.error("Erreur lors de la recherche de visualisation: %s", e)
            return None
    
    def get_or_create_visualization(self, viz_type: str, dataframe: pd.DataFrame, columns: Dict[str, str], title: str) -> Tuple[str, bool]:
        """
        Récupère une visualisation existante ou en crée une nouvelle.
        
        Args:
            viz_type: Type de visualisation
            dataframe: DataFrame pandas
            columns: Colonnes à utiliser
            title: Titre de la visualisation
            
        Returns:
            Tuple (image_base64, is_from_cache)
        """
        # Générer les identifiants
        data_hash = self.get_data_hash(dataframe)
        viz_id = self.generate_visualization_id(viz_type, columns, data_hash)
        
        # Chercher une visualisation existante
        existing_viz = self.get_visualization(viz_id)
        if existing_viz:
            logger.info("Visualisation récupérée du cache: %s", viz_id)
            return existing_viz[0], True
        
        # Chercher une visualisation similaire
        similar_viz = self.find_similar_visualization(viz_type, columns, data_hash)
        if similar_viz:
            return similar_viz[0], True
        
        # Créer une nouvelle visualisation
        logger.info("Création d'une nouvelle visualisation: %s", viz_id)
        viz_base64 = self.create_visualization(viz_type, dataframe, columns, title)
        
        # Stocker la nouvelle visualisation
        metadata = {
            'viz_type': viz_type,
            'title': title,
            'columns': columns,
            'data_hash': data_hash
        }
        
        self.store_visualization(viz_id, viz_base64, metadata)
        
        return viz_base64, False
    
    def list_stored_visualizations(self) -> List[Dict[str, Any]]:
        """Retourne la liste des visualisations stockées."""
        try:
            results = self.viz_collection.get()
            
            visualizations = []
            for i, viz_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                visualizations.append({
                    'id': viz_id,
                    'type': metadata.get('viz_type', 'unknown'),
                    'title': metadata.get('title', 'Sans titre'),
                    'columns': metadata.get('columns', '{}')
                })
            
            return visualizations
            
        except Exception as e:
            logger.error("Erreur lors de la liste des visualisations: %s", e)
            return []
    
    def clear_all_visualizations(self) -> bool:
        """Supprime toutes les visualisations stockées."""
        try:
            self.client.reset()
            self.viz_collection = self.client.create_collection("visualizations")
            logger.info("Toutes les visualisations ont été supprimées")
            return True
            
        except Exception as e:
            logger.error("Erreur lors de la suppression des visualisations: %s", e)
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les visualisations stockées."""
        try:
            total_viz = self.viz_collection.count()
            
            # Compter par type
            results = self.viz_collection.get()
            type_counts = {}
            
            for metadata in results['metadatas']:
                viz_type = metadata.get('viz_type', 'unknown')
                type_counts[viz_type] = type_counts.get(viz_type, 0) + 1
            
            return {
                'total_visualizations': total_viz,
                'by_type': type_counts,
                'db_path': self.db_path
            }
            
        except Exception as e:
            logger.error("Erreur lors de la récupération des statistiques: %s", e)
            return {
                'total_visualizations': 0,
                'by_type': {},
                'db_path': self.db_path
            }