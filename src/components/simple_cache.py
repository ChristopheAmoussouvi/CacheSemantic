"""
Système de cache simple pour les requêtes locales.
Version allégée sans dépendances lourdes (sentence-transformers).
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Classe pour gérer un cache simple basé sur des hashes de requêtes.
    Version légère sans embedding models pour un fonctionnement purement local.
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialise le cache simple.
        
        Args:
            cache_dir: Répertoire pour stocker les fichiers de cache
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "simple_cache.json")
        self.cache_data = {}
        
        # Créer le répertoire de cache s'il n'existe pas
        os.makedirs(cache_dir, exist_ok=True)
        
        # Charger le cache existant
        self._load_cache()
        
        logger.info(f"Cache simple initialisé avec {len(self.cache_data)} entrées")
    
    def _load_cache(self):
        """Charge les données de cache depuis le fichier JSON."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache_data = json.load(f)
                logger.info(f"Cache chargé: {len(self.cache_data)} entrées")
            else:
                self.cache_data = {}
                logger.info("Nouveau cache créé")
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du cache: {e}")
            self.cache_data = {}
    
    def _save_cache(self):
        """Sauvegarde les données de cache dans le fichier JSON."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            logger.debug("Cache sauvegardé")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du cache: {e}")
    
    def _get_query_hash(self, query: str) -> str:
        """
        Génère un hash pour une requête.
        
        Args:
            query: La requête à hasher
            
        Returns:
            Hash MD5 de la requête normalisée
        """
        # Normaliser la requête (minuscules, espaces)
        normalized_query = query.lower().strip()
        return hashlib.md5(normalized_query.encode('utf-8')).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une réponse du cache si elle existe.
        
        Args:
            query: La requête à rechercher
            
        Returns:
            Dictionnaire avec la réponse mise en cache ou None
        """
        query_hash = self._get_query_hash(query)
        
        if query_hash in self.cache_data:
            cached_response = self.cache_data[query_hash]
            logger.info(f"Réponse trouvée dans le cache pour: {query[:50]}...")
            return cached_response
        
        return None
    
    def put(self, query: str, response: Dict[str, Any]):
        """
        Met en cache une réponse pour une requête.
        
        Args:
            query: La requête originale
            response: La réponse à mettre en cache
        """
        query_hash = self._get_query_hash(query)
        # Ajouter des métadonnées
        cache_entry = {
            "original_query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        self.cache_data[query_hash] = cache_entry
        self._save_cache()
        
        logger.info(f"Réponse mise en cache pour: {query[:50]}...")
    
    def clear(self):
        """Vide le cache."""
        self.cache_data = {}
        self._save_cache()
        logger.info("Cache vidé")
    
    def size(self) -> int:
        """Retourne le nombre d'entrées dans le cache."""
        return len(self.cache_data)
    
    def list_queries(self) -> list:
        """Retourne la liste des requêtes mises en cache."""
        return [entry["original_query"] for entry in self.cache_data.values()]
    
    def get_stats(self) -> dict:
        """Retourne les statistiques du cache."""
        return {
            "cache_size": len(self.cache_data),
            "total_queries": len(self.cache_data),
            "cache_file": self.cache_file
        }