"""
Dashboard d'analyse avancée avec sentiment, anomalies, prédictions et heatmap géographique.
Interface complète pour l'analyse des performances du support client.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

# Imports des composants d'analyse
from src.components.sentiment_analyzer import SentimentAnalyzer
from src.components.anomaly_detector import AnomalyDetector
from src.components.predictive_analytics import PredictiveAnalytics
from src.components.geographic_heatmap import GeographicHeatmap

class AnalyticsDashboard:
    """Dashboard principal d'analyse avec tous les modules."""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.predictive_analytics = PredictiveAnalytics()
        self.geographic_heatmap = GeographicHeatmap()
        
    def render_dashboard(self, df: pd.DataFrame):
        """Rend le dashboard complet."""
        
        st.title("📊 Dashboard Analytics Avancé")
        st.markdown("Analyse complète des performances du support client avec IA")
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4 = st.tabs([
            "😊 Analyse Sentiment", 
            "🚨 Détection Anomalies", 
            "🔮 Analytics Prédictif", 
            "🗺️ Heatmap Géographique"
        ])
        
        with tab1:
            self.render_sentiment_analysis(df)
        
        with tab2:
            self.render_anomaly_detection(df)
        
        with tab3:
            self.render_predictive_analytics(df)
        
        with tab4:
            self.render_geographic_heatmap(df)
    
    def render_sentiment_analysis(self, df: pd.DataFrame):
        """Onglet analyse de sentiment."""
        st.header("😊 Analyse de Sentiment en Temps Réel")
        
        # Configuration
        col1, col2 = st.columns(2)
        with col1:
            text_column = st.selectbox(
                "Colonne de texte",
                ["commentaire", "description", "message"] + [col for col in df.columns if 'text' in col.lower() or 'comment' in col.lower()],
                index=0
            )
        with col2:
            date_column = st.selectbox(
                "Colonne de date",
                ["date", "timestamp", "created_at"] + [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()],
                index=0
            )
        
        if st.button("🔄 Analyser le Sentiment"):
            with st.spinner("Analyse en cours..."):
                # Analyse du sentiment
                df_sentiment = self.sentiment_analyzer.analyze_dataframe(df, text_column, date_column)
                
                # Résumé global
                summary = self.sentiment_analyzer.get_sentiment_summary(df_sentiment)
                
                # Métriques principales
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Messages Positifs", f"{summary['positive_count']}", 
                             f"{summary['positive_percentage']:.1f}%")
                with col2:
                    st.metric("Messages Neutres", f"{summary['neutral_count']}", 
                             f"{summary['neutral_percentage']:.1f}%")
                with col3:
                    st.metric("Messages Négatifs", f"{summary['negative_count']}", 
                             f"{summary['negative_percentage']:.1f}%")
                with col4:
                    sentiment_trend = "📈" if summary['sentiment_trend'] == 'positive' else "📉" if summary['sentiment_trend'] == 'negative' else "➡️"
                    st.metric("Tendance", sentiment_trend, f"{summary['average_compound']:.2f}")
                
                # Graphique de distribution
                fig_dist = px.pie(
                    values=[summary['positive_count'], summary['neutral_count'], summary['negative_count']],
                    names=['Positif', 'Neutre', 'Négatif'],
                    title="Distribution du Sentiment",
                    color_discrete_map={'Positif': '#2E8B57', 'Neutre': '#FFD700', 'Négatif': '#DC143C'}
                )
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Tendances temporelles
                trends = self.sentiment_analyzer.get_trends_over_time(df_sentiment, date_column)
                
                fig_trends = go.Figure()
                fig_trends.add_trace(go.Scatter(
                    x=trends[date_column], y=trends['sentiment_positive'],
                    mode='lines', name='Positif', line=dict(color='green')
                ))
                fig_trends.add_trace(go.Scatter(
                    x=trends[date_column], y=trends['sentiment_negative'],
                    mode='lines', name='Négatif', line=dict(color='red')
                ))
                fig_trends.add_trace(go.Scatter(
                    x=trends[date_column], y=trends['sentiment_neutral'],
                    mode='lines', name='Neutre', line=dict(color='orange')
                ))
                
                fig_trends.update_layout(
                    title="Évolution du Sentiment dans le Temps",
                    xaxis_title="Date",
                    yaxis_title="Score de Sentiment"
                )
                st.plotly_chart(fig_trends, use_container_width=True)
                
                # Analyse par canal
                channel_sentiment = self.sentiment_analyzer.get_sentiment_by_channel(df_sentiment)
                
                fig_channel = px.bar(
                    channel_sentiment,
                    x='canal' if 'canal' in channel_sentiment.columns else channel_sentiment.columns[0],
                    y=['sentiment_positive', 'sentiment_negative'],
                    title="Sentiment par Canal de Support",
                    barmode='group'
                )
                st.plotly_chart(fig_channel, use_container_width=True)
    
    def render_anomaly_detection(self, df: pd.DataFrame):
        """Onglet détection d'anomalies."""
        st.header("🚨 Détection d'Anomalies Automatique")
        
        # Configuration
        col1, col2 = st.columns(2)
        with col1:
            sensitivity = st.slider("Sensibilité de détection", 0.05, 0.3, 0.1, 0.05)
            self.anomaly_detector.sensitivity = sensitivity
        with col2:
            methods = st.multiselect(
                "Méthodes de détection",
                ['isolation_forest', 'statistical', 'clustering', 'time_series'],
                default=['isolation_forest', 'statistical']
            )
        
        if st.button("🔍 Détecter les Anomalies"):
            with st.spinner("Détection en cours..."):
                # Détection des anomalies
                df_anomalies = self.anomaly_detector.detect_anomalies(df, methods)
                
                # Résumé
                summary = self.anomaly_detector.get_anomaly_summary(df_anomalies)
                
                # Métriques principales
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Anomalies Détectées", summary['anomaly_count'])
                with col2:
                    st.metric("Taux d'Anomalie", f"{summary['anomaly_rate']:.1f}%")
                with col3:
                    st.metric("Sévérité Élevée", summary['high_severity'])
                with col4:
                    st.metric("Dernière Détection", summary['detection_timestamp'].strftime("%H:%M"))
                
                # Alertes critiques
                alerts = self.anomaly_detector.generate_alerts(df_anomalies)
                if alerts:
                    st.subheader("🚨 Alertes Critiques")
                    for alert in alerts[:3]:  # Top 3 alertes
                        severity_color = "🔴" if alert['severity'] == 'critical' else "🟡"
                        with st.expander(f"{severity_color} {alert['description']}"):
                            st.write(f"**Score d'anomalie:** {alert['score']:.2f}")
                            st.write(f"**Timestamp:** {alert['timestamp']}")
                            if alert['affected_metrics']:
                                st.write("**Métriques affectées:**")
                                for metric in alert['affected_metrics'][:3]:
                                    st.write(f"- {metric['metric']}: {metric['value']:.2f} (attendu: {metric['expected']:.2f})")
                
                # Timeline des anomalies
                timeline = self.anomaly_detector.get_anomaly_timeline(df_anomalies)
                
                fig_timeline = go.Figure()
                fig_timeline.add_trace(go.Bar(
                    x=timeline['date'],
                    y=timeline['anomaly_count'],
                    name='Nombre d\'anomalies',
                    marker_color='red'
                ))
                
                fig_timeline.update_layout(
                    title="Timeline des Anomalies",
                    xaxis_title="Date",
                    yaxis_title="Nombre d'Anomalies"
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Analyse des patterns
                patterns = self.anomaly_detector.get_pattern_analysis(df_anomalies)
                
                if patterns['common_patterns']:
                    st.subheader("📊 Patterns Détectés")
                    for pattern in patterns['common_patterns'][:5]:
                        pattern_type = "📈 Élevé" if pattern['pattern_type'] == 'high' else "📉 Faible"
                        st.write(f"**{pattern['column']}**: {pattern_type} - "
                               f"Normal: {pattern['mean_normal']:.2f}, Anomalie: {pattern['mean_anomaly']:.2f}")
                
                # Heures de pic
                if patterns['peak_hours']:
                    fig_hours = px.bar(
                        x=[f"{h['hour']}h" for h in patterns['peak_hours']],
                        y=[h['count'] for h in patterns['peak_hours']],
                        title="Heures de Pic des Anomalies"
                    )
                    st.plotly_chart(fig_hours, use_container_width=True)
    
    def render_predictive_analytics(self, df: pd.DataFrame):
        """Onglet analytics prédictif."""
        st.header("🔮 Analytics Prédictif avec IA")
        
        # Configuration
        col1, col2 = st.columns(2)
        with col1:
            forecast_days = st.slider("Jours de prévision", 1, 30, 7)
        with col2:
            confidence_level = st.selectbox("Niveau de confiance", [0.95, 0.99], format_func=lambda x: f"{x*100:.0f}%")
        
        if st.button("🚀 Générer les Prévisions"):
            with st.spinner("Entraînement des modèles et génération des prévisions..."):
                # Entraînement des modèles
                training_results = self.predictive_analytics.train_forecasting_models(df)
                
                # Performance des modèles
                st.subheader("🎯 Performance des Modèles")
                perf_data = []
                for metric, results in training_results.items():
                    if 'error' not in results:
                        perf_data.append({
                            'Métrique': metric,
                            'MAE Test': f"{results['test_mae']:.2f}",
                            'RMSE Test': f"{results['test_rmse']:.2f}",
                            'Type Modèle': results['model_type']
                        })
                
                if perf_data:
                    st.dataframe(pd.DataFrame(perf_data))
                
                # Génération des prévisions
                forecasts = self.predictive_analytics.generate_forecasts(df, forecast_days, confidence_level)
                
                # Graphiques de prévision
                for metric, forecast_data in forecasts.items():
                    if 'error' not in forecast_data:
                        st.subheader(f"📈 Prévision - {metric}")
                        
                        fig = go.Figure()
                        
                        # Ligne de prévision
                        fig.add_trace(go.Scatter(
                            x=forecast_data['dates'],
                            y=forecast_data['predictions'],
                            mode='lines',
                            name='Prévision',
                            line=dict(color='blue')
                        ))
                        
                        # Intervalle de confiance
                        fig.add_trace(go.Scatter(
                            x=forecast_data['dates'] + forecast_data['dates'][::-1],
                            y=forecast_data['confidence_upper'] + forecast_data['confidence_lower'][::-1],
                            fill='toself',
                            fillcolor='rgba(0,100,80,0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name=f'IC {confidence_level*100:.0f}%'
                        ))
                        
                        fig.update_layout(
                            title=f"Prévision {metric} - {forecast_days} jours",
                            xaxis_title="Date",
                            yaxis_title=metric
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Analyse saisonnière
                seasonal_analysis = self.predictive_analytics.analyze_seasonal_trends(df)
                
                st.subheader("📅 Analyse Saisonnière")
                seasonal_tab1, seasonal_tab2, seasonal_tab3 = st.tabs(["Horaire", "Journalier", "Mensuel"])
                
                with seasonal_tab1:
                    for metric, analysis in seasonal_analysis.items():
                        if analysis and 'hourly_pattern' in analysis:
                            hourly_data = analysis['hourly_pattern']['hourly_values']
                            fig = px.line(
                                x=list(hourly_data.keys()),
                                y=list(hourly_data.values()),
                                title=f"Pattern Horaire - {metric}",
                                labels={'x': 'Heure', 'y': metric}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
                with seasonal_tab2:
                    for metric, analysis in seasonal_analysis.items():
                        if analysis and 'daily_pattern' in analysis:
                            daily_data = analysis['daily_pattern']['daily_values']
                            days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
                            fig = px.bar(
                                x=[days[int(k)] for k in daily_data.keys()],
                                y=list(daily_data.values()),
                                title=f"Pattern Journalier - {metric}",
                                labels={'x': 'Jour', 'y': metric}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
                with seasonal_tab3:
                    for metric, analysis in seasonal_analysis.items():
                        if analysis and 'monthly_pattern' in analysis:
                            monthly_data = analysis['monthly_pattern']['monthly_values']
                            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                                    'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
                            fig = px.bar(
                                x=[months[int(k)-1] for k in monthly_data.keys()],
                                y=list(monthly_data.values()),
                                title=f"Pattern Mensuel - {metric}",
                                labels={'x': 'Mois', 'y': metric}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
                # Insights automatiques
                insights = self.predictive_analytics.generate_insights(df)
                if insights:
                    st.subheader("💡 Insights Automatiques")
                    for insight in insights:
                        icon = {"warning": "⚠️", "critical": "🚨", "positive": "✅", "info": "ℹ️"}
                        st.info(f"{icon.get(insight['type'], '📊')} **{insight['metric']}**: {insight['message']}\n\n"
                               f"💡 Recommandation: {insight['recommendation']}")
    
    def render_geographic_heatmap(self, df: pd.DataFrame):
        """Onglet heatmap géographique."""
        st.header("🗺️ Heatmap Géographique des Performances")
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        # Créer des données d'exemple si nécessaire
        if df.empty or not any(col in df.columns for col in ['latitude', 'longitude']):
            sample_df = self.geographic_heatmap.create_sample_geographic_data()
        else:
            sample_df = df
        
        with col1:
            regions = ['Toutes'] + list(sample_df.get('region', pd.Series()).unique())
            selected_region = st.selectbox("Région", regions)
        
        with col2:
            domains = ['Tous'] + list(sample_df.get('domain', pd.Series()).unique())
            selected_domain = st.selectbox("Domaine", domains)
        
        with col3:
            metrics = ['performance_score', 'satisfaction_score', 'response_time', 'resolution_rate']
            selected_metric = st.selectbox("Métrique", metrics)
        
        # Période de sélection
        col4, col5 = st.columns(2)
        with col4:
            start_date = st.date_input("Date début", datetime.now() - timedelta(days=30))
        with col5:
            end_date = st.date_input("Date fin", datetime.now())
        
        # Génération de la carte
        if st.button("🗺️ Générer la Carte"):
            with st.spinner("Génération de la carte..."):
                # Appliquer les filtres
                region_filter = None if selected_region == 'Toutes' else selected_region
                domain_filter = None if selected_domain == 'Tous' else selected_domain
                date_range = (datetime.combine(start_date, datetime.min.time()), 
                            datetime.combine(end_date, datetime.max.time()))
                
                # Créer la carte
                map_obj = self.geographic_heatmap.create_performance_heatmap(
                    sample_df,
                    metric_col=selected_metric,
                    region_filter=region_filter,
                    domain_filter=domain_filter,
                    date_range=date_range
                )
                
                # Afficher la carte
                try:
                    import streamlit.components.v1 as components
                    map_html = map_obj._repr_html_()
                    components.html(map_html, height=600)
                except Exception as e:
                    st.error(f"Erreur d'affichage de la carte: {e}")
                    st.info("Assurez-vous que folium est installé: pip install folium")
                
                # Export de la carte
                st.download_button(
                    "📥 Télécharger la carte (HTML)",
                    data=map_obj._repr_html_(),
                    file_name=f"heatmap_{selected_metric}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html"
                )
        
        # Statistiques régionales
        st.subheader("📊 Statistiques par Région")
        regional_stats = self.geographic_heatmap.get_regional_statistics(sample_df)
        
        stats_data = []
        for region, stats in regional_stats.items():
            stats_data.append({
                'Région': region,
                'Nb Agences': stats['agency_count'],
                'Performance Moy.': f"{stats['avg_performance']:.2f}",
                'Satisfaction Moy.': f"{stats['avg_satisfaction']:.1f}/5",
                'Temps Réponse Moy.': f"{stats['avg_response_time']:.0f} min",
                'Taux Résolution': f"{stats['avg_resolution_rate']:.1%}",
                'Total Tickets': stats['total_tickets'],
                'Meilleure Agence': stats['top_performing_agency']
            })
        
        st.dataframe(pd.DataFrame(stats_data))
        
        # Insights géographiques
        insights = self.geographic_heatmap.generate_performance_insights(sample_df)
        if insights:
            st.subheader("💡 Insights Géographiques")
            for insight in insights:
                icon_map = {
                    'regional_performance': '🏆',
                    'correlation': '🔗',
                    'underperformance': '⚠️'
                }
                st.info(f"{icon_map.get(insight['type'], '📊')} **{insight['title']}**\n\n"
                       f"{insight['message']}\n\n💡 {insight['recommendation']}")
                
                if 'affected_agencies' in insight:
                    with st.expander("Agences concernées"):
                        for agency in insight['affected_agencies']:
                            st.write(f"• {agency}")
        
        # Export des données
        col1, col2 = st.columns(2)
        with col1:
            geojson_data = self.geographic_heatmap.export_map_data(sample_df, 'geojson')
            st.download_button(
                "📥 Export GeoJSON",
                data=json.dumps(geojson_data, indent=2),
                file_name=f"agencies_data_{datetime.now().strftime('%Y%m%d')}.geojson",
                mime="application/json"
            )
        
        with col2:
            csv_data = sample_df.to_csv(index=False)
            st.download_button(
                "📥 Export CSV",
                data=csv_data,
                file_name=f"agencies_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )