"""
Chatbot basé sur un arbre de décision pour l'analyse de données.
Remplace le LLM OpenAI par une approche déterministe et locale.
"""

import re
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionTreeChatbot:
    """
    Chatbot utilisant un arbre de décision pour analyser les requêtes utilisateur
    et déterminer les actions appropriées sans LLM externe.
    """
    
    def __init__(self):
        """Initialise le chatbot avec les règles de décision."""
        self.keywords = self._build_keyword_patterns()
        self.responses = self._build_responses()
        
        logger.info("Chatbot Decision Tree initialisé")
    
    def _build_keyword_patterns(self) -> Dict[str, List[str]]:
        """Construit les patterns de mots-clés pour la classification."""
        return {
            'summary': [
                'résumé', 'summary', 'aperçu', 'overview', 'description',
                'statistiques', 'stats', 'info', 'informations', 'données'
            ],
            'visualization': [
                'graphique', 'graph', 'plot', 'visualisation', 'chart',
                'histogram', 'histogramme', 'scatter', 'nuage', 'barres',
                'ligne', 'line', 'heatmap', 'corrélation', 'boxplot',
                'distribution', 'tendance', 'trend'
            ],
            'analysis': [
                'analyse', 'analyser', 'comparer', 'compare', 'calcul',
                'moyenne', 'mean', 'médiane', 'median', 'maximum', 'minimum',
                'somme', 'sum', 'total', 'count', 'nombre'
            ],
            'filter': [
                'filtre', 'filter', 'où', 'where', 'contient', 'égal',
                'supérieur', 'inférieur', 'entre', 'between'
            ],
            'correlation': [
                'corrélation', 'correlation', 'relation', 'lien',
                'dépendance', 'influence'
            ],
            'time_series': [
                'temps', 'time', 'date', 'évolution', 'tendance',
                'progression', 'série temporelle'
            ]
        }
    
    def _build_responses(self) -> Dict[str, str]:
        """Construit les réponses templates."""
        return {
            'summary': "Je vais vous montrer un résumé statistique des données.",
            'histogram': "Je vais créer un histogramme pour visualiser la distribution.",
            'scatter': "Je vais créer un graphique en nuage de points pour voir les relations.",
            'bar_chart': "Je vais créer un graphique en barres pour comparer les catégories.",
            'line_chart': "Je vais créer un graphique linéaire pour voir l'évolution.",
            'heatmap': "Je vais créer une heatmap pour visualiser les corrélations.",
            'boxplot': "Je vais créer un boxplot pour analyser la distribution et les outliers.",
            'analysis': "Je vais effectuer l'analyse demandée sur les données.",
            'error': "Je ne comprends pas votre demande. Pouvez-vous reformuler ?",
            'no_data': "Aucune donnée n'est actuellement chargée."
        }
    
    def analyze_query(self, query: str, dataframe: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Analyse la requête utilisateur et détermine l'action appropriée.
        
        Args:
            query: Requête utilisateur
            dataframe: DataFrame pandas des données chargées
            
        Returns:
            Dictionnaire avec l'action déterminée et les paramètres
        """
        if dataframe is None or dataframe.empty:
            return {
                'action': 'error',
                'message': self.responses['no_data'],
                'success': False
            }
        
        query_lower = query.lower()
        
        # Étape 1: Déterminer le type d'action principal
        action_type = self._classify_main_action(query_lower)
        
        # Étape 2: Extraire les colonnes mentionnées
        columns = self._extract_columns(query_lower, dataframe)
        
        # Étape 3: Déterminer les paramètres spécifiques
        if action_type == 'summary':
            return self._handle_summary_request(query_lower, dataframe, columns)
        elif action_type == 'visualization':
            return self._handle_visualization_request(query_lower, dataframe, columns)
        elif action_type == 'analysis':
            return self._handle_analysis_request(query_lower, dataframe, columns)
        else:
            return {
                'action': 'error',
                'message': self.responses['error'],
                'success': False
            }
    
    def _classify_main_action(self, query: str) -> str:
        """Classifie l'action principale de la requête."""
        scores = {}
        
        for action_type, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                scores[action_type] = score
        
        if not scores:
            return 'unknown'
        
        # Retourner l'action avec le score le plus élevé
        return max(scores, key=scores.get)
    
    def _extract_columns(self, query: str, dataframe: pd.DataFrame) -> List[str]:
        """Extrait les noms de colonnes mentionnés dans la requête."""
        found_columns = []
        
        for col in dataframe.columns:
            col_lower = col.lower()
            # Recherche exacte et partielle
            if col_lower in query or any(word in col_lower for word in query.split()):
                found_columns.append(col)
        
        return found_columns
    
    def _handle_summary_request(self, query: str, dataframe: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Traite une demande de résumé."""
        return {
            'action': 'summary',
            'message': self.responses['summary'],
            'parameters': {
                'type': 'summary',
                'columns': columns if columns else list(dataframe.columns),
                'include_stats': True,
                'include_info': True
            },
            'success': True
        }
    
    def _handle_visualization_request(self, query: str, dataframe: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Traite une demande de visualisation."""
        # Déterminer le type de graphique
        viz_type = self._determine_viz_type(query, dataframe, columns)
        
        # Sélectionner les colonnes appropriées
        selected_columns = self._select_viz_columns(viz_type, dataframe, columns)
        
        return {
            'action': 'visualization',
            'message': self.responses.get(viz_type, "Je vais créer une visualisation."),
            'parameters': {
                'viz_type': viz_type,
                'columns': selected_columns,
                'title': self._generate_title(viz_type, selected_columns)
            },
            'success': True
        }
    
    def _determine_viz_type(self, query: str, dataframe: pd.DataFrame, columns: List[str]) -> str:
        """Détermine le type de visualisation le plus approprié."""
        # Règles basées sur les mots-clés
        if any(word in query for word in ['histogram', 'histogramme', 'distribution']):
            return 'histogram'
        elif any(word in query for word in ['scatter', 'nuage', 'relation']):
            return 'scatter'
        elif any(word in query for word in ['barres', 'bar', 'catégorie']):
            return 'bar_chart'
        elif any(word in query for word in ['ligne', 'line', 'évolution', 'temps']):
            return 'line_chart'
        elif any(word in query for word in ['heatmap', 'corrélation', 'correlation']):
            return 'heatmap'
        elif any(word in query for word in ['boxplot', 'boîte']):
            return 'boxplot'
        
        # Règles basées sur les types de données
        if columns:
            numeric_cols = [col for col in columns if dataframe[col].dtype in ['float64', 'int64']]
            categorical_cols = [col for col in columns if dataframe[col].dtype == 'object']
            
            if len(numeric_cols) >= 2:
                return 'scatter'
            elif len(numeric_cols) == 1 and len(categorical_cols) >= 1:
                return 'bar_chart'
            elif len(numeric_cols) == 1:
                return 'histogram'
            elif len(categorical_cols) >= 1:
                return 'bar_chart'
        
        # Défaut basé sur la structure des données
        numeric_columns = dataframe.select_dtypes(include=['number']).columns
        if len(numeric_columns) >= 2:
            return 'heatmap'
        elif len(numeric_columns) == 1:
            return 'histogram'
        else:
            return 'bar_chart'
    
    def _select_viz_columns(self, viz_type: str, dataframe: pd.DataFrame, mentioned_columns: List[str]) -> Dict[str, str]:
        """Sélectionne les colonnes appropriées pour la visualisation."""
        numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = dataframe.select_dtypes(include=['object', 'category']).columns.tolist()
        
        result = {}
        
        if viz_type == 'histogram':
            if mentioned_columns:
                num_mentioned = [col for col in mentioned_columns if col in numeric_cols]
                result['x'] = num_mentioned[0] if num_mentioned else numeric_cols[0] if numeric_cols else None
            else:
                result['x'] = numeric_cols[0] if numeric_cols else None
                
        elif viz_type == 'scatter':
            if len(mentioned_columns) >= 2:
                num_mentioned = [col for col in mentioned_columns if col in numeric_cols]
                if len(num_mentioned) >= 2:
                    result['x'] = num_mentioned[0]
                    result['y'] = num_mentioned[1]
                else:
                    result['x'] = numeric_cols[0] if len(numeric_cols) > 0 else None
                    result['y'] = numeric_cols[1] if len(numeric_cols) > 1 else None
            else:
                result['x'] = numeric_cols[0] if len(numeric_cols) > 0 else None
                result['y'] = numeric_cols[1] if len(numeric_cols) > 1 else None
                
        elif viz_type == 'bar_chart':
            if mentioned_columns:
                cat_mentioned = [col for col in mentioned_columns if col in categorical_cols]
                num_mentioned = [col for col in mentioned_columns if col in numeric_cols]
                result['x'] = cat_mentioned[0] if cat_mentioned else categorical_cols[0] if categorical_cols else None
                result['y'] = num_mentioned[0] if num_mentioned else numeric_cols[0] if numeric_cols else None
            else:
                result['x'] = categorical_cols[0] if categorical_cols else None
                result['y'] = numeric_cols[0] if numeric_cols else None
                
        elif viz_type == 'line_chart':
            # Recherche de colonnes de date/temps
            date_cols = []
            for col in dataframe.columns:
                if 'date' in col.lower() or 'time' in col.lower() or 'temps' in col.lower():
                    date_cols.append(col)
            
            result['x'] = date_cols[0] if date_cols else (mentioned_columns[0] if mentioned_columns else dataframe.columns[0])
            num_mentioned = [col for col in mentioned_columns if col in numeric_cols] if mentioned_columns else numeric_cols
            result['y'] = num_mentioned[0] if num_mentioned else numeric_cols[0] if numeric_cols else None
            
        elif viz_type == 'heatmap':
            result['columns'] = mentioned_columns if mentioned_columns else numeric_cols[:10]  # Limiter à 10 colonnes
            
        elif viz_type == 'boxplot':
            if mentioned_columns:
                num_mentioned = [col for col in mentioned_columns if col in numeric_cols]
                result['y'] = num_mentioned[0] if num_mentioned else numeric_cols[0] if numeric_cols else None
            else:
                result['y'] = numeric_cols[0] if numeric_cols else None
        
        return result
    
    def _generate_title(self, viz_type: str, columns: Dict[str, str]) -> str:
        """Génère un titre approprié pour la visualisation."""
        titles = {
            'histogram': f"Distribution de {columns.get('x', 'données')}",
            'scatter': f"Relation entre {columns.get('x', 'X')} et {columns.get('y', 'Y')}",
            'bar_chart': f"{columns.get('y', 'Valeurs')} par {columns.get('x', 'Catégorie')}",
            'line_chart': f"Évolution de {columns.get('y', 'valeurs')} dans le temps",
            'heatmap': "Matrice de corrélation",
            'boxplot': f"Distribution de {columns.get('y', 'données')}"
        }
        
        return titles.get(viz_type, "Visualisation des données")
    
    def _handle_analysis_request(self, query: str, dataframe: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Traite une demande d'analyse."""
        analysis_type = self._determine_analysis_type(query)
        
        return {
            'action': 'analysis',
            'message': self.responses['analysis'],
            'parameters': {
                'analysis_type': analysis_type,
                'columns': columns if columns else list(dataframe.columns),
                'query': query
            },
            'success': True
        }
    
    def _determine_analysis_type(self, query: str) -> str:
        """Détermine le type d'analyse demandé."""
        if any(word in query for word in ['moyenne', 'mean', 'avg']):
            return 'mean'
        elif any(word in query for word in ['médiane', 'median']):
            return 'median'
        elif any(word in query for word in ['maximum', 'max']):
            return 'max'
        elif any(word in query for word in ['minimum', 'min']):
            return 'min'
        elif any(word in query for word in ['somme', 'sum', 'total']):
            return 'sum'
        elif any(word in query for word in ['count', 'nombre', 'combien']):
            return 'count'
        else:
            return 'describe'
    
    def get_help_message(self) -> str:
        """Retourne un message d'aide avec les types de requêtes supportées."""
        return """
        🤖 **Types de requêtes supportées :**
        
        📊 **Résumés et statistiques :**
        - "Montre-moi un résumé des données"
        - "Quelles sont les statistiques de base ?"
        
        📈 **Visualisations :**
        - "Crée un histogramme de [colonne]"
        - "Montre un graphique en barres de [colonne]"
        - "Fais un scatter plot de [col1] et [col2]"
        - "Affiche une heatmap de corrélation"
        
        🔍 **Analyses :**
        - "Quelle est la moyenne de [colonne] ?"
        - "Calcule la somme totale de [colonne]"
        - "Trouve le maximum de [colonne]"
        
        💡 **Astuce :** Mentionnez les noms des colonnes dans vos questions !
        """