"""
Composant de heatmap géographique pour l'analyse des performances par région.
Carte interactive avec fonctionnalités de recherche, sélection de période et filtrage par domaine.
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, Search, MarkerCluster
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GeographicHeatmap:
    """Générateur de heatmap géographique pour les performances d'agences."""
    
    def __init__(self):
        self.default_center = [46.2276, 2.2137]  # Centre de la France
        self.default_zoom = 6
        
    def create_sample_geographic_data(self, n_agencies: int = 50) -> pd.DataFrame:
        """Crée des données géographiques d'exemple pour les agences."""
        # Use modern NumPy random generator with seed for reproducibility
        rng = np.random.default_rng(42)
        
        # Coordonnées approximatives de grandes villes françaises
        cities = [
            ("Paris", 48.8566, 2.3522),
            ("Lyon", 45.7640, 4.8357),
            ("Marseille", 43.2965, 5.3698),
            ("Toulouse", 43.6047, 1.4442),
            ("Nice", 43.7102, 7.2620),
            ("Nantes", 47.2184, -1.5536),
            ("Montpellier", 43.6110, 3.8767),
            ("Strasbourg", 48.5734, 7.7521),
            ("Bordeaux", 44.8378, -0.5792),
            ("Lille", 50.6292, 3.0573),
            ("Rennes", 48.1173, -1.6778),
            ("Reims", 49.2583, 4.0317),
            ("Toulon", 43.1242, 5.9280),
            ("Saint-Étienne", 45.4397, 4.3872),
            ("Le Havre", 49.4944, 0.1079),
            ("Grenoble", 45.1885, 5.7245),
            ("Dijon", 47.3220, 5.0415),
            ("Angers", 47.4784, -0.5632),
            ("Nîmes", 43.8367, 4.3601),
            ("Villeurbanne", 45.7772, 4.8814)
        ]
        
        agencies = []
        for i in range(n_agencies):
            # Choisir une ville de base
            base_city = cities[i % len(cities)]
            city_name, base_lat, base_lon = base_city
            
            # Ajouter une variation aléatoire autour de la ville
            lat_offset = rng.normal(0, 0.1)
            lon_offset = rng.normal(0, 0.1)
            
            # Métriques de performance
            base_performance = rng.uniform(0.6, 0.95)
            satisfaction = rng.normal(4.2, 0.6)
            satisfaction = np.clip(satisfaction, 1, 5)
            
            response_time = rng.exponential(120)  # minutes
            resolution_rate = rng.beta(8, 2)  # Biaisé vers des valeurs élevées
            
            # Domaines d'activité
            domains = ['crédit', 'compte', 'carte', 'assurance', 'épargne']
            domain = rng.choice(domains)
            
            # Région
            if base_lat > 48.5:
                region = "Nord"
            elif base_lat < 44:
                region = "Sud"
            else:
                region = "Centre"
            
            agency = {
                'agency_id': f'AG_{i+1:03d}',
                'name': f'Agence {city_name} {i//len(cities) + 1}',
                'latitude': base_lat + lat_offset,
                'longitude': base_lon + lon_offset,
                'city': city_name,
                'region': region,
                'domain': domain,
                'performance_score': base_performance,
                'satisfaction_score': satisfaction,
                'response_time': response_time,
                'resolution_rate': resolution_rate,
                'ticket_count': rng.poisson(100),
                'staff_count': rng.integers(5, 25),  # Note: randint -> integers
                'last_updated': datetime.now() - timedelta(hours=float(rng.integers(0, 24)))
            }
            
            agencies.append(agency)
        
        return pd.DataFrame(agencies)
    
    def _filter_dataframe(self, df: pd.DataFrame, region_filter: Optional[str] = None,
                         domain_filter: Optional[str] = None,
                         date_range: Optional[Tuple[datetime, datetime]] = None) -> pd.DataFrame:
        """Applique les filtres au DataFrame."""
        filtered_df = df.copy()
        
        if region_filter and 'region' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['region'] == region_filter]
        
        if domain_filter and 'domain' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['domain'] == domain_filter]
        
        if date_range and 'last_updated' in filtered_df.columns:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (pd.to_datetime(filtered_df['last_updated']) >= start_date) &
                (pd.to_datetime(filtered_df['last_updated']) <= end_date)
            ]
        
        return filtered_df
    
    def _create_base_map(self, filtered_df: pd.DataFrame, lat_col: str, lon_col: str) -> folium.Map:
        """Crée la carte de base avec les tuiles."""
        if filtered_df.empty:
            return folium.Map(location=self.default_center, zoom_start=self.default_zoom)
        
        center_lat = filtered_df[lat_col].mean()
        center_lon = filtered_df[lon_col].mean()
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap'
        )
        
        folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
        folium.TileLayer('cartodbdark_matter', name='CartoDB Dark').add_to(m)
        
        return m
    
    def _prepare_heatmap_data(self, filtered_df: pd.DataFrame, metric_col: str,
                             lat_col: str, lon_col: str, name_col: str) -> Tuple[List, List]:
        """Prépare les données pour la heatmap et les markers."""
        heat_data = []
        markers = []
        
        metric_values = filtered_df[metric_col]
        min_val, max_val = metric_values.min(), metric_values.max()
        
        for _, row in filtered_df.iterrows():
            lat = float(row[lat_col])
            lon = float(row[lon_col])
            metric_val = float(row[metric_col])
            
            # Intensité pour la heatmap (0-1)
            intensity = (metric_val - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            heat_data.append([lat, lon, intensity])
            
            # Données pour les markers
            marker_data = {
                'lat': lat,
                'lon': lon,
                'name': str(row.get(name_col, f'Agence {len(markers)+1}')),
                'metric_value': metric_val,
                'popup_info': self._extract_popup_info(row)
            }
            markers.append(marker_data)
        
        return heat_data, markers
    
    def _extract_popup_info(self, row: pd.Series) -> Dict:
        """Extrait les informations pour le popup."""
        popup_info = {}
        popup_cols = ['region', 'domain', 'satisfaction_score', 'response_time', 'resolution_rate']
        
        for col in popup_cols:
            if col in row:
                popup_info[col] = row[col]
        
        return popup_info
    
    def _get_marker_style(self, metric_value: float) -> Tuple[str, str]:
        """Détermine la couleur et l'icône du marker selon la performance."""
        if metric_value >= 0.8:
            return 'green', 'ok-sign'
        elif metric_value >= 0.6:
            return 'orange', 'warning-sign'
        else:
            return 'red', 'remove-sign'
    
    def _create_popup_content(self, marker: Dict, metric_col: str) -> str:
        """Crée le contenu HTML du popup."""
        popup_content = f"<b>{marker['name']}</b><br/>"
        popup_content += f"{metric_col}: {marker['metric_value']:.2f}<br/>"
        
        for key, value in marker['popup_info'].items():
            if key == 'satisfaction_score':
                popup_content += f"Satisfaction: {value:.1f}/5<br/>"
            elif key == 'response_time':
                popup_content += f"Temps de réponse: {value:.0f} min<br/>"
            elif key == 'resolution_rate':
                popup_content += f"Taux résolution: {value:.1%}<br/>"
            else:
                popup_content += f"{key}: {value}<br/>"
        
        return popup_content
    
    def _add_heatmap_layer(self, m: folium.Map, heat_data: List) -> None:
        """Ajoute la couche heatmap à la carte."""
        if heat_data:
            HeatMap(
                heat_data,
                name='Heatmap Performance',
                min_opacity=0.3,
                max_zoom=18,
                radius=15,
                blur=10,
                gradient={0.0: 'red', 0.5: 'orange', 1.0: 'green'}
            ).add_to(m)
    
    def _add_markers(self, m: folium.Map, markers: List, metric_col: str) -> None:
        """Ajoute les markers avec clustering à la carte."""
        marker_cluster = MarkerCluster(name='Agences').add_to(m)
        
        for marker in markers:
            color, icon = self._get_marker_style(marker['metric_value'])
            popup_content = self._create_popup_content(marker, metric_col)
            
            folium.Marker(
                location=[marker['lat'], marker['lon']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=marker['name'],
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(marker_cluster)
    
    def _add_search_functionality(self, m: folium.Map, markers: List) -> None:
        """Ajoute la fonctionnalité de recherche à la carte."""
        if not markers:
            return
        
        geojson_features = []
        for marker in markers:
            feature = {
                "type": "Feature",
                "properties": {
                    "name": marker['name'],
                    "performance": marker['metric_value']
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [marker['lon'], marker['lat']]
                }
            }
            geojson_features.append(feature)
        
        geojson_data = {
            "type": "FeatureCollection",
            "features": geojson_features
        }
        
        search_layer = folium.GeoJson(
            geojson_data,
            name="Recherche",
            show=False
        ).add_to(m)
        
        Search(
            layer=search_layer,
            search_label="name",
            placeholder="Rechercher une agence...",
            collapsed=False,
            position="topleft"
        ).add_to(m)
    
    def _add_legend(self, m: folium.Map, metric_col: str) -> None:
        """Ajoute la légende à la carte."""
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Légende - {metric_col}</b></p>
        <p><i class="fa fa-circle" style="color:green"></i> Excellente (≥0.8)</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Correcte (0.6-0.8)</p>
        <p><i class="fa fa-circle" style="color:red"></i> Faible (<0.6)</p>
        </div>
        '''
        
        try:
            legend_element = folium.Element(legend_html)
            m.get_root().add_child(legend_element)
        except Exception:
            logger.warning("Could not add legend to map - Folium version compatibility issue")
    
    def create_performance_heatmap(self, df: pd.DataFrame,
                                 metric_col: str = 'performance_score',
                                 lat_col: str = 'latitude',
                                 lon_col: str = 'longitude',
                                 name_col: str = 'name',
                                 region_filter: Optional[str] = None,
                                 domain_filter: Optional[str] = None,
                                 date_range: Optional[Tuple[datetime, datetime]] = None) -> folium.Map:
        """Crée une heatmap des performances par agence."""
        
        # Créer des données d'exemple si nécessaire
        if df.empty or not all(col in df.columns for col in [lat_col, lon_col]):
            df = self.create_sample_geographic_data()
        
        # Appliquer les filtres
        filtered_df = self._filter_dataframe(df, region_filter, domain_filter, date_range)
        
        # Créer la carte de base
        m = self._create_base_map(filtered_df, lat_col, lon_col)
        
        if filtered_df.empty:
            return m
        
        # Préparer les données
        heat_data, markers = self._prepare_heatmap_data(filtered_df, metric_col, lat_col, lon_col, name_col)
        
        # Ajouter les couches à la carte
        self._add_heatmap_layer(m, heat_data)
        self._add_markers(m, markers, metric_col)
        self._add_search_functionality(m, markers)
        self._add_legend(m, metric_col)
        
        # Contrôles de couches
        folium.LayerControl().add_to(m)
        
        return m
    
    def get_regional_statistics(self, df: pd.DataFrame) -> Dict:
        """Calcule les statistiques par région."""
        
        if df.empty or 'region' not in df.columns:
            df = self.create_sample_geographic_data()
        
        stats = {}
        
        for region in df['region'].unique():
            region_data = df[df['region'] == region]
            
            stats[region] = {
                'agency_count': len(region_data),
                'avg_performance': region_data.get('performance_score', pd.Series([0])).mean(),
                'avg_satisfaction': region_data.get('satisfaction_score', pd.Series([0])).mean(),
                'avg_response_time': region_data.get('response_time', pd.Series([0])).mean(),
                'avg_resolution_rate': region_data.get('resolution_rate', pd.Series([0])).mean(),
                'total_tickets': region_data.get('ticket_count', pd.Series([0])).sum(),
                'top_performing_agency': region_data.loc[
                    region_data.get('performance_score', pd.Series([0])).idxmax()
                ].get('name', 'N/A') if not region_data.empty else 'N/A'
            }
        
        return stats
    
    def export_map_data(self, df: pd.DataFrame, 
                       output_format: str = 'geojson') -> Dict:
        """Exporte les données de la carte dans différents formats."""
        
        if df.empty:
            df = self.create_sample_geographic_data()
        
        if output_format.lower() == 'geojson':
            features = []
            
            for _, row in df.iterrows():
                feature = {
                    "type": "Feature",
                    "properties": {
                        key: (value.isoformat() if isinstance(value, datetime) else 
                             float(value) if isinstance(value, (int, float, np.number)) else str(value))
                        for key, value in row.items() 
                        if key not in ['latitude', 'longitude']
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(row['longitude']), float(row['latitude'])]
                    }
                }
                features.append(feature)
            
            return {
                "type": "FeatureCollection",
                "features": features
            }
        
        elif output_format.lower() == 'csv':
            return {"csv_data": df.to_dict('records')}
        
        else:
            return {"error": f"Format non supporté: {output_format}"}
    
    def generate_performance_insights(self, df: pd.DataFrame) -> List[Dict]:
        """Génère des insights sur les performances géographiques."""
        
        if df.empty:
            df = self.create_sample_geographic_data()
        
        insights = []
        
        # Analyse par région
        regional_stats = self.get_regional_statistics(df)
        
        best_region = max(regional_stats.keys(), 
                         key=lambda x: regional_stats[x]['avg_performance'])
        worst_region = min(regional_stats.keys(), 
                          key=lambda x: regional_stats[x]['avg_performance'])
        
        insights.append({
            'type': 'regional_performance',
            'title': 'Performance par région',
            'message': f'Meilleure région: {best_region} ({regional_stats[best_region]["avg_performance"]:.2f})',
            'recommendation': f'Appliquer les bonnes pratiques de {best_region} à {worst_region}'
        })
        
        # Analyse des corrélations géographiques
        if 'ticket_count' in df.columns and 'satisfaction_score' in df.columns:
            correlation = df['ticket_count'].corr(df['satisfaction_score'])
            
            if correlation < -0.3:
                insights.append({
                    'type': 'correlation',
                    'title': 'Corrélation volume-satisfaction',
                    'message': f'Corrélation négative forte ({correlation:.2f})',
                    'recommendation': 'Les agences à fort volume ont une satisfaction plus faible'
                })
        
        # Détection d'agences sous-performantes
        if 'performance_score' in df.columns:
            low_performers = df[df['performance_score'] < 0.6]
            
            if len(low_performers) > 0:
                insights.append({
                    'type': 'underperformance',
                    'title': 'Agences sous-performantes',
                    'message': f'{len(low_performers)} agences avec score < 0.6',
                    'recommendation': 'Actions correctives prioritaires requises',
                    'affected_agencies': low_performers['name'].tolist()[:5]  # Top 5
                })
        
        return insights