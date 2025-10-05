"""
Module de génération automatique de visualisations basées sur la détection du type de données.
Analyse intelligente des colonnes pour proposer des graphiques pertinents.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataTypeDetector:
    """Détecte le type métier des données pour proposer des visualisations adaptées."""
    
    # Patterns de détection par type de données métier
    PATTERNS = {
        'reclamations': {
            'keywords': ['reclamation', 'plainte', 'incident', 'ticket', 'gravite', 'statut'],
            'required': 2
        },
        'satisfaction': {
            'keywords': ['satisfaction', 'nps', 'csat', 'ces', 'score', 'feedback', 'avis', 'note'],
            'required': 2
        },
        'ventes': {
            'keywords': ['vente', 'ventes', 'ca', 'chiffre', 'revenue', 'prix', 'montant', 'quantite'],
            'required': 2
        },
        'clients': {
            'keywords': ['client', 'age', 'sexe', 'segment', 'categorie_client', 'anciennete'],
            'required': 2
        },
        'finances': {
            'keywords': ['budget', 'depense', 'cout', 'marge', 'benefice', 'perte'],
            'required': 2
        },
        'rh': {
            'keywords': ['employe', 'salaire', 'poste', 'departement', 'anciennete', 'formation'],
            'required': 2
        },
        'produits': {
            'keywords': ['produit', 'stock', 'inventaire', 'reference', 'categorie_produit'],
            'required': 2
        }
    }
    
    @staticmethod
    def detect_data_type(df: pd.DataFrame) -> str:
        """
        Détecte le type métier du DataFrame.
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Type détecté ('reclamations', 'satisfaction', 'ventes', etc.) ou 'generique'
        """
        columns_lower = [col.lower().replace('_', '').replace(' ', '') for col in df.columns]
        
        scores = {}
        for data_type, config in DataTypeDetector.PATTERNS.items():
            keywords = config['keywords']
            required = config['required']
            
            matches = sum(1 for col in columns_lower 
                         if any(keyword in col for keyword in keywords))
            
            if matches >= required:
                scores[data_type] = matches
        
        if scores:
            detected_type = max(scores.items(), key=lambda x: x[1])[0]
            logger.info(f"Type de données détecté: {detected_type} (score: {scores[detected_type]})")
            return detected_type
        
        logger.info("Type de données: générique (aucun pattern détecté)")
        return 'generique'
    
    @staticmethod
    def identify_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Identifie les types de colonnes (date, numérique, catégorielle).
        
        Returns:
            Dict avec 'date', 'numeric', 'categorical', 'text'
        """
        column_types = {
            'date': [],
            'numeric': [],
            'categorical': [],
            'text': []
        }
        
        for col in df.columns:
            # Vérifier si c'est une date
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                column_types['date'].append(col)
            elif 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(df[col])
                    column_types['date'].append(col)
                except (ValueError, TypeError):
                    pass
            
            # Vérifier si c'est numérique
            elif pd.api.types.is_numeric_dtype(df[col]):
                # Si peu de valeurs uniques, c'est potentiellement catégoriel
                if df[col].nunique() < 10 and len(df) > 20:
                    column_types['categorical'].append(col)
                else:
                    column_types['numeric'].append(col)
            
            # Vérifier si c'est catégoriel
            elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                if df[col].nunique() < len(df) * 0.5:  # Moins de 50% de valeurs uniques
                    column_types['categorical'].append(col)
                else:
                    column_types['text'].append(col)
        
        return column_types


class AutoPlotter:
    """Génère automatiquement des visualisations pertinentes basées sur le type de données."""
    
    def __init__(self, export_dir: str = "./exports"):
        """
        Initialise le générateur de plots automatiques.
        
        Args:
            export_dir: Répertoire pour sauvegarder les visualisations
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        self.detector = DataTypeDetector()
    
    def generate_auto_plots(self, df: pd.DataFrame, max_plots: int = 6) -> List[Tuple[str, str]]:
        """
        Génère automatiquement des visualisations pertinentes.
        
        Args:
            df: DataFrame à visualiser
            max_plots: Nombre maximum de graphiques à générer
            
        Returns:
            Liste de tuples (titre, chemin_fichier)
        """
        data_type = self.detector.detect_data_type(df)
        column_types = self.detector.identify_column_types(df)
        
        logger.info(f"Génération de plots automatiques pour type: {data_type}")
        logger.info(f"Colonnes détectées: {column_types}")
        
        # Sélectionner la stratégie de visualisation
        if data_type == 'reclamations':
            return self._generate_reclamations_plots(df, column_types, max_plots)
        elif data_type == 'satisfaction':
            return self._generate_satisfaction_plots(df, column_types, max_plots)
        elif data_type == 'ventes':
            return self._generate_ventes_plots(df, column_types, max_plots)
        elif data_type == 'clients':
            return self._generate_clients_plots(df, column_types, max_plots)
        else:
            return self._generate_generic_plots(df, column_types, max_plots)
    
    def _generate_reclamations_plots(self, df: pd.DataFrame, column_types: Dict, max_plots: int) -> List[Tuple[str, str]]:
        """Génère des visualisations spécifiques aux réclamations."""
        plots = []
        
        # 1. Distribution des types de réclamations
        type_col = self._find_column(df, ['type', 'categorie', 'motif'])
        if type_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, type_col, "Distribution des types de réclamations")
            if plot_path:
                plots.append(("Distribution des types", plot_path))
        
        # 2. Distribution de la gravité
        gravite_col = self._find_column(df, ['gravite', 'severite', 'priorite'])
        if gravite_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, gravite_col, "Distribution par gravité")
            if plot_path:
                plots.append(("Distribution gravité", plot_path))
        
        # 3. Évolution temporelle
        if column_types['date'] and len(plots) < max_plots:
            date_col = column_types['date'][0]
            plot_path = self._plot_temporal_trend(df, date_col, "Évolution des réclamations")
            if plot_path:
                plots.append(("Évolution temporelle", plot_path))
        
        # 4. Top services/départements
        service_col = self._find_column(df, ['service', 'departement', 'equipe'])
        if service_col and len(plots) < max_plots:
            plot_path = self._plot_top_categories(df, service_col, "Top 10 services", top_n=10)
            if plot_path:
                plots.append(("Top services", plot_path))
        
        # 5. Délais de traitement
        delai_col = self._find_column(df, ['delai', 'duree', 'temps'])
        if delai_col and len(plots) < max_plots:
            plot_path = self._plot_boxplot(df, delai_col, "Distribution des délais de traitement")
            if plot_path:
                plots.append(("Délais de traitement", plot_path))
        
        # 6. Statut des réclamations
        statut_col = self._find_column(df, ['statut', 'etat', 'status'])
        if statut_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, statut_col, "Répartition par statut")
            if plot_path:
                plots.append(("Répartition statut", plot_path))
        
        return plots
    
    def _generate_satisfaction_plots(self, df: pd.DataFrame, column_types: Dict, max_plots: int) -> List[Tuple[str, str]]:
        """Génère des visualisations spécifiques à la satisfaction client."""
        plots = []
        
        # 1. Distribution du NPS
        nps_col = self._find_column(df, ['nps', 'net_promoter'])
        if nps_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, nps_col, "Distribution du NPS", bins=11)
            if plot_path:
                plots.append(("Distribution NPS", plot_path))
        
        # 2. Distribution CSAT
        csat_col = self._find_column(df, ['csat', 'satisfaction'])
        if csat_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, csat_col, "Distribution CSAT", bins=5)
            if plot_path:
                plots.append(("Distribution CSAT", plot_path))
        
        # 3. Évolution de la satisfaction
        if column_types['date'] and (nps_col or csat_col) and len(plots) < max_plots:
            date_col = column_types['date'][0]
            score_col = nps_col or csat_col
            plot_path = self._plot_temporal_trend(df, date_col, "Évolution de la satisfaction", value_col=score_col)
            if plot_path:
                plots.append(("Évolution satisfaction", plot_path))
        
        # 4. Satisfaction par service
        service_col = self._find_column(df, ['service', 'departement', 'equipe'])
        if service_col and (nps_col or csat_col) and len(plots) < max_plots:
            score_col = nps_col or csat_col
            plot_path = self._plot_grouped_avg(df, service_col, score_col, "Satisfaction moyenne par service")
            if plot_path:
                plots.append(("Satisfaction par service", plot_path))
        
        # 5. Distribution des sentiments
        sentiment_col = self._find_column(df, ['sentiment', 'emotion', 'feeling'])
        if sentiment_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, sentiment_col, "Répartition des sentiments")
            if plot_path:
                plots.append(("Répartition sentiments", plot_path))
        
        # 6. Corrélation temps d'attente / satisfaction
        temps_col = self._find_column(df, ['temps_attente', 'attente', 'wait'])
        if temps_col and (nps_col or csat_col) and len(plots) < max_plots:
            score_col = nps_col or csat_col
            plot_path = self._plot_scatter(df, temps_col, score_col, "Temps d'attente vs Satisfaction")
            if plot_path:
                plots.append(("Corrélation temps/satisfaction", plot_path))
        
        return plots
    
    def _generate_ventes_plots(self, df: pd.DataFrame, column_types: Dict, max_plots: int) -> List[Tuple[str, str]]:
        """Génère des visualisations spécifiques aux ventes."""
        plots = []
        
        # 1. Évolution des ventes
        if column_types['date'] and len(plots) < max_plots:
            date_col = column_types['date'][0]
            ventes_col = self._find_column(df, ['vente', 'ca', 'montant', 'revenue'])
            plot_path = self._plot_temporal_trend(df, date_col, "Évolution des ventes", value_col=ventes_col)
            if plot_path:
                plots.append(("Évolution ventes", plot_path))
        
        # 2. Ventes par région
        region_col = self._find_column(df, ['region', 'zone', 'territoire'])
        if region_col and len(plots) < max_plots:
            ventes_col = self._find_column(df, ['vente', 'ca', 'montant'])
            if ventes_col:
                plot_path = self._plot_grouped_sum(df, region_col, ventes_col, "Ventes par région")
                if plot_path:
                    plots.append(("Ventes par région", plot_path))
        
        # 3. Top produits
        produit_col = self._find_column(df, ['produit', 'article', 'item'])
        if produit_col and len(plots) < max_plots:
            plot_path = self._plot_top_categories(df, produit_col, "Top 10 produits", top_n=10)
            if plot_path:
                plots.append(("Top produits", plot_path))
        
        # 4. Distribution des prix
        prix_col = self._find_column(df, ['prix', 'price', 'tarif'])
        if prix_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, prix_col, "Distribution des prix", bins=20)
            if plot_path:
                plots.append(("Distribution prix", plot_path))
        
        # 5. Corrélation prix/quantité
        quantite_col = self._find_column(df, ['quantite', 'qty', 'volume'])
        if prix_col and quantite_col and len(plots) < max_plots:
            plot_path = self._plot_scatter(df, prix_col, quantite_col, "Prix vs Quantité")
            if plot_path:
                plots.append(("Prix vs Quantité", plot_path))
        
        return plots
    
    def _generate_clients_plots(self, df: pd.DataFrame, column_types: Dict, max_plots: int) -> List[Tuple[str, str]]:
        """Génère des visualisations spécifiques aux clients."""
        plots = []
        
        # 1. Distribution de l'âge
        age_col = self._find_column(df, ['age'])
        if age_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, age_col, "Distribution de l'âge", bins=15)
            if plot_path:
                plots.append(("Distribution âge", plot_path))
        
        # 2. Répartition par sexe
        sexe_col = self._find_column(df, ['sexe', 'genre', 'gender'])
        if sexe_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, sexe_col, "Répartition par sexe")
            if plot_path:
                plots.append(("Répartition sexe", plot_path))
        
        # 3. Clients par ville
        ville_col = self._find_column(df, ['ville', 'city', 'localite'])
        if ville_col and len(plots) < max_plots:
            plot_path = self._plot_top_categories(df, ville_col, "Top 10 villes", top_n=10)
            if plot_path:
                plots.append(("Top villes", plot_path))
        
        # 4. Distribution des revenus
        revenus_col = self._find_column(df, ['revenu', 'salaire', 'income'])
        if revenus_col and len(plots) < max_plots:
            plot_path = self._plot_distribution(df, revenus_col, "Distribution des revenus", bins=20)
            if plot_path:
                plots.append(("Distribution revenus", plot_path))
        
        return plots
    
    def _generate_generic_plots(self, df: pd.DataFrame, column_types: Dict, max_plots: int) -> List[Tuple[str, str]]:
        """Génère des visualisations génériques."""
        plots = []
        
        # 1. Distribution des colonnes numériques
        for col in column_types['numeric'][:2]:
            if len(plots) >= max_plots:
                break
            plot_path = self._plot_distribution(df, col, f"Distribution de {col}", bins=20)
            if plot_path:
                plots.append((f"Distribution {col}", plot_path))
        
        # 2. Distribution des colonnes catégorielles
        for col in column_types['categorical'][:2]:
            if len(plots) >= max_plots:
                break
            plot_path = self._plot_top_categories(df, col, f"Top 10 {col}", top_n=10)
            if plot_path:
                plots.append((f"Top {col}", plot_path))
        
        # 3. Évolution temporelle si date présente
        if column_types['date'] and column_types['numeric'] and len(plots) < max_plots:
            date_col = column_types['date'][0]
            numeric_col = column_types['numeric'][0]
            plot_path = self._plot_temporal_trend(df, date_col, f"Évolution de {numeric_col}", value_col=numeric_col)
            if plot_path:
                plots.append((f"Évolution {numeric_col}", plot_path))
        
        # 4. Scatter plot pour corrélations
        if len(column_types['numeric']) >= 2 and len(plots) < max_plots:
            col1, col2 = column_types['numeric'][:2]
            plot_path = self._plot_scatter(df, col1, col2, f"{col1} vs {col2}")
            if plot_path:
                plots.append((f"{col1} vs {col2}", plot_path))
        
        return plots
    
    # ================== Fonctions utilitaires ==================
    
    def _find_column(self, df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
        """Trouve une colonne par mots-clés."""
        columns_lower = {col.lower().replace('_', '').replace(' ', ''): col for col in df.columns}
        for keyword in keywords:
            keyword_clean = keyword.replace('_', '').replace(' ', '')
            for col_clean, col_original in columns_lower.items():
                if keyword_clean in col_clean:
                    return col_original
        return None
    
    def _plot_distribution(self, df: pd.DataFrame, column: str, title: str, bins: int = 20) -> Optional[str]:
        """Crée un histogramme de distribution."""
        try:
            plt.figure(figsize=(10, 6))
            
            if pd.api.types.is_numeric_dtype(df[column]):
                # Histogramme pour données numériques
                plt.hist(df[column].dropna(), bins=bins, edgecolor='black', alpha=0.7, color='#1f77b4')
                plt.xlabel(column)
                plt.ylabel("Fréquence")
            else:
                # Bar chart pour données catégorielles
                value_counts = df[column].value_counts().head(15)
                plt.bar(range(len(value_counts)), value_counts.values, edgecolor='black', alpha=0.7, color='#1f77b4')
                plt.xticks(range(len(value_counts)), value_counts.index, rotation=45, ha='right')
                plt.ylabel("Nombre")
            
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            filename = f"auto_plot_{self._sanitize_filename(title)}.png"
            filepath = self.export_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erreur lors de la création du plot de distribution: {e}")
            plt.close()
            return None
    
    def _plot_temporal_trend(self, df: pd.DataFrame, date_col: str, title: str, value_col: Optional[str] = None) -> Optional[str]:
        """Crée un line chart d'évolution temporelle."""
        try:
            plt.figure(figsize=(12, 6))
            
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col])
            df_temp = df_temp.sort_values(date_col)
            
            if value_col and value_col in df_temp.columns:
                # Agréger par date
                df_agg = df_temp.groupby(df_temp[date_col].dt.date)[value_col].mean().reset_index()
                plt.plot(df_agg[date_col], df_agg[value_col], marker='o', linewidth=2, markersize=4, color='#1f77b4')
                plt.ylabel(value_col)
            else:
                # Compter les occurrences par date
                df_agg = df_temp.groupby(df_temp[date_col].dt.date).size().reset_index(name='count')
                plt.plot(df_agg[date_col], df_agg['count'], marker='o', linewidth=2, markersize=4, color='#1f77b4')
                plt.ylabel("Nombre")
            
            plt.xlabel("Date")
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            filename = f"auto_plot_{self._sanitize_filename(title)}.png"
            filepath = self.export_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erreur lors de la création du plot temporel: {e}")
            plt.close()
            return None
    
    def _plot_top_categories(self, df: pd.DataFrame, column: str, title: str, top_n: int = 10) -> Optional[str]:
        """Crée un bar chart horizontal des top catégories."""
        try:
            plt.figure(figsize=(10, 8))
            
            value_counts = df[column].value_counts().head(top_n)
            y_pos = np.arange(len(value_counts))
            
            plt.barh(y_pos, value_counts.values, edgecolor='black', alpha=0.7, color='#1f77b4')
            plt.yticks(y_pos, value_counts.index)
            plt.xlabel("Nombre")
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(axis='x', alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            filename = f"auto_plot_{self._sanitize_filename(title)}.png"
            filepath = self.export_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erreur lors de la création du top categories plot: {e}")
            plt.close()
            return None
    
    def _plot_boxplot(self, df: pd.DataFrame, column: str, title: str) -> Optional[str]:
        """Crée un boxplot."""
        try:
            plt.figure(figsize=(10, 6))
            
            data = df[column].dropna()
            box = plt.boxplot([data], vert=True, patch_artist=True, widths=0.5)
            for patch in box['boxes']:
                patch.set_facecolor('#1f77b4')
                patch.set_alpha(0.7)
            
            plt.ylabel(column)
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.xticks([1], [column])
            plt.tight_layout()
            
            filename = f"auto_plot_{self._sanitize_filename(title)}.png"
            filepath = self.export_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erreur lors de la création du boxplot: {e}")
            plt.close()
            return None
    
    def _plot_grouped_avg(self, df: pd.DataFrame, group_col: str, value_col: str, title: str) -> Optional[str]:
        """Crée un bar chart des moyennes par groupe."""
        try:
            plt.figure(figsize=(12, 6))
            
            grouped = df.groupby(group_col)[value_col].mean().sort_values(ascending=False).head(15)
            x_pos = np.arange(len(grouped))
            
            plt.bar(x_pos, grouped.values, edgecolor='black', alpha=0.7, color='#1f77b4')
            plt.xticks(x_pos, grouped.index, rotation=45, ha='right')
            plt.ylabel(f"Moyenne {value_col}")
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            filename = f"auto_plot_{self._sanitize_filename(title)}.png"
            filepath = self.export_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erreur lors de la création du grouped avg plot: {e}")
            plt.close()
            return None
    
    def _plot_grouped_sum(self, df: pd.DataFrame, group_col: str, value_col: str, title: str) -> Optional[str]:
        """Crée un bar chart des sommes par groupe."""
        try:
            plt.figure(figsize=(12, 6))
            
            grouped = df.groupby(group_col)[value_col].sum().sort_values(ascending=False).head(15)
            x_pos = np.arange(len(grouped))
            
            plt.bar(x_pos, grouped.values, edgecolor='black', alpha=0.7, color='#1f77b4')
            plt.xticks(x_pos, grouped.index, rotation=45, ha='right')
            plt.ylabel(f"Total {value_col}")
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            filename = f"auto_plot_{self._sanitize_filename(title)}.png"
            filepath = self.export_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erreur lors de la création du grouped sum plot: {e}")
            plt.close()
            return None
    
    def _plot_scatter(self, df: pd.DataFrame, x_col: str, y_col: str, title: str) -> Optional[str]:
        """Crée un scatter plot."""
        try:
            plt.figure(figsize=(10, 6))
            
            df_clean = df[[x_col, y_col]].dropna()
            plt.scatter(df_clean[x_col], df_clean[y_col], alpha=0.5, edgecolor='black', linewidth=0.5, color='#1f77b4')
            
            # Ajouter une ligne de régression
            if len(df_clean) > 1:
                z = np.polyfit(df_clean[x_col], df_clean[y_col], 1)
                p = np.poly1d(z)
                plt.plot(df_clean[x_col], p(df_clean[x_col]), "r--", linewidth=2, alpha=0.8, label='Tendance')
                plt.legend()
            
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            filename = f"auto_plot_{self._sanitize_filename(title)}.png"
            filepath = self.export_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(filepath)
        except Exception as e:
            logger.error(f"Erreur lors de la création du scatter plot: {e}")
            plt.close()
            return None
    
    def _sanitize_filename(self, text: str) -> str:
        """Nettoie un texte pour créer un nom de fichier valide."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s-]+', '_', text)
        return text[:50]  # Limiter la longueur
