"""
Gestionnaire de base de données vectorielle avec ChromaDB pour le stockage persistant.
Ce module gère l'indexation et la recherche de données structurées.
"""

import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, cast
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """
    Gestionnaire pour ChromaDB avec persistance.
    
    Gère l'indexation des données CSV/Excel et la recherche vectorielle
    pour permettre l'interrogation en langage naturel.
    """
    
    def __init__(
        self,
        db_path: str = "./chroma_db",
        collection_name: str = "data_collection",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialise le gestionnaire de données.
        
        Args:
            db_path: Chemin vers la base de données ChromaDB
            collection_name: Nom de la collection ChromaDB
            embedding_model: Modèle d'embedding à utiliser
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Créer le répertoire de base de données
        os.makedirs(db_path, exist_ok=True)
        
        # Initialiser ChromaDB avec persistance
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Fonction d'embedding
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Obtenir ou créer la collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name
            )
            logger.info(f"Collection '{collection_name}' chargée")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name
            )
            logger.info(f"Nouvelle collection '{collection_name}' créée")
        
        # Métadonnées des fichiers chargés
        self.loaded_files: Dict[str, Dict[str, Any]] = {}
    
    def load_data_file(self, file_path: str, chunk_size: int = 1000) -> bool:
        """
        Charge un fichier CSV ou Excel dans ChromaDB.
        
        Args:
            file_path: Chemin vers le fichier à charger
            chunk_size: Taille des chunks pour le traitement
            
        Returns:
            True si le chargement a réussi, False sinon
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"Fichier non trouvé: {file_path_obj}")
                return False
            
            # Charger le fichier selon son extension
            if file_path_obj.suffix.lower() == '.csv':
                df = pd.read_csv(file_path_obj)
            elif file_path_obj.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path_obj)
            else:
                logger.error(f"Format de fichier non supporté: {file_path_obj.suffix}")
                return False
            
            logger.info(f"Fichier chargé: {file_path_obj.name} ({len(df)} lignes, {len(df.columns)} colonnes)")
            
            # Créer un identifiant unique pour le fichier
            file_id = file_path_obj.stem
            
            # Supprimer les données existantes pour ce fichier
            self._remove_file_data(file_id)
            
            # Préparer les documents pour l'indexation
            documents = []
            metadatas = []
            ids = []
            
            # Créer une description du schéma
            schema_description = self._create_schema_description(df, file_path_obj.name)
            documents.append(schema_description)
            metadatas.append({
                'type': 'schema',
                'file_id': file_id,
                'file_name': file_path_obj.name,
                'num_rows': len(df),
                'num_cols': len(df.columns),
                'columns': ','.join(df.columns.tolist())
            })
            ids.append(f"{file_id}_schema")
            
            # Indexer les données par chunks
            for chunk_start in range(0, len(df), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(df))
                chunk_df = df.iloc[chunk_start:chunk_end]
                
                # Créer une description textuelle du chunk
                chunk_description = self._create_chunk_description(
                    chunk_df, chunk_start, chunk_end, file_path_obj.name
                )
                
                documents.append(chunk_description)
                metadatas.append({
                    'type': 'data_chunk',
                    'file_id': file_id,
                    'file_name': file_path_obj.name,
                    'chunk_start': chunk_start,
                    'chunk_end': chunk_end,
                    'chunk_size': len(chunk_df)
                })
                ids.append(f"{file_id}_chunk_{chunk_start}_{chunk_end}")
            
            # Ajouter à ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # Sauvegarder les métadonnées du fichier
            self.loaded_files[file_id] = {
                'file_name': file_path_obj.name,
                'file_path': str(file_path_obj),
                'num_rows': len(df),
                'num_cols': len(df.columns),
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.to_dict(),
                'sample_data': df.head(3).to_dict('records')
            }
            
            logger.info(f"Fichier '{file_path_obj.name}' indexé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier: {e}")
            return False
    
    def _remove_file_data(self, file_id: str) -> None:
        """Supprime toutes les données d'un fichier de la collection."""
        try:
            # Rechercher tous les documents liés à ce fichier
            results = self.collection.get(
                where=cast(Any, {"file_id": file_id})  # Type cast to avoid ChromaDB type strictness
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.debug(f"Supprimé {len(results['ids'])} documents pour {file_id}")
        except Exception as e:
            logger.warning(f"Erreur lors de la suppression des données existantes: {e}")
    
    def _create_schema_description(self, df: pd.DataFrame, file_name: str) -> str:
        """Crée une description textuelle du schéma des données."""
        description = f"Fichier: {file_name}\n"
        description += f"Nombre de lignes: {len(df)}\n"
        description += f"Nombre de colonnes: {len(df.columns)}\n\n"
        description += "Colonnes et types de données:\n"
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null_count = df[col].count()
            null_count = len(df) - non_null_count
            
            description += f"- {col} ({dtype}): {non_null_count} valeurs non-nulles"
            if null_count > 0:
                description += f", {null_count} valeurs manquantes"
            description += "\n"
            
            # Ajouter des exemples de valeurs pour les colonnes catégorielles
            if df[col].dtype == 'object' and df[col].nunique() <= 10:
                unique_vals = df[col].dropna().unique()[:5]
                description += f"  Exemples: {', '.join(map(str, unique_vals))}\n"
        
        return description
    
    def _create_chunk_description(
        self, 
        chunk_df: pd.DataFrame, 
        start_idx: int, 
        end_idx: int, 
        file_name: str
    ) -> str:
        """Crée une description textuelle d'un chunk de données."""
        description = f"Données du fichier {file_name} (lignes {start_idx} à {end_idx-1}):\n\n"
        
        # Statistiques descriptives pour les colonnes numériques
        numeric_cols = chunk_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            description += "Statistiques numériques:\n"
            for col in numeric_cols:
                if chunk_df[col].count() > 0:
                    description += f"- {col}: min={chunk_df[col].min():.2f}, "
                    description += f"max={chunk_df[col].max():.2f}, "
                    description += f"moyenne={chunk_df[col].mean():.2f}\n"
        
        # Valeurs fréquentes pour les colonnes catégorielles
        categorical_cols = chunk_df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            description += "\nValeurs catégorielles:\n"
            for col in categorical_cols[:3]:  # Limiter à 3 colonnes
                value_counts = chunk_df[col].value_counts().head(3)
                if len(value_counts) > 0:
                    description += f"- {col}: {dict(value_counts)}\n"
        
        # Échantillon de données
        description += "\nÉchantillon de données:\n"
        sample_size = min(3, len(chunk_df))
        for i in range(sample_size):
            row = chunk_df.iloc[i]
            description += f"Ligne {start_idx + i}: "
            description += ", ".join([f"{col}={row[col]}" for col in chunk_df.columns[:5]])
            if len(chunk_df.columns) > 5:
                description += "..."
            description += "\n"
        
        return description
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        file_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche dans la base de données vectorielle.
        
        Args:
            query: Requête de recherche
            n_results: Nombre de résultats à retourner
            file_filter: Filtrer par identifiant de fichier
            
        Returns:
            Liste des résultats de recherche
        """
        try:
            # Construire le filtre where si nécessaire
            where_filter = None
            if file_filter:
                where_filter = {"file_id": file_filter}
            
            # Effectuer la recherche
            if where_filter:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=cast(Any, where_filter)  # Type cast to avoid ChromaDB type strictness
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
            
            # Formatter les résultats
            formatted_results = []
            if results and 'ids' in results and results['ids']:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i] if results['documents'] else None,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else None,
                        'distance': results['distances'][0][i] if 'distances' in results and results['distances'] else None
                    }
                    formatted_results.append(result)
            
            logger.debug(f"Recherche '{query}' a retourné {len(formatted_results)} résultats")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def get_file_info(self, file_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retourne les informations sur les fichiers chargés.
        
        Args:
            file_id: Identifiant du fichier spécifique (optionnel)
            
        Returns:
            Informations sur le(s) fichier(s)
        """
        if file_id:
            return self.loaded_files.get(file_id, {})
        return self.loaded_files
    
    def list_files(self) -> List[str]:
        """Retourne la liste des fichiers chargés."""
        return list(self.loaded_files.keys())
    
    def remove_file(self, file_id: str) -> bool:
        """
        Supprime un fichier de la base de données.
        
        Args:
            file_id: Identifiant du fichier à supprimer
            
        Returns:
            True si la suppression a réussi
        """
        try:
            self._remove_file_data(file_id)
            if file_id in self.loaded_files:
                del self.loaded_files[file_id]
            logger.info(f"Fichier '{file_id}' supprimé")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier: {e}")
            return False
    
    def reset_database(self) -> bool:
        """Remet à zéro toute la base de données."""
        try:
            self.client.reset()
            self.collection = self.client.create_collection(
                name=self.collection_name
            )
            self.loaded_files = {}
            logger.info("Base de données réinitialisée")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur la base de données."""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'loaded_files': len(self.loaded_files),
                'files': list(self.loaded_files.keys()),
                'embedding_model': self.embedding_model
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}
