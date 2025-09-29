"""
Détecteur d'anomalies pour identifier les patterns inhabituels dans les données.
Détection automatique avec alertes, visualisation chronologique et reconnaissance de patterns.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Détecteur d'anomalies avec multiple algorithmes."""
    
    def __init__(self, sensitivity: float = 0.1):
        """
        Initialise le détecteur d'anomalies.
        
        Args:
            sensitivity: Sensibilité de détection (0.1 = 10% des données comme anomalies)
        """
        self.sensitivity = sensitivity
        self.scaler = StandardScaler()
        self.detection_methods = {
            'isolation_forest': self._detect_isolation_forest,
            'statistical': self._detect_statistical,
            'clustering': self._detect_clustering,
            'time_series': self._detect_time_series
        }
        
    def detect_anomalies(self, df: pd.DataFrame, 
                        methods: List[str] = None,
                        numerical_cols: List[str] = None) -> pd.DataFrame:
        """Détecte les anomalies avec plusieurs méthodes."""
        if methods is None:
            methods = ['isolation_forest', 'statistical']
        
        if numerical_cols is None:
            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numerical_cols:
            # Créer des colonnes numériques factices pour la démo
            df = df.copy()
            df['response_time'] = np.random.exponential(2, len(df))
            df['satisfaction_score'] = np.random.normal(4, 0.8, len(df))
            df['ticket_priority'] = np.random.randint(1, 6, len(df))
            numerical_cols = ['response_time', 'satisfaction_score', 'ticket_priority']
        
        results_df = df.copy()
        
        # Appliquer chaque méthode de détection
        for method in methods:
            if method in self.detection_methods:
                anomaly_scores = self.detection_methods[method](df[numerical_cols])
                results_df[f'anomaly_{method}'] = anomaly_scores
        
        # Score composite (moyenne des méthodes)
        anomaly_cols = [col for col in results_df.columns if col.startswith('anomaly_')]
        if anomaly_cols:
            results_df['anomaly_score'] = results_df[anomaly_cols].mean(axis=1)
            results_df['is_anomaly'] = results_df['anomaly_score'] > 0.5
        
        return results_df
    
    def _detect_isolation_forest(self, data: pd.DataFrame) -> np.ndarray:
        """Détection par Isolation Forest."""
        try:
            model = IsolationForest(contamination=self.sensitivity, random_state=42)
            predictions = model.fit_predict(data.fillna(data.mean()))
            # Convertir -1/1 en 0/1 (0=normal, 1=anomalie)
            return (predictions == -1).astype(int)
        except Exception as e:
            logger.warning(f"Erreur Isolation Forest: {e}")
            return np.zeros(len(data))
    
    def _detect_statistical(self, data: pd.DataFrame) -> np.ndarray:
        """Détection statistique par Z-score."""
        try:
            z_scores = np.abs(stats.zscore(data.fillna(data.mean()), axis=0, nan_policy='omit'))
            # Point anormal si Z-score > 3 pour au moins une variable
            threshold = 3
            anomalies = (z_scores > threshold).any(axis=1).astype(int)
            return anomalies
        except Exception as e:
            logger.warning(f"Erreur détection statistique: {e}")
            return np.zeros(len(data))
    
    def _detect_clustering(self, data: pd.DataFrame) -> np.ndarray:
        """Détection par clustering DBSCAN."""
        try:
            # Normaliser les données
            scaled_data = self.scaler.fit_transform(data.fillna(data.mean()))
            
            # DBSCAN pour identifier les points isolés
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            clusters = dbscan.fit_predict(scaled_data)
            
            # Points avec cluster -1 sont considérés comme anomalies
            return (clusters == -1).astype(int)
        except Exception as e:
            logger.warning(f"Erreur clustering: {e}")
            return np.zeros(len(data))
    
    def _detect_time_series(self, data: pd.DataFrame) -> np.ndarray:
        """Détection d'anomalies temporelles."""
        try:
            anomalies = np.zeros(len(data))
            
            for col in data.columns:
                if data[col].dtype in [np.float64, np.int64]:
                    series = data[col].fillna(data[col].mean())
                    
                    # Détection par écart mobile
                    window = min(10, len(series) // 4)
                    if window < 2:
                        continue
                    
                    rolling_mean = series.rolling(window=window, center=True).mean()
                    rolling_std = series.rolling(window=window, center=True).std()
                    
                    # Points au-delà de 2 écarts-types
                    threshold = 2
                    col_anomalies = np.abs(series - rolling_mean) > (threshold * rolling_std)
                    anomalies = np.maximum(anomalies, col_anomalies.fillna(0).astype(int))
            
            return anomalies
        except Exception as e:
            logger.warning(f"Erreur time series: {e}")
            return np.zeros(len(data))
    
    def get_anomaly_summary(self, df: pd.DataFrame) -> Dict:
        """Résumé des anomalies détectées."""
        if 'is_anomaly' not in df.columns:
            df = self.detect_anomalies(df)
        
        total_points = len(df)
        anomaly_count = df['is_anomaly'].sum()
        anomaly_rate = anomaly_count / total_points * 100 if total_points > 0 else 0
        
        # Statistiques par sévérité
        if 'anomaly_score' in df.columns:
            high_severity = (df['anomaly_score'] > 0.8).sum()
            medium_severity = ((df['anomaly_score'] > 0.5) & (df['anomaly_score'] <= 0.8)).sum()
            low_severity = ((df['anomaly_score'] > 0.3) & (df['anomaly_score'] <= 0.5)).sum()
        else:
            high_severity = medium_severity = low_severity = 0
        
        return {
            'total_points': total_points,
            'anomaly_count': anomaly_count,
            'anomaly_rate': anomaly_rate,
            'high_severity': high_severity,
            'medium_severity': medium_severity,
            'low_severity': low_severity,
            'detection_timestamp': datetime.now()
        }
    
    def get_anomaly_timeline(self, df: pd.DataFrame, 
                           date_col: str = 'date',
                           period: str = 'H') -> pd.DataFrame:
        """Timeline des anomalies."""
        if date_col not in df.columns:
            df = df.copy()
            df[date_col] = pd.date_range(
                start=datetime.now() - timedelta(days=7),
                periods=len(df),
                freq='30min'
            )
        
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Grouper par période
        timeline = df.groupby(df[date_col].dt.to_period(period)).agg({
            'is_anomaly': 'sum',
            'anomaly_score': 'mean'
        }).reset_index()
        
        timeline[date_col] = timeline[date_col].dt.to_timestamp()
        timeline['anomaly_count'] = timeline['is_anomaly']
        
        return timeline
    
    def get_pattern_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyse des patterns d'anomalies."""
        if 'is_anomaly' not in df.columns:
            df = self.detect_anomalies(df)
        
        anomalies = df[df['is_anomaly'] == 1]
        
        if len(anomalies) == 0:
            return {
                'common_patterns': [],
                'peak_hours': [],
                'correlation_insights': []
            }
        
        patterns = []
        
        # Analyse des heures de pic
        if 'date' in df.columns:
            df['hour'] = pd.to_datetime(df['date']).dt.hour
            anomaly_hours = anomalies['hour'].value_counts().head(3)
            peak_hours = [{'hour': int(hour), 'count': int(count)} 
                         for hour, count in anomaly_hours.items()]
        else:
            peak_hours = []
        
        # Patterns communs dans les colonnes numériques
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'anomaly_score' in numerical_cols:
            numerical_cols.remove('anomaly_score')
        
        for col in numerical_cols[:5]:  # Limiter à 5 colonnes
            if col in anomalies.columns:
                col_stats = {
                    'column': col,
                    'mean_normal': df[df['is_anomaly'] == 0][col].mean(),
                    'mean_anomaly': anomalies[col].mean(),
                    'pattern_type': 'high' if anomalies[col].mean() > df[col].mean() else 'low'
                }
                patterns.append(col_stats)
        
        return {
            'common_patterns': patterns,
            'peak_hours': peak_hours,
            'correlation_insights': []
        }
    
    def generate_alerts(self, df: pd.DataFrame, 
                       alert_threshold: float = 0.7) -> List[Dict]:
        """Génère des alertes pour les anomalies critiques."""
        if 'is_anomaly' not in df.columns:
            df = self.detect_anomalies(df)
        
        alerts = []
        
        # Alertes par sévérité
        critical_anomalies = df[df.get('anomaly_score', 0) > alert_threshold]
        
        for _, row in critical_anomalies.head(10).iterrows():  # Limiter à 10 alertes
            severity = 'critical' if row.get('anomaly_score', 0) > 0.9 else 'warning'
            
            alert = {
                'id': f"anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(alerts)}",
                'severity': severity,
                'timestamp': datetime.now(),
                'score': float(row.get('anomaly_score', 0)),
                'description': f"Anomalie détectée avec score {row.get('anomaly_score', 0):.2f}",
                'affected_metrics': []
            }
            
            # Identifier les métriques affectées
            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            for col in numerical_cols:
                if col in row and not col.startswith('anomaly_'):
                    col_mean = df[col].mean()
                    if abs(row[col] - col_mean) > df[col].std() * 2:
                        alert['affected_metrics'].append({
                            'metric': col,
                            'value': float(row[col]),
                            'expected': float(col_mean)
                        })
            
            alerts.append(alert)
        
        return alerts