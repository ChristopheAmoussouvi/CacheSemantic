"""
Tests unitaires pour les composants du dashboard analytics.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.components.sentiment_analyzer import SentimentAnalyzer
from src.components.anomaly_detector import AnomalyDetector
from src.components.predictive_analytics import PredictiveAnalytics
from src.components.geographic_heatmap import GeographicHeatmap


class TestAnalyticsComponents(unittest.TestCase):
    """Tests pour les composants d'analyse."""
    
    def setUp(self):
        """Prépare les données de test."""
        self.sample_df = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=100, freq='H'),
            'commentaire': [
                'Service excellent',
                'Très satisfait',
                'Problème frustrant',
                'Aide rapide',
                'Bug terrible'
            ] * 20,
            'satisfaction_score': np.random.normal(4, 0.5, 100),
            'response_time': np.random.exponential(120, 100),
            'ticket_volume': np.random.poisson(50, 100)
        })
        
    def test_sentiment_analyzer(self):
        """Test de l'analyseur de sentiment."""
        analyzer = SentimentAnalyzer()
        
        # Test analyse simple
        result = analyzer.analyze_text("Service excellent, très satisfait")
        self.assertIn('positive', result)
        self.assertIn('negative', result)
        self.assertIn('neutral', result)
        self.assertIn('compound', result)
        
        # Test sur DataFrame
        df_sentiment = analyzer.analyze_dataframe(self.sample_df)
        self.assertIn('sentiment_positive', df_sentiment.columns)
        self.assertIn('sentiment_label', df_sentiment.columns)
        
        # Test résumé
        summary = analyzer.get_sentiment_summary(df_sentiment)
        self.assertIn('total_messages', summary)
        self.assertIn('positive_count', summary)
        
    def test_anomaly_detector(self):
        """Test du détecteur d'anomalies."""
        detector = AnomalyDetector()
        
        # Test détection
        df_anomalies = detector.detect_anomalies(self.sample_df)
        self.assertIn('is_anomaly', df_anomalies.columns)
        self.assertIn('anomaly_score', df_anomalies.columns)
        
        # Test résumé
        summary = detector.get_anomaly_summary(df_anomalies)
        self.assertIn('anomaly_count', summary)
        self.assertIn('anomaly_rate', summary)
        
        # Test alertes
        alerts = detector.generate_alerts(df_anomalies)
        self.assertIsInstance(alerts, list)
        
    def test_predictive_analytics(self):
        """Test de l'analyse prédictive."""
        predictor = PredictiveAnalytics()
        
        # Test entraînement
        results = predictor.train_forecasting_models(self.sample_df)
        self.assertIsInstance(results, dict)
        
        # Test prévisions
        forecasts = predictor.generate_forecasts(self.sample_df, forecast_days=3)
        self.assertIsInstance(forecasts, dict)
        
        # Test analyse saisonnière
        seasonal = predictor.analyze_seasonal_trends(self.sample_df)
        self.assertIsInstance(seasonal, dict)
        
    def test_geographic_heatmap(self):
        """Test de la heatmap géographique."""
        heatmap = GeographicHeatmap()
        
        # Test création de données
        geo_df = heatmap.create_sample_geographic_data(10)
        self.assertEqual(len(geo_df), 10)
        self.assertIn('latitude', geo_df.columns)
        self.assertIn('longitude', geo_df.columns)
        
        # Test statistiques régionales
        stats = heatmap.get_regional_statistics(geo_df)
        self.assertIsInstance(stats, dict)
        
        # Test insights
        insights = heatmap.generate_performance_insights(geo_df)
        self.assertIsInstance(insights, list)
        
        # Test export
        geojson_data = heatmap.export_map_data(geo_df, 'geojson')
        self.assertIn('type', geojson_data)
        self.assertEqual(geojson_data['type'], 'FeatureCollection')


class TestAnalyticsDashboard(unittest.TestCase):
    """Tests pour le dashboard principal."""
    
    def test_dashboard_import(self):
        """Test d'import du dashboard."""
        try:
            from src.components.analytics_dashboard import AnalyticsDashboard
            dashboard = AnalyticsDashboard()
            self.assertIsNotNone(dashboard)
        except ImportError:
            self.skipTest("Dashboard non disponible (dépendances manquantes)")


if __name__ == '__main__':
    # Exécuter les tests
    unittest.main(verbosity=2)