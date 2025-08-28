"""
Agent IA utilisant LangChain pour l'interaction en langage naturel avec les données.
Intègre le cache sémantique et la génération de visualisations.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
import logging

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from langchain.tools import BaseTool

from .semantic_cache import SemanticCache
from .data_manager import DataManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisualizationTool(BaseTool):
    """Outil personnalisé pour générer des visualisations."""
    
    name: str = "create_visualization"
    description: str = """
    Créer des visualisations de données avec matplotlib/seaborn.
    Paramètres attendus en JSON:
    {
        "plot_type": "histogram|scatter|line|bar|heatmap|boxplot",
        "data": "données au format dict ou liste",
        "x_col": "nom de la colonne x",
        "y_col": "nom de la colonne y (optionnel)",
        "title": "titre du graphique",
        "style": "style du graphique (optionnel)"
    }
    """
    
    def _run(self, query: str, run_manager=None) -> str:
        """Exécute la création de visualisation."""
        try:
            # Parser les paramètres JSON
            params = json.loads(query)
            return self._create_plot(params)
        except Exception as e:
            return f"Erreur lors de la création de la visualisation: {str(e)}"
    
    def _create_plot(self, params: Dict[str, Any]) -> str:
        """Crée le graphique selon les paramètres."""
        try:
            plot_type = params.get('plot_type', 'bar')
            data = params.get('data', {})
            x_col = params.get('x_col')
            y_col = params.get('y_col')
            title = params.get('title', 'Visualisation')
            
            # Convertir les données en DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                return "Format de données non valide"
            
            # Configurer le style
            plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Créer le graphique selon le type
            if plot_type == 'histogram':
                if x_col and x_col in df.columns:
                    ax.hist(df[x_col].dropna(), bins=20, alpha=0.7)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel('Fréquence')
            
            elif plot_type == 'scatter':
                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                    ax.scatter(df[x_col], df[y_col], alpha=0.6)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
            
            elif plot_type == 'line':
                if x_col and y_col and x_col in df.columns and y_col in df.columns:
                    ax.plot(df[x_col], df[y_col], marker='o')
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
            
            elif plot_type == 'bar':
                if x_col and x_col in df.columns:
                    if y_col and y_col in df.columns:
                        ax.bar(df[x_col], df[y_col])
                        ax.set_ylabel(y_col)
                    else:
                        value_counts = df[x_col].value_counts()
                        ax.bar(range(len(value_counts)), value_counts.values)
                        ax.set_xticks(range(len(value_counts)))
                        ax.set_xticklabels(value_counts.index, rotation=45)
                        ax.set_ylabel('Nombre')
                    ax.set_xlabel(x_col)
            
            elif plot_type == 'heatmap':
                # Sélectionner seulement les colonnes numériques
                numeric_df = df.select_dtypes(include=['number'])
                if not numeric_df.empty:
                    correlation_matrix = numeric_df.corr()
                    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
                else:
                    return "Aucune donnée numérique pour créer une heatmap"
            
            elif plot_type == 'boxplot':
                if x_col and x_col in df.columns:
                    if df[x_col].dtype in ['float64', 'int64']:
                        ax.boxplot(df[x_col].dropna())
                        ax.set_ylabel(x_col)
                    else:
                        return f"La colonne {x_col} n'est pas numérique"
            
            # Ajouter le titre
            ax.set_title(title)
            plt.tight_layout()
            
            # Convertir en base64 pour l'affichage
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"VISUALIZATION_CREATED:{plot_base64}"
            
        except Exception as e:
            return f"Erreur lors de la création du graphique: {str(e)}"


class AIAgent:
    """
    Agent IA pour l'interaction en langage naturel avec les données.
    
    Intègre le cache sémantique, ChromaDB et la génération de visualisations.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        data_manager: DataManager,
        semantic_cache: SemanticCache,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.1
    ):
        """
        Initialise l'agent IA.
        
        Args:
            openai_api_key: Clé API OpenAI
            data_manager: Instance du gestionnaire de données
            semantic_cache: Instance du cache sémantique
            model_name: Nom du modèle LLM à utiliser
            temperature: Température pour le modèle
        """
        self.data_manager = data_manager
        self.semantic_cache = semantic_cache
        
        # Initialiser le modèle LLM
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model_name,
            temperature=temperature
        )
        
        # Mémoire de conversation
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Outil de visualisation
        self.viz_tool = VisualizationTool()
        
        # Agent pandas (sera créé dynamiquement selon les données)
        self.current_agent = None
        self.current_dataframe = None
        
        logger.info("Agent IA initialisé")
    
    def load_data_for_analysis(self, file_path: str) -> bool:
        """
        Charge des données pour l'analyse directe avec pandas.
        
        Args:
            file_path: Chemin vers le fichier de données
            
        Returns:
            True si le chargement a réussi
        """
        try:
            # Charger le fichier dans un DataFrame
            if file_path.endswith('.csv'):
                self.current_dataframe = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.current_dataframe = pd.read_excel(file_path)
            else:
                logger.error("Format de fichier non supporté")
                return False
            
            # Créer un agent pandas
            self.current_agent = create_pandas_dataframe_agent(
                llm=self.llm,
                df=self.current_dataframe,
                verbose=True,
                allow_dangerous_code=True,  # Nécessaire pour l'exécution de code
                handle_parsing_errors=True
            )
            
            logger.info(f"Données chargées: {len(self.current_dataframe)} lignes, {len(self.current_dataframe.columns)} colonnes")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            return False
    
    def process_query(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Traite une requête utilisateur en langage naturel.
        
        Args:
            query: Requête utilisateur
            use_cache: Utiliser le cache sémantique
            
        Returns:
            Dictionnaire contenant la réponse et les métadonnées
        """
        try:
            # Vérifier le cache sémantique en premier
            if use_cache:
                cached_result = self.semantic_cache.query(query)
                if cached_result:
                    logger.info("Réponse récupérée du cache sémantique")
                    return {
                        'response': cached_result['response'],
                        'source': 'cache',
                        'similarity_score': cached_result.get('similarity_score'),
                        'visualization': cached_result.get('visualization')
                    }
            
            # Déterminer le type de requête
            query_type = self._classify_query(query)
            
            if query_type == 'visualization':
                result = self._handle_visualization_query(query)
            elif query_type == 'data_analysis':
                result = self._handle_data_analysis_query(query)
            else:
                result = self._handle_general_query(query)
            
            # Ajouter au cache si la requête a réussi
            if use_cache and result.get('success', True):
                self.semantic_cache.add(
                    query_text=query,
                    response=result['response'],
                    metadata={
                        'query_type': query_type,
                        'visualization': result.get('visualization')
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la requête: {e}")
            return {
                'response': f"Désolé, une erreur s'est produite: {str(e)}",
                'source': 'error',
                'success': False
            }
    
    def _classify_query(self, query: str) -> str:
        """Classifie le type de requête."""
        visualization_keywords = [
            'graphique', 'graph', 'plot', 'visualisation', 'chart',
            'histogram', 'scatter', 'ligne', 'barres', 'heatmap',
            'boxplot', 'distribution', 'corrélation', 'trend'
        ]
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in visualization_keywords):
            return 'visualization'
        elif self.current_dataframe is not None:
            return 'data_analysis'
        else:
            return 'general'
    
    def _handle_visualization_query(self, query: str) -> Dict[str, Any]:
        """Traite une requête de visualisation."""
        try:
            if self.current_dataframe is None or self.current_agent is None:
                return {
                    'response': "Aucune donnée n'est actuellement chargée pour créer des visualisations.",
                    'source': 'agent',
                    'success': False
                }
            
            # Utiliser l'agent pandas pour analyser la requête et créer les paramètres
            analysis_prompt = f"""
            Analysez cette requête de visualisation: "{query}"
            
            Données disponibles:
            - Colonnes: {list(self.current_dataframe.columns)}
            - Types: {dict(self.current_dataframe.dtypes)}
            - Shape: {self.current_dataframe.shape}
            
            Créez les paramètres JSON pour la visualisation au format:
            {{
                "plot_type": "histogram|scatter|line|bar|heatmap|boxplot",
                "data": <échantillon des données>,
                "x_col": "nom_colonne_x",
                "y_col": "nom_colonne_y",
                "title": "titre descriptif"
            }}
            
            Retournez SEULEMENT le JSON, sans autre texte.
            """
            
            # Obtenir les paramètres de visualisation
            result = self.current_agent.invoke({"input": analysis_prompt})
            viz_params = result.get("output", "") if isinstance(result, dict) else str(result)
            
            # Nettoyer la réponse pour extraire le JSON
            import re
            json_match = re.search(r'\{.*\}', viz_params, re.DOTALL)
            if json_match:
                viz_params = json_match.group(0)
            
            # Créer la visualisation
            viz_result = self.viz_tool._run(viz_params)
            
            if viz_result.startswith("VISUALIZATION_CREATED:"):
                plot_base64 = viz_result.replace("VISUALIZATION_CREATED:", "")
                return {
                    'response': f"Visualisation créée pour: {query}",
                    'source': 'agent',
                    'success': True,
                    'visualization': plot_base64
                }
            else:
                return {
                    'response': f"Erreur lors de la création de la visualisation: {viz_result}",
                    'source': 'agent',
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la visualisation: {e}")
            return {
                'response': f"Erreur lors de la création de la visualisation: {str(e)}",
                'source': 'agent',
                'success': False
            }
    
    def _handle_data_analysis_query(self, query: str) -> Dict[str, Any]:
        """Traite une requête d'analyse de données."""
        try:
            if self.current_agent is None:
                return {
                    'response': "Aucune donnée n'est actuellement chargée pour l'analyse.",
                    'source': 'agent',
                    'success': False
                }
            
            # Utiliser l'agent pandas pour analyser les données
            result = self.current_agent.invoke({"input": query})
            response = result.get("output", "") if isinstance(result, dict) else str(result)
            
            return {
                'response': response,
                'source': 'pandas_agent',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des données: {e}")
            return {
                'response': f"Erreur lors de l'analyse: {str(e)}",
                'source': 'agent',
                'success': False
            }
    
    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Traite une requête générale."""
        try:
            # Rechercher dans ChromaDB pour le contexte
            search_results = self.data_manager.search(query, n_results=3)
            
            # Construire le contexte
            context = "Informations disponibles dans la base de données:\n"
            for result in search_results:
                context += f"- {result['document'][:200]}...\n"
            
            # Construire le prompt avec contexte
            prompt = f"""
            Contexte des données disponibles:
            {context}
            
            Question de l'utilisateur: {query}
            
            Répondez de manière claire et concise en français, en utilisant les informations disponibles.
            Si vous ne trouvez pas d'information pertinente, dites-le clairement.
            """
            
            # Obtenir la réponse du LLM
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                'response': response.content,
                'source': 'llm_with_context',
                'success': True,
                'context_used': len(search_results) > 0
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la requête générale: {e}")
            return {
                'response': f"Erreur lors du traitement: {str(e)}",
                'source': 'agent',
                'success': False
            }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique de conversation."""
        try:
            messages = self.memory.chat_memory.messages
            history = []
            
            for message in messages:
                if isinstance(message, HumanMessage):
                    history.append({'role': 'user', 'content': message.content})
                elif isinstance(message, AIMessage):
                    history.append({'role': 'assistant', 'content': message.content})
            
            return history
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def clear_conversation_history(self):
        """Efface l'historique de conversation."""
        self.memory.clear()
        logger.info("Historique de conversation effacé")
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des données actuellement chargées."""
        if self.current_dataframe is None:
            return {'message': 'Aucune donnée chargée'}
        
        return {
            'shape': self.current_dataframe.shape,
            'columns': list(self.current_dataframe.columns),
            'dtypes': dict(self.current_dataframe.dtypes.astype(str)),
            'missing_values': dict(self.current_dataframe.isnull().sum()),
            'sample': self.current_dataframe.head(3).to_dict('records')
        }
