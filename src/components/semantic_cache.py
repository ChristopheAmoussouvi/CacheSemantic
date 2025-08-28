"""
Système de cache sémantique utilisant FAISS pour optimiser les requêtes répétitives.
Ce module permet de stocker et récupérer des réponses basées sur la similarité sémantique.
"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Tuple, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Classe pour gérer le cache sémantique avec FAISS.
    
    Utilise des embeddings pour déterminer la similarité entre les requêtes
    et retourne des réponses cachées si la similarité dépasse un seuil défini.
    """
    
    def __init__(
        self, 
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        threshold: float = 0.85,
        cache_dir: str = "./cache",
        max_cache_size: int = 1000
    ):
        """
        Initialise le cache sémantique.
        
        Args:
            embedding_model: Nom du modèle d'embedding à utiliser
            threshold: Seuil de similarité pour retourner une réponse cachée
            cache_dir: Répertoire où stocker le cache
            max_cache_size: Taille maximale du cache
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.threshold = threshold
        self.cache_dir = cache_dir
        self.max_cache_size = max_cache_size
        
        # Créer le répertoire de cache s'il n'existe pas
        os.makedirs(cache_dir, exist_ok=True)
        
        # Chemins des fichiers de cache
        self.index_path = os.path.join(cache_dir, "faiss_index.bin")
        self.metadata_path = os.path.join(cache_dir, "cache_metadata.pkl")
        
        # Initialiser l'index FAISS et les métadonnées
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product pour la similarité cosinus
        self.cache_metadata: List[Dict[str, Any]] = []
        
        # Charger le cache existant
        self._load_cache()
        
        logger.info(f"Cache sémantique initialisé avec {len(self.cache_metadata)} entrées")
    
    def _load_cache(self) -> None:
        """Charge le cache existant depuis le disque."""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # Charger l'index FAISS
                self.index = faiss.read_index(self.index_path)
                
                # Charger les métadonnées
                with open(self.metadata_path, 'rb') as f:
                    self.cache_metadata = pickle.load(f)
                
                logger.info(f"Cache chargé avec {len(self.cache_metadata)} entrées")
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du cache: {e}")
            # Réinitialiser en cas d'erreur
            self.index = faiss.IndexFlatIP(self.dimension)
            self.cache_metadata = []
    
    def _save_cache(self) -> None:
        """Sauvegarde le cache sur le disque."""
        try:
            # Sauvegarder l'index FAISS
            faiss.write_index(self.index, self.index_path)
            
            # Sauvegarder les métadonnées
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.cache_metadata, f)
                
            logger.debug("Cache sauvegardé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du cache: {e}")
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Normalise un embedding pour la similarité cosinus."""
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Génère l'embedding d'un texte."""
        embedding = self.embedding_model.encode(text)
        return self._normalize_embedding(embedding.astype(np.float32))
    
    def query(self, query_text: str, k: int = 5) -> Optional[Dict[str, Any]]:
        """
        Recherche une réponse dans le cache basée sur la similarité sémantique.
        
        Args:
            query_text: Texte de la requête
            k: Nombre de résultats similaires à récupérer
            
        Returns:
            Dictionnaire contenant la réponse si trouvée, None sinon
        """
        if not self.cache_metadata:
            return None
        
        try:
            # Générer l'embedding de la requête
            query_embedding = self._get_embedding(query_text)
            
            # Rechercher les voisins les plus proches
            similarities, indices = self.index.search(
                query_embedding.reshape(1, -1), 
                min(k, len(self.cache_metadata))
            )
            
            # Vérifier si la meilleure similarité dépasse le seuil
            if similarities[0][0] >= self.threshold:
                best_match_idx = indices[0][0]
                result = self.cache_metadata[best_match_idx].copy()
                result['similarity_score'] = float(similarities[0][0])
                result['cache_hit'] = True
                
                logger.info(f"Cache hit avec similarité: {similarities[0][0]:.3f}")
                return result
            
            logger.debug(f"Pas de cache hit, meilleure similarité: {similarities[0][0]:.3f}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la requête cache: {e}")
            return None
    
    def add(
        self, 
        query_text: str, 
        response: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Ajoute une nouvelle entrée au cache.
        
        Args:
            query_text: Texte de la requête
            response: Réponse à cacher
            metadata: Métadonnées supplémentaires
        """
        try:
            # Vérifier la taille du cache
            if len(self.cache_metadata) >= self.max_cache_size:
                self._evict_oldest()
            
            # Générer l'embedding
            embedding = self._get_embedding(query_text)
            
            # Ajouter à l'index FAISS
            self.index.add(embedding.reshape(1, -1))
            
            # Créer l'entrée de métadonnées
            cache_entry = {
                'query': query_text,
                'response': response,
                'metadata': metadata or {},
                'timestamp': np.datetime64('now')
            }
            
            self.cache_metadata.append(cache_entry)
            
            # Sauvegarder périodiquement
            if len(self.cache_metadata) % 10 == 0:
                self._save_cache()
            
            logger.debug(f"Ajouté au cache: {query_text[:50]}...")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout au cache: {e}")
    
    def _evict_oldest(self) -> None:
        """Supprime les entrées les plus anciennes du cache."""
        # Simple FIFO pour cette implémentation
        # Dans une version plus avancée, on pourrait utiliser LRU
        if self.cache_metadata:
            # Reconstruire l'index sans la première entrée
            if len(self.cache_metadata) > 1:
                new_index = faiss.IndexFlatIP(self.dimension)
                new_metadata = self.cache_metadata[1:]
                
                for entry in new_metadata:
                    embedding = self._get_embedding(entry['query'])
                    new_index.add(embedding.reshape(1, -1))
                
                self.index = new_index
                self.cache_metadata = new_metadata
                
                logger.debug("Éviction de l'entrée la plus ancienne du cache")
    
    def clear(self) -> None:
        """Vide complètement le cache."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.cache_metadata = []
        
        # Supprimer les fichiers de cache
        for path in [self.index_path, self.metadata_path]:
            if os.path.exists(path):
                os.remove(path)
        
        logger.info("Cache vidé")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le cache."""
        return {
            'total_entries': len(self.cache_metadata),
            'threshold': self.threshold,
            'max_size': self.max_cache_size,
            'dimension': self.dimension,
            'model': self.embedding_model.get_sentence_embedding_dimension()
        }
    
    def __del__(self):
        """Sauvegarde le cache lors de la destruction de l'objet."""
        try:
            self._save_cache()
        except:
            pass
