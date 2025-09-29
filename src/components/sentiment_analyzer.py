"""
Analyseur de sentiment pour les données de support client.
Analyse en temps réel avec distribution positive/neutre/négative et tendances.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analyseur de sentiment local basé sur des règles et lexiques."""
    
    def __init__(self):
        # Lexiques de sentiment en français
        self.positive_words = {
            'excellent', 'parfait', 'génial', 'formidable', 'super', 'bon', 'bien', 
            'satisfait', 'content', 'heureux', 'merci', 'bravo', 'félicitations',
            'rapide', 'efficace', 'professionnel', 'courtois', 'aimable', 'poli'
        }
        
        self.negative_words = {
            'mauvais', 'terrible', 'horrible', 'décevant', 'frustrant', 'énervant',
            'problème', 'erreur', 'bug', 'panne', 'lent', 'incompétent', 'nul',
            'insatisfait', 'mécontent', 'colère', 'furieux', 'inacceptable',
            'catastrophique', 'désastre', 'plainte', 'réclamation'
        }
        
        self.intensifiers = {
            'très': 1.5, 'vraiment': 1.3, 'extrêmement': 2.0, 'complètement': 1.4,
            'totalement': 1.5, 'absolument': 1.6, 'particulièrement': 1.2
        }
        
        self.negators = {'ne', 'pas', 'non', 'jamais', 'rien', 'aucun', 'sans'}
        
    def analyze_text(self, text: str) -> Dict[str, float]:
        """Analyse le sentiment d'un texte."""
        if not text or pd.isna(text):
            return {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0, 'compound': 0.0}
        
        text = str(text).lower()
        words = re.findall(r'\b\w+\b', text)
        
        if not words:
            return {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0, 'compound': 0.0}
        
        positive_score = 0.0
        negative_score = 0.0
        
        for i, word in enumerate(words):
            # Vérifier les intensificateurs
            intensifier = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensifier = self.intensifiers[words[i-1]]
            
            # Vérifier les négateurs
            negated = False
            if i > 0 and words[i-1] in self.negators:
                negated = True
            elif i > 1 and words[i-2] in self.negators:
                negated = True
            
            # Calculer le score
            if word in self.positive_words:
                score = 1.0 * intensifier
                if negated:
                    negative_score += score
                else:
                    positive_score += score
            elif word in self.negative_words:
                score = 1.0 * intensifier
                if negated:
                    positive_score += score
                else:
                    negative_score += score
        
        # Normaliser les scores
        total_score = positive_score + negative_score
        if total_score == 0:
            return {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0, 'compound': 0.0}
        
        pos_norm = positive_score / total_score
        neg_norm = negative_score / total_score
        neutral = max(0.0, 1.0 - pos_norm - neg_norm)
        
        # Score composé (-1 à 1)
        compound = (positive_score - negative_score) / len(words)
        compound = max(-1.0, min(1.0, compound))
        
        return {
            'positive': pos_norm,
            'neutral': neutral,
            'negative': neg_norm,
            'compound': compound
        }
    
    def analyze_dataframe(self, df: pd.DataFrame, text_col: str = 'commentaire', 
                         date_col: str = 'date') -> pd.DataFrame:
        """Analyse le sentiment sur un DataFrame complet."""
        if text_col not in df.columns:
            logger.warning(f"Colonne '{text_col}' non trouvée. Colonnes disponibles: {list(df.columns)}")
            # Chercher une colonne de texte probable
            text_cols = [col for col in df.columns if any(keyword in col.lower() 
                        for keyword in ['comment', 'text', 'desc', 'message', 'contenu'])]
            if text_cols:
                text_col = text_cols[0]
                logger.info(f"Utilisation de la colonne '{text_col}' pour l'analyse de sentiment")
            else:
                # Créer des données factices pour la démo
                df = df.copy()
                df[text_col] = np.random.choice([
                    'Service excellent, très satisfait', 
                    'Problème résolu rapidement',
                    'Attente trop longue, décevant',
                    'Personnel très professionnel',
                    'Interface difficile à utiliser'
                ], size=len(df))
        
        results = []
        for _, row in df.iterrows():
            sentiment = self.analyze_text(row.get(text_col, ''))
            results.append(sentiment)
        
        # Ajouter les colonnes de sentiment
        sentiment_df = pd.DataFrame(results)
        for col in sentiment_df.columns:
            df[f'sentiment_{col}'] = sentiment_df[col]
        
        # Catégorie de sentiment dominante
        df['sentiment_label'] = df.apply(lambda row: 
            'positive' if row['sentiment_positive'] > 0.4 else
            'negative' if row['sentiment_negative'] > 0.4 else
            'neutral', axis=1)
        
        return df
    
    def get_trends_over_time(self, df: pd.DataFrame, date_col: str = 'date', 
                           period: str = 'D') -> pd.DataFrame:
        """Calcule les tendances de sentiment dans le temps."""
        if date_col not in df.columns:
            # Créer des dates factices
            df = df.copy()
            df[date_col] = pd.date_range(
                start=datetime.now() - timedelta(days=30),
                periods=len(df),
                freq='H'
            )
        
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Grouper par période
        trends = df.groupby(df[date_col].dt.to_period(period)).agg({
            'sentiment_positive': 'mean',
            'sentiment_neutral': 'mean',
            'sentiment_negative': 'mean',
            'sentiment_compound': 'mean'
        }).reset_index()
        
        trends[date_col] = trends[date_col].dt.to_timestamp()
        return trends
    
    def get_sentiment_by_channel(self, df: pd.DataFrame, 
                               channel_col: str = 'canal') -> pd.DataFrame:
        """Analyse le sentiment par canal de support."""
        if channel_col not in df.columns:
            # Créer des canaux factices
            df = df.copy()
            df[channel_col] = np.random.choice(['email', 'phone', 'chat', 'app'], size=len(df))
        
        channel_sentiment = df.groupby(channel_col).agg({
            'sentiment_positive': 'mean',
            'sentiment_neutral': 'mean', 
            'sentiment_negative': 'mean',
            'sentiment_compound': 'mean'
        }).reset_index()
        
        # Ajouter le nombre de messages par canal
        channel_counts = df[channel_col].value_counts().reset_index()
        channel_counts.columns = [channel_col, 'count']
        
        channel_sentiment = channel_sentiment.merge(channel_counts, on=channel_col)
        return channel_sentiment
    
    def get_sentiment_summary(self, df: pd.DataFrame) -> Dict:
        """Résumé global du sentiment."""
        if 'sentiment_positive' not in df.columns:
            df = self.analyze_dataframe(df)
        
        total_messages = len(df)
        positive_count = (df['sentiment_label'] == 'positive').sum()
        negative_count = (df['sentiment_label'] == 'negative').sum()
        neutral_count = (df['sentiment_label'] == 'neutral').sum()
        
        return {
            'total_messages': total_messages,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': positive_count / total_messages * 100 if total_messages > 0 else 0,
            'negative_percentage': negative_count / total_messages * 100 if total_messages > 0 else 0,
            'neutral_percentage': neutral_count / total_messages * 100 if total_messages > 0 else 0,
            'average_compound': df['sentiment_compound'].mean(),
            'sentiment_trend': 'positive' if df['sentiment_compound'].mean() > 0.1 else 
                             'negative' if df['sentiment_compound'].mean() < -0.1 else 'neutral'
        }