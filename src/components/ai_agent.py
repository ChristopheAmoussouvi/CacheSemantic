# Agent IA local sans dependances LLM

import pandas as pd
from typing import Dict, Any, List, Optional
import logging

from .simple_cache import SimpleCache
from .data_manager import DataManager
from .decision_tree_chatbot import DecisionTreeChatbot
from .visualization_manager import VisualizationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalAIAgent:
    def __init__(
        self,
        data_manager: DataManager,
        simple_cache: SimpleCache,
        viz_manager: Optional[VisualizationManager] = None
    ):
        self.data_manager = data_manager
        self.simple_cache = simple_cache
        self.viz_manager = viz_manager or VisualizationManager()
        self.chatbot = DecisionTreeChatbot()
        self.current_dataframe = None
        self.current_file_info = None
        self.conversation_history = []
        logger.info("Agent IA local initialise")
    
    def load_data_for_analysis(self, file_path: str) -> bool:
        try:
            if file_path.endswith('.csv'):
                self.current_dataframe = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.current_dataframe = pd.read_excel(file_path)
            else:
                logger.error("Format de fichier non supporte")
                return False
            
            self.current_file_info = {
                'file_path': file_path,
                'shape': self.current_dataframe.shape,
                'columns': list(self.current_dataframe.columns),
                'dtypes': dict(self.current_dataframe.dtypes.astype(str))
            }
            
            logger.info("Donnees chargees: %d lignes, %d colonnes", 
                       len(self.current_dataframe), len(self.current_dataframe.columns))
            return True
            
        except Exception as e:
            logger.error("Erreur lors du chargement des donnees: %s", str(e))
            return False
    
    def process_query(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        try:
            self.conversation_history.append({'role': 'user', 'content': query})
            
            if use_cache:
                cached_result = self.simple_cache.get(query)
                if cached_result:
                    logger.info("Reponse recuperee du cache semantique")
                    response = {
                        'response': cached_result['response'],
                        'source': 'cache',
                        'similarity_score': cached_result.get('similarity_score'),
                        'visualization': cached_result.get('visualization')
                    }
                    self.conversation_history.append({'role': 'assistant', 'content': response['response']})
                    return response
            
            analysis = self.chatbot.analyze_query(query, self.current_dataframe)
            
            if not analysis['success']:
                response = {
                    'response': analysis['message'],
                    'source': 'chatbot',
                    'success': False
                }
                self.conversation_history.append({'role': 'assistant', 'content': response['response']})
                return response
            
            if analysis['action'] == 'summary':
                result = self._handle_summary_request(analysis['parameters'])
            elif analysis['action'] == 'visualization':
                result = self._handle_visualization_request(analysis['parameters'])
            elif analysis['action'] == 'analysis':
                result = self._handle_analysis_request(analysis['parameters'])
            else:
                result = {
                    'response': "Je ne sais pas comment traiter cette requete.",
                    'source': 'chatbot',
                    'success': False
                }
            
            if use_cache and result.get('success', True):
                self.simple_cache.put(query, result)
            
            self.conversation_history.append({'role': 'assistant', 'content': result['response']})
            return result
            
        except Exception as e:
            logger.error("Erreur lors du traitement de la requete: %s", str(e))
            error_response = {
                'response': f"Desole, une erreur s'est produite: {str(e)}",
                'source': 'error',
                'success': False
            }
            self.conversation_history.append({'role': 'assistant', 'content': error_response['response']})
            return error_response
    
    def _handle_summary_request(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if self.current_dataframe is None:
                return {
                    'response': "Aucune donnee n'est disponible pour creer un resume.",
                    'source': 'local_agent',
                    'success': False
                }
            
            summary_parts = []
            summary_parts.append("Resume des donnees")
            summary_parts.append(f"- Nombre de lignes: {len(self.current_dataframe):,}")
            summary_parts.append(f"- Nombre de colonnes: {len(self.current_dataframe.columns)}")
            
            summary_parts.append("Colonnes disponibles:")
            for col in self.current_dataframe.columns:
                dtype = str(self.current_dataframe[col].dtype)
                null_count = self.current_dataframe[col].isnull().sum()
                summary_parts.append(f"- {col} ({dtype})")
                if null_count > 0:
                    summary_parts.append(f"  {null_count} valeurs manquantes")
            
            numeric_cols = self.current_dataframe.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary_parts.append("Statistiques numeriques:")
                for col in numeric_cols[:5]:
                    stats = self.current_dataframe[col].describe()
                    summary_parts.append(f"- {col}: Moy={stats['mean']:.2f}, Min={stats['min']:.2f}, Max={stats['max']:.2f}")
            
            response_text = "\n".join(summary_parts)
            
            return {
                'response': response_text,
                'source': 'local_agent',
                'success': True,
                'action': 'summary'
            }
            
        except Exception as e:
            logger.error("Erreur lors de la generation du resume: %s", str(e))
            return {
                'response': f"Erreur lors de la generation du resume: {str(e)}",
                'source': 'local_agent',
                'success': False
            }
    
    def _handle_visualization_request(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if self.current_dataframe is None:
                return {
                    'response': "Aucune donnee n'est disponible pour creer une visualisation.",
                    'source': 'local_agent',
                    'success': False
                }
            
            viz_type = parameters.get('viz_type', 'bar_chart')
            columns = parameters.get('columns', {})
            title = parameters.get('title', 'Visualisation des donnees')
            
            viz_base64, from_cache = self.viz_manager.get_or_create_visualization(
                viz_type=viz_type,
                dataframe=self.current_dataframe,
                columns=columns,
                title=title
            )
            
            cache_info = " (recuperee du cache)" if from_cache else " (nouvellement creee)"
            response_text = f"Visualisation creee: {title}{cache_info}"
            
            return {
                'response': response_text,
                'source': 'local_agent',
                'success': True,
                'visualization': viz_base64,
                'action': 'visualization',
                'from_cache': from_cache
            }
            
        except Exception as e:
            logger.error("Erreur lors de la creation de la visualisation: %s", str(e))
            return {
                'response': f"Erreur lors de la creation de la visualisation: {str(e)}",
                'source': 'local_agent',
                'success': False
            }
    
    def _handle_analysis_request(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if self.current_dataframe is None:
                return {
                    'response': "Aucune donnee n'est disponible pour l'analyse.",
                    'source': 'local_agent',
                    'success': False
                }
            
            analysis_type = parameters.get('analysis_type', 'describe')
            columns = parameters.get('columns', [])
            
            valid_columns = [col for col in columns if col in self.current_dataframe.columns]
            if not valid_columns:
                valid_columns = list(self.current_dataframe.columns)
            
            result_parts = []
            
            if analysis_type == 'mean':
                numeric_cols = [col for col in valid_columns if self.current_dataframe[col].dtype in ['float64', 'int64']]
                if numeric_cols:
                    result_parts.append("Moyennes calculees:")
                    for col in numeric_cols:
                        mean_val = self.current_dataframe[col].mean()
                        result_parts.append(f"- {col}: {mean_val:.2f}")
                else:
                    result_parts.append("Aucune colonne numerique disponible pour calculer la moyenne.")
            
            elif analysis_type == 'describe':
                numeric_cols = [col for col in valid_columns if self.current_dataframe[col].dtype in ['float64', 'int64']]
                if numeric_cols:
                    result_parts.append("Analyse descriptive:")
                    desc = self.current_dataframe[numeric_cols].describe()
                    for col in numeric_cols[:5]:
                        stats = desc[col]
                        result_parts.append(f"{col}:")
                        result_parts.append(f"  - Moyenne: {stats['mean']:.2f}")
                        result_parts.append(f"  - Ecart-type: {stats['std']:.2f}")
                        result_parts.append(f"  - Min: {stats['min']:.2f}, Max: {stats['max']:.2f}")
                        result_parts.append(f"  - Mediane: {stats['50%']:.2f}")
                else:
                    result_parts.append("Aucune colonne numerique disponible pour l'analyse descriptive.")
            
            response_text = "\n".join(result_parts) if result_parts else "Aucun resultat d'analyse disponible."
            
            return {
                'response': response_text,
                'source': 'local_agent',
                'success': True,
                'action': 'analysis'
            }
            
        except Exception as e:
            logger.error("Erreur lors de l'analyse: %s", str(e))
            return {
                'response': f"Erreur lors de l'analyse: {str(e)}",
                'source': 'local_agent',
                'success': False
            }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        self.conversation_history = []
        logger.info("Historique de conversation efface")
    
    def get_data_summary(self) -> Dict[str, Any]:
        if self.current_dataframe is None:
            return {'message': 'Aucune donnee chargee'}
        
        return {
            'shape': self.current_dataframe.shape,
            'columns': list(self.current_dataframe.columns),
            'dtypes': dict(self.current_dataframe.dtypes.astype(str)),
            'missing_values': dict(self.current_dataframe.isnull().sum()),
            'sample': self.current_dataframe.head(3).to_dict('records')
        }
    
    def get_help_message(self) -> str:
        return self.chatbot.get_help_message()
    
    def get_viz_stats(self) -> Dict[str, Any]:
        return self.viz_manager.get_stats()