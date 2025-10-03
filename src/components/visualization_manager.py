"""
Gestionnaire de visualisations utilisant ChromaDB pour stocker des graphiques Matplotlib.
Remplace le système de génération dynamique par un système de cache de visualisations.
"""

import os
import base64
import hashlib
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import chromadb
from chromadb.config import Settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisualizationManager:
    """
    Gestionnaire pour créer, stocker et récupérer des visualisations Matplotlib
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
        except (ValueError, RuntimeError):
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
        Crée une visualisation Matplotlib et la retourne en base64.
        
        Args:
            viz_type: Type de visualisation ('histogram', 'scatter', etc.)
            dataframe: DataFrame pandas
            columns: Dictionnaire des colonnes à utiliser
            title: Titre de la visualisation
            
        Returns:
            Image encodée en base64
        """
        try:
            # Configuration du style Matplotlib
            plt.style.use('default')
            
            # Palette de couleurs personnalisée
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
            _fig, ax = plt.subplots(figsize=(10, 6))
            
            if viz_type == 'histogram':
                if columns.get('x') and columns['x'] in dataframe.columns:
                    data = dataframe[columns['x']].dropna()
                    if pd.api.types.is_numeric_dtype(data):
                        # Histogramme pour données numériques
                        ax.hist(data, bins=20, color=colors[0], alpha=0.7, edgecolor='black')
                        ax.set_xlabel(columns['x'], fontsize=11)
                        ax.set_ylabel('Fréquence', fontsize=11)
                        ax.grid(axis='y', alpha=0.3, linestyle='--')
                    else:
                        # Graphique en barres pour données catégorielles
                        value_counts = data.value_counts()
                        x_pos = np.arange(len(value_counts))
                        ax.bar(x_pos, value_counts.values, color=colors[:len(value_counts)], 
                              alpha=0.7, edgecolor='black')
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
                        ax.set_xlabel(columns['x'], fontsize=11)
                        ax.set_ylabel('Nombre', fontsize=11)
                        ax.grid(axis='y', alpha=0.3, linestyle='--')
                        
            elif viz_type == 'scatter':
                if columns.get('x') and columns.get('y'):
                    if (columns['x'] in dataframe.columns and
                        columns['y'] in dataframe.columns):
                        # Aligner les données (supprimer les NaN)
                        valid_mask = dataframe[[columns['x'], columns['y']]].notna().all(axis=1)
                        x_clean = dataframe.loc[valid_mask, columns['x']]
                        y_clean = dataframe.loc[valid_mask, columns['y']]
                        ax.scatter(x_clean, y_clean, color=colors[0], alpha=0.6, 
                                  edgecolor='black', s=50)
                        ax.set_xlabel(columns['x'], fontsize=11)
                        ax.set_ylabel(columns['y'], fontsize=11)
                        ax.grid(True, alpha=0.3, linestyle='--')
                        
            elif viz_type == 'bar_chart':
                if columns.get('x') and columns.get('y'):
                    if (columns['x'] in dataframe.columns and
                        columns['y'] in dataframe.columns):
                        # Grouper les données si nécessaire
                        if dataframe[columns['x']].dtype == 'object':
                            grouped_data = dataframe.groupby(columns['x'])[columns['y']].mean()
                            x_pos = np.arange(len(grouped_data))
                            ax.bar(x_pos, grouped_data.values, 
                                  color=colors[:len(grouped_data)], 
                                  alpha=0.7, edgecolor='black')
                            ax.set_xticks(x_pos)
                            ax.set_xticklabels(grouped_data.index, rotation=45, ha='right')
                        else:
                            ax.bar(dataframe[columns['x']], dataframe[columns['y']], 
                                  color=colors[0], alpha=0.7, edgecolor='black')
                            plt.xticks(rotation=45, ha='right')
                        ax.set_xlabel(columns['x'], fontsize=11)
                        ax.set_ylabel(columns['y'], fontsize=11)
                        ax.grid(axis='y', alpha=0.3, linestyle='--')
                        
            elif viz_type == 'line_chart':
                if columns.get('x') and columns.get('y'):
                    if (columns['x'] in dataframe.columns and
                        columns['y'] in dataframe.columns):
                        # Trier par x pour une ligne cohérente
                        sorted_data = dataframe.sort_values(columns['x'])
                        ax.plot(sorted_data[columns['x']], sorted_data[columns['y']], 
                               color=colors[0], linewidth=2, marker='o', markersize=6,
                               markerfacecolor=colors[1], markeredgecolor='black')
                        ax.set_xlabel(columns['x'], fontsize=11)
                        ax.set_ylabel(columns['y'], fontsize=11)
                        ax.grid(True, alpha=0.3, linestyle='--')
                        plt.xticks(rotation=45, ha='right')
                        
            elif viz_type == 'heatmap':
                numeric_columns = columns.get('columns', dataframe.select_dtypes(include=['number']).columns.tolist())
                if len(numeric_columns) > 1:
                    # Limiter à 10 colonnes pour la lisibilité
                    numeric_columns = numeric_columns[:10]
                    correlation_matrix = dataframe[numeric_columns].corr()
                    
                    # Créer la heatmap avec matplotlib
                    im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto',
                                  vmin=-1, vmax=1)
                    
                    # Ajouter une colorbar
                    cbar = plt.colorbar(im, ax=ax)
                    cbar.set_label('Corrélation', fontsize=11)
                    
                    # Ajouter les annotations
                    for i in range(len(correlation_matrix)):
                        for j in range(len(correlation_matrix.columns)):
                            ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                                   ha='center', va='center', color='black',
                                   fontsize=9)
                    
                    # Configurer les ticks
                    ax.set_xticks(np.arange(len(correlation_matrix.columns)))
                    ax.set_yticks(np.arange(len(correlation_matrix.index)))
                    ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
                    ax.set_yticklabels(correlation_matrix.index)
                else:
                    ax.text(
                        0.5,
                        0.5,
                        'Pas assez de colonnes numériques\npour une heatmap',
                        ha='center',
                        va='center',
                        transform=ax.transAxes,
                        fontsize=12
                    )
                           
            elif viz_type == 'boxplot':
                if columns.get('y') and columns['y'] in dataframe.columns:
                    if pd.api.types.is_numeric_dtype(dataframe[columns['y']]):
                        data_clean = dataframe[columns['y']].dropna()
                        bp = ax.boxplot([data_clean], tick_labels=[columns['y']], 
                                       patch_artist=True, widths=0.6)
                        # Personnaliser les couleurs
                        for patch in bp['boxes']:
                            patch.set_facecolor(colors[0])
                            patch.set_alpha(0.7)
                        for whisker in bp['whiskers']:
                            whisker.set(color='black', linewidth=1.5)
                        for cap in bp['caps']:
                            cap.set(color='black', linewidth=1.5)
                        for median in bp['medians']:
                            median.set(color='red', linewidth=2)
                        ax.set_ylabel('Valeurs', fontsize=11)
                        ax.grid(axis='y', alpha=0.3, linestyle='--')
                    else:
                        ax.text(0.5, 0.5, f'La colonne {columns["y"]} n\'est pas numérique',
                                ha='center', va='center', transform=ax.transAxes,
                                fontsize=12)
            
            # Ajouter le titre
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
            plt.tight_layout()
            
            # Convertir en base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return plot_base64
            
        except (IOError, RuntimeError, ValueError) as e:
            logger.error("Erreur lors de la création de la visualisation: %s", e)
            # Créer une image d'erreur
            _fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(
                0.5,
                0.5,
                f'Erreur lors de la création\nde la visualisation:\n{str(e)}',
                ha='center',
                va='center',
                transform=ax.transAxes,
                fontsize=12
            )
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
            
        except (IOError, RuntimeError, ValueError) as e:
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
            
        except (ValueError, RuntimeError, KeyError) as e:
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
            
        except (ValueError, RuntimeError, KeyError) as e:
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
        # Construire un dictionnaire de métadonnées avec des clés explicitement typées str
        metadata: Dict[str, Any] = {}
        metadata['viz_type'] = str(viz_type)
        metadata['title'] = str(title)
        # Stocker les colonnes sous forme de dict sérialisé pour éviter tout type exotique
        metadata['columns'] = columns if isinstance(columns, dict) else {}
        metadata['data_hash'] = str(data_hash)
        
        self.store_visualization(viz_id, viz_base64, metadata)
        
        return viz_base64, False
    
    def list_stored_visualizations(self) -> List[Dict[str, Any]]:
        """Retourne la liste des visualisations stockées."""
        try:
            results = self.viz_collection.get()

            ids_list = results.get('ids') or []
            metadatas_list = results.get('metadatas') or []

            visualizations: List[Dict[str, Any]] = []
            for i, viz_id in enumerate(ids_list):
                raw_meta: Any = metadatas_list[i] if i < len(metadatas_list) else {}
                # Normaliser la metadata en dict en évitant les None
                if raw_meta is None:
                    meta: Dict[str, Any] = {}
                else:
                    try:
                        meta = dict(raw_meta)  # type: ignore[arg-type]
                    except Exception:
                        meta = {}
                visualizations.append({
                    'id': viz_id,
                    'type': meta.get('viz_type', 'unknown'),
                    'title': meta.get('title', 'Sans titre'),
                    'columns': meta.get('columns', '{}')
                })

            return visualizations
            
        except (ValueError, RuntimeError, KeyError) as e:
            logger.error("Erreur lors de la liste des visualisations: %s", e)
            return []
    
    def clear_all_visualizations(self) -> bool:
        """Supprime toutes les visualisations stockées."""
        try:
            self.client.reset()
            self.viz_collection = self.client.create_collection("visualizations")
            logger.info("Toutes les visualisations ont été supprimées")
            return True
            
        except (ValueError, RuntimeError) as e:
            logger.error("Erreur lors de la suppression des visualisations: %s", e)
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les visualisations stockées."""
        try:
            total_viz = self.viz_collection.count()
            
            # Compter par type
            results = self.viz_collection.get()
            type_counts: Dict[str, int] = {}
            metadatas_seq = results.get('metadatas') or []

            for raw_meta in metadatas_seq:
                if not raw_meta:
                    continue
                try:
                    meta = dict(raw_meta)  # type: ignore[arg-type]
                except Exception:
                    meta = {}
                # Forcer la clé en chaîne pour respecter Dict[str, int]
                viz_type_key = str(meta.get('viz_type', 'unknown'))
                type_counts[viz_type_key] = type_counts.get(viz_type_key, 0) + 1
            
            return {
                'total_visualizations': total_viz,
                'by_type': type_counts,
                'db_path': self.db_path
            }
            
        except (ValueError, RuntimeError, KeyError) as e:
            logger.error("Erreur lors de la récupération des statistiques: %s", e)
            return {
                'total_visualizations': 0,
                'by_type': {},
                'db_path': self.db_path
            }