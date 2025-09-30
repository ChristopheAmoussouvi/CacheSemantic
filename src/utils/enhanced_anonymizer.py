"""
Module d'anonymisation avancée des données avec détection intelligente des noms non communs
et protection renforcée des informations sensibles.

Version améliorée avec IA heuristique pour la détection de noms rares et étrangers.
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import Dict, List, Tuple, Set, Optional, Any, Union
from dataclasses import dataclass, field
from collections import Counter
import unicodedata
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedAnonymizationConfig:
    """Configuration avancée pour l'anonymisation des données."""
    # Seuils de détection adaptatifs
    name_threshold_strict: float = 0.9  # Seuil strict pour noms évidents
    name_threshold_loose: float = 0.6   # Seuil souple pour noms possibles
    min_name_length: int = 2            # Longueur minimale d'un nom
    max_name_length: int = 50           # Longueur maximale d'un nom
    
    # Détection de noms avancée
    detect_uncommon_names: bool = True   # Détecter les noms non communs
    name_entropy_threshold: float = 2.5  # Seuil d'entropie pour détecter les noms
    capitalization_weight: float = 0.3   # Poids de la capitalisation
    
    # Patterns personnalisables
    account_patterns: Optional[List[str]] = None
    sensitive_patterns: Optional[List[str]] = None
    address_patterns: Optional[List[str]] = None
    
    # Options de préservation
    preserve_data_utility: bool = True
    preserve_statistical_properties: bool = True
    anonymization_mode: str = "balanced"  # "strict", "balanced", "permissive"
    
    # Nouvelles détections
    detect_addresses: bool = True
    detect_ids: bool = True
    detect_dates_of_birth: bool = True
    detect_biometric_data: bool = True

    def __post_init__(self):
        if self.account_patterns is None:
            self.account_patterns = [
                r'\b\d{10,20}\b',  # Numéros de compte longs
                r'\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b',  # Format IBAN
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Numéros de carte
                r'\b\d{3}-\d{2}-\d{4}\b',  # Format SSN américain
                r'\b\d{13}\b',  # Numéros NIR français (Sécurité Sociale)
                r'\b[A-Z]{1,2}\d{6,12}[A-Z]?\b',  # Identifiants bancaires
            ]

        if self.sensitive_patterns is None:
            self.sensitive_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',  # Emails
                r'\b(?:0[1-9]|(?:\+33|0033)[1-9])(?:[-.\s]?\d{2}){4}\b',  # Téléphones français étendus
                r'\b\+\d{1,3}[-.\s]?\d{1,14}\b',  # Téléphones internationaux
                r'\b\d{1,3}[,.]\d{3}[,.]\d{3}[,.]\d{3}\b',  # Numéros avec séparateurs
                r'\b\d{5}\b',  # Codes postaux français
                r'\b\d{1,5}[-\s]?\d{3,5}\b',  # Codes postaux autres
            ]

        if self.address_patterns is None:
            self.address_patterns = [
                r'\b\d+\s+(?:rue|avenue|boulevard|place|allée|impasse|chemin|route)\s+[A-Za-zÀ-ÿ\s]+\b',
                r'\b\d+\s+[A-Za-zÀ-ÿ\s]+(?:street|avenue|boulevard|road|lane|drive|court)\b',
                r'\b\d{5}\s+[A-Za-zÀ-ÿ-]+\b',  # Code postal + ville
                r'\b[A-Za-zÀ-ÿ-]+\s+\d{5}\b',  # Ville + code postal
            ]


@dataclass
class EnhancedAnonymizationReport:
    """Rapport détaillé des actions d'anonymisation effectuées."""
    columns_removed: List[str] = field(default_factory=list)
    columns_anonymized: List[str] = field(default_factory=list)
    sensitive_data_found: Dict[str, int] = field(default_factory=dict)
    uncommon_names_detected: Dict[str, List[str]] = field(default_factory=dict)
    addresses_found: int = 0
    ids_found: int = 0
    total_rows_processed: int = 0
    total_columns_processed: int = 0
    anonymization_score: float = 0.0  # Score de qualité d'anonymisation


class EnhancedDataAnonymizer:
    """
    Anonymiseur de données avancé avec détection intelligente des noms non communs.
    
    Utilise des heuristiques avancées pour détecter :
    - Noms propres rares et étrangers
    - Patterns de noms composés
    - Données sensibles complexes
    - Adresses et localisations
    """

    def __init__(self, config: Optional[EnhancedAnonymizationConfig] = None):
        """
        Initialise l'anonymiseur avancé.

        Args:
            config: Configuration d'anonymisation avancée
        """
        self.config = config or EnhancedAnonymizationConfig()
        self.report = EnhancedAnonymizationReport()

        # Bases de données de noms étendues
        self.french_first_names = self._load_french_names()
        self.french_last_names = self._load_french_last_names()
        self.arabic_names = self._load_arabic_names()  # Nouvelle base de noms arabes/maghrébins
        self.international_patterns = self._load_international_name_patterns()
        
        # Cache pour les analyses de noms
        self._name_analysis_cache: Dict[str, Tuple[bool, float, List[str]]] = {}
        self._entropy_cache: Dict[str, float] = {}

        logger.info("EnhancedDataAnonymizer initialisé avec mode: %s", self.config.anonymization_mode)

    def _load_arabic_names(self) -> Set[str]:
        """Charge une base étendue de noms arabes/maghrébins/berbères."""
        return {
            # Prénoms masculins arabes
            'mohamed', 'mohammed', 'muhammad', 'ahmad', 'ahmed', 'omar', 'umar', 'ali', 
            'hassan', 'hussein', 'youssef', 'yousef', 'joseph', 'ibrahim', 'ismail',
            'khalid', 'karim', 'tarek', 'tariq', 'samir', 'amin', 'nasser', 'said',
            'mahmoud', 'mustafa', 'abdullah', 'abderrahman', 'abdelkader', 'abdelaziz',
            
            # Prénoms féminins arabes
            'fatima', 'aisha', 'khadija', 'zahra', 'amina', 'safaa', 'nadia', 'leila',
            'sofia', 'maryam', 'salma', 'hanan', 'yasmin', 'dalal', 'wafa', 'nour',
            
            # Noms de famille maghrébins
            'benali', 'ben-ali', 'benameur', 'mansouri', 'el-mansouri', 'al-mansouri',
            'khaldoun', 'ibn-khaldoun', 'benaissa', 'bouazza', 'meziane', 'ouali',
            'zerhouni', 'tlemcani', 'fassi', 'alaoui', 'idrissi', 'hassani',
            
            # Noms berbères/amazighs
            'tamazight', 'amellal', 'azul', 'tanirt', 'tilelli', 'yemma', 'gouraya',
            'akli', 'mohand', 'ouali', 'amazigh', 'kabyle',
            
            # Particules et titres
            'sidi', 'moulay', 'lalla', 'sid', 'abu', 'abou', 'ould', 'bint'
        }

    def _load_french_names(self) -> Set[str]:
        """Charge une liste étendue de prénoms français."""
        return {
            # Prénoms classiques
            'marie', 'jean', 'pierre', 'paul', 'jacques', 'michel', 'andre', 'philippe',
            'anne', 'sophie', 'claire', 'emma', 'julie', 'sarah', 'lucas', 'thomas',
            'nicolas', 'antoine', 'camille', 'chloe', 'lea', 'manon', 'oceane', 'ambre',
            'louis', 'gabriel', 'raphael', 'arthur', 'hugo', 'mathis', 'noah', 'adam',
            # Prénoms modernes
            'enzo', 'theo', 'liam', 'nathan', 'maxime', 'ethan', 'timothe', 'tom',
            'lola', 'jade', 'louise', 'alice', 'celia', 'rose', 'anna', 'lina',
            # Prénoms composés
            'jean-luc', 'marie-claire', 'anne-sophie', 'jean-pierre', 'marie-france',
            # Variantes avec accents
            'élise', 'andré', 'cécile', 'rené', 'agnès', 'hélène', 'jérôme', 'françois'
        }

    def _load_french_last_names(self) -> Set[str]:
        """Charge une liste étendue de noms de famille français."""
        return {
            # Noms classiques
            'martin', 'bernard', 'durand', 'petit', 'robert', 'richard', 'moreau',
            'simon', 'laurent', 'lefebvre', 'michel', 'garcia', 'david', 'bertrand',
            'roussel', 'vincent', 'fournier', 'morel', 'girard', 'andre', 'lefevre',
            'mercier', 'dupont', 'lambert', 'bonnet', 'francois', 'martinez', 'legrand',
            # Noms composés et avec particules
            'de-la-fontaine', 'du-moulin', 'le-roy', 'saint-martin', 'van-den-berg',
            # Noms avec accents
            'françois', 'müller', 'josé', 'garcía', 'gonzález'
        }

    def _load_international_name_patterns(self) -> Dict[str, List[str]]:
        """Charge des patterns pour détecter les noms de différentes origines."""
        return {
            'arabic': [r'[A-Za-z]*(?:mohamed|ahmed|omar|hassan|ali|fatima|aisha)[A-Za-z]*'],
            'asian': [r'[A-Za-z]*(?:chen|wang|li|zhang|kim|park|tanaka|sato)[A-Za-z]*'],
            'african': [r'[A-Za-z]*(?:kone|traore|diallo|barry|camara|diouf)[A-Za-z]*'],
            'eastern_european': [r'[A-Za-z]*(?:ovski|ovsky|enko|ić|escu|escu)[A-Za-z]*'],
            'hispanic': [r'[A-Za-z]*(?:rodriguez|gonzalez|lopez|martinez|garcia)[A-Za-z]*'],
        }

    def calculate_name_entropy(self, text: str) -> float:
        """
        Calcule l'entropie d'un texte pour détecter les noms propres.
        
        Les noms propres ont généralement une entropie plus élevée que les mots communs.
        """
        if text in self._entropy_cache:
            return self._entropy_cache[text]
        
        if not text or len(text) < 2:
            return 0.0
        
        # Normaliser le texte
        text_clean = re.sub(r'[^a-zA-ZÀ-ÿ]', '', text.lower())
        
        if not text_clean:
            return 0.0
        
        # Calculer la distribution des caractères
        char_counts = Counter(text_clean)
        text_length = len(text_clean)
        
        # Calculer l'entropie de Shannon
        entropy = 0.0
        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        # Bonus pour la diversité des caractères
        char_diversity = len(char_counts) / len(text_clean)
        entropy_adjusted = entropy * (1 + char_diversity)
        
        self._entropy_cache[text] = entropy_adjusted
        return entropy_adjusted

    def analyze_capitalization_pattern(self, text: str) -> float:
        """Analyse les patterns de capitalisation - version TRÈS permissive pour noms du Maghreb."""
        if not text or len(text) < 2:
            return 0.0
        
        score = 0.0
        words = text.split()
        
        for word in words:
            if len(word) < 2:
                continue
                
            # Première lettre majuscule (bonus léger)
            if word[0].isupper():
                score += 0.3  # Réduit de 0.5 à 0.3
                
            # Reste en minuscules (pattern classique)
            if word[1:].islower():
                score += 0.1  # Réduit de 0.3 à 0.1
                
            # NOUVEAU: Bonus pour mots entièrement en minuscules s'ils sont connus
            elif word.islower() and self._is_known_name_word(word):
                score += 0.2  # Bonus pour noms connus en minuscules
                
            # Mélange majuscules/minuscules (noms composés)
            elif any(c.isupper() for c in word[1:]) and any(c.islower() for c in word[1:]):
                score += 0.1
        
        return min(score, 1.0)

    def _is_known_name_word(self, word: str) -> bool:
        """Vérifie si un mot en minuscules est un nom connu."""
        word_lower = word.lower()
        return (word_lower in self.french_first_names or 
                word_lower in self.french_last_names or 
                word_lower in self.arabic_names)

    def detect_international_name_patterns(self, text: str) -> bool:
        """Détecte les noms selon des patterns internationaux."""
        text_lower = text.lower()
        
        for origin, patterns in self.international_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return True
        
        return False

    def is_name_like_advanced(self, value: str) -> Tuple[bool, float, List[str]]:
        """
        Détection avancée des noms avec score de confidence et raisons.
        
        Returns:
            Tuple (is_name, confidence_score, detection_reasons)
        """
        if not isinstance(value, str) or len(value.strip()) < self.config.min_name_length:
            return False, 0.0, []

        value_clean = value.strip()
        
        # Vérifier la longueur
        if len(value_clean) > self.config.max_name_length:
            return False, 0.0, ["too_long"]

        # Cache pour éviter les recalculs
        cache_key = value_clean.lower()
        if cache_key in self._name_analysis_cache:
            cached_result = self._name_analysis_cache[cache_key]
            return cached_result[0], cached_result[1], cached_result[2]

        confidence_score = 0.0
        detection_reasons = []

        # 1. Vérifier les noms connus
        words = value_clean.split()
        known_name_score = 0.0
        for word in words:
            word_lower = word.lower()
            if word_lower in self.french_first_names:
                known_name_score += 0.8
                detection_reasons.append("known_first_name")
            elif word_lower in self.french_last_names:
                known_name_score += 0.7
                detection_reasons.append("known_last_name")
        
        if len(words) > 0:
            known_name_score /= len(words)
        confidence_score += known_name_score * 0.4

        # 2. Analyse des patterns internationaux
        if self.detect_international_name_patterns(value_clean):
            confidence_score += 0.3
            detection_reasons.append("international_pattern")

        # 3. Analyse de l'entropie
        entropy = self.calculate_name_entropy(value_clean)
        if entropy >= self.config.name_entropy_threshold:
            entropy_boost = min((entropy - self.config.name_entropy_threshold) / 2.0, 0.25)
            confidence_score += entropy_boost
            detection_reasons.append(f"high_entropy_{entropy:.2f}")

        # 4. Analyse de la capitalisation
        cap_score = self.analyze_capitalization_pattern(value_clean)
        confidence_score += cap_score * self.config.capitalization_weight
        if cap_score > 0.5:
            detection_reasons.append("proper_capitalization")

        # 5. Pattern structurel des noms
        name_pattern = r"^[A-Za-zÀ-ÿ]+(?:[-'\s][A-Za-zÀ-ÿ]+)*$"
        if re.match(name_pattern, value_clean):
            confidence_score += 0.15
            detection_reasons.append("name_structure")
            
            # Bonus pour les caractères accentués (noms français/européens)
            if any(char in value_clean for char in 'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'):
                confidence_score += 0.1
                detection_reasons.append("accented_chars")

        # 6. Structure multi-mots (prénom + nom)
        if len(words) >= 2:
            # Bonus si tous les mots ont au moins 2 caractères
            if all(len(word) >= 2 for word in words):
                confidence_score += 0.1
                detection_reasons.append("multi_word_structure")
            
            # Bonus pour 2-3 mots (structure nom classique)
            if 2 <= len(words) <= 3:
                confidence_score += 0.05
                detection_reasons.append("optimal_word_count")

        # 7. Détection des initiales (J.K. Rowling, etc.)
        initial_pattern = r'\b[A-Z]\.\s*[A-Z]\.?\s*[A-Za-zÀ-ÿ]+\b'
        if re.search(initial_pattern, value_clean):
            confidence_score += 0.2
            detection_reasons.append("initials_pattern")

        # Normaliser le score
        confidence_score = min(confidence_score, 1.0)

        # Décision basée sur les seuils
        is_name = False
        if confidence_score >= self.config.name_threshold_strict:
            is_name = True
        elif (confidence_score >= self.config.name_threshold_loose and 
              self.config.detect_uncommon_names):
            is_name = True

        # Mettre en cache
        result = (is_name, confidence_score, detection_reasons)
        self._name_analysis_cache[cache_key] = result

        return result

    def detect_name_columns_advanced(self, df: pd.DataFrame) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
        """
        Détection avancée des colonnes de noms avec analyse détaillée.
        
        Returns:
            Tuple (name_columns, detailed_analysis)
        """
        name_columns = []
        detailed_analysis = {}

        for col in df.columns:
            if df[col].dtype != 'object':
                continue

            # Échantillonnage intelligent
            sample_size = min(1000, len(df))
            sample = df[col].dropna()
            
            if len(sample) == 0:
                continue
                
            if len(sample) > sample_size:
                sample = sample.sample(n=sample_size, random_state=42)

            # Analyse détaillée de chaque valeur
            name_detections = []
            confidence_scores = []
            detection_reasons_all = []

            for value in sample:
                is_name, confidence, reasons = self.is_name_like_advanced(str(value))
                if is_name:
                    name_detections.append(value)
                    confidence_scores.append(confidence)
                    detection_reasons_all.extend(reasons)

            # Statistiques de la colonne
            name_ratio = len(name_detections) / len(sample)
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            reason_counts = Counter(detection_reasons_all)

            # Analyse contextuelle du nom de colonne
            col_name_hints = self._analyze_column_name(col)
            context_boost = col_name_hints.get('name_likelihood', 0.0)

            # Score final ajusté
            final_score = (name_ratio * 0.6 + avg_confidence * 0.3 + context_boost * 0.1)

            # Seuil adaptatif selon le mode
            threshold = self._get_adaptive_threshold(col, sample)

            # Décision
            is_name_column = final_score >= threshold

            # Stocker l'analyse détaillée
            detailed_analysis[col] = {
                'name_ratio': name_ratio,
                'avg_confidence': avg_confidence,
                'final_score': final_score,
                'threshold_used': threshold,
                'is_name_column': is_name_column,
                'sample_names': name_detections[:5],  # Échantillon
                'detection_reasons': dict(reason_counts),
                'column_name_hints': col_name_hints,
                'total_samples': len(sample)
            }

            if is_name_column:
                name_columns.append(col)
                # Stocker les noms détectés pour le rapport
                self.report.uncommon_names_detected[col] = name_detections[:10]

            logger.debug(f"Colonne '{col}': score={final_score:.3f}, seuil={threshold:.3f}, "
                        f"ratio_noms={name_ratio:.2%}, confiance={avg_confidence:.3f}")

        return name_columns, detailed_analysis

    def _analyze_column_name(self, col_name: str) -> Dict[str, Any]:
        """Analyse le nom de la colonne pour détecter les indices de noms."""
        col_lower = col_name.lower()
        
        # Mots-clés évidents
        obvious_name_keywords = [
            'nom', 'name', 'prenom', 'firstname', 'lastname', 'surname',
            'client', 'customer', 'user', 'person', 'people', 'individu'
        ]
        
        # Mots-clés possibles
        possible_name_keywords = [
            'titre', 'title', 'responsable', 'manager', 'contact',
            'signataire', 'beneficiaire', 'proprietaire'
        ]
        
        name_likelihood = 0.0
        hints = []
        
        for keyword in obvious_name_keywords:
            if keyword in col_lower:
                name_likelihood = max(name_likelihood, 0.8)
                hints.append(f"obvious_keyword_{keyword}")
        
        for keyword in possible_name_keywords:
            if keyword in col_lower:
                name_likelihood = max(name_likelihood, 0.4)
                hints.append(f"possible_keyword_{keyword}")
        
        # Patterns de noms de colonnes
        if re.search(r'nom.*complet|full.*name|complete.*name', col_lower):
            name_likelihood = max(name_likelihood, 0.9)
            hints.append("full_name_pattern")
        
        return {
            'name_likelihood': name_likelihood,
            'hints': hints
        }

    def _get_adaptive_threshold(self, col_name: str, sample: pd.Series) -> float:
        """Calcule un seuil adaptatif basé sur le contexte."""
        base_threshold = self.config.name_threshold_strict
        
        if self.config.anonymization_mode == "strict":
            return base_threshold * 0.8  # Plus strict
        elif self.config.anonymization_mode == "permissive":
            return base_threshold * 1.2  # Plus permissif
        
        # Mode balancé - ajustement contextuel
        col_hints = self._analyze_column_name(col_name)
        if col_hints['name_likelihood'] > 0.5:
            return base_threshold * 0.9  # Légèrement plus strict si colonne suspecte
        
        return base_threshold

    def detect_addresses(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Détecte les colonnes et valeurs contenant des adresses."""
        address_findings = {}
        
        text_columns = df.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            addresses_found = []
            
            # Échantillonner les données
            sample = df[col].dropna().astype(str).head(100)
            
            for value in sample:
                for pattern in self.config.address_patterns or []:
                    if re.search(pattern, value, re.IGNORECASE):
                        addresses_found.append(value)
                        break
            
            if addresses_found:
                address_findings[col] = addresses_found
                self.report.addresses_found += len(addresses_found)
        
        return address_findings

    def anonymize_dataframe_advanced(
        self, 
        df: pd.DataFrame, 
        preserve_utility: bool = True
    ) -> Tuple[pd.DataFrame, EnhancedAnonymizationReport]:
        """
        Anonymisation avancée avec détection intelligente.
        
        Returns:
            Tuple (DataFrame anonymisé, rapport détaillé)
        """
        logger.info(f"Début anonymisation avancée: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Réinitialiser le rapport
        self.report = EnhancedAnonymizationReport()
        self.report.total_rows_processed = len(df)
        self.report.total_columns_processed = len(df.columns)
        
        df_anonymized = df.copy()
        
        # 1. Détection avancée des colonnes de noms
        name_columns, name_analysis = self.detect_name_columns_advanced(df)
        if name_columns:
            df_anonymized = df_anonymized.drop(columns=name_columns)
            self.report.columns_removed.extend(name_columns)
            logger.info(f"Colonnes de noms supprimées: {name_columns}")
        
        # 2. Détection des comptes (version existante améliorée)
        account_columns = self.detect_account_columns_enhanced(df)
        if account_columns:
            df_anonymized = df_anonymized.drop(columns=account_columns)
            self.report.columns_removed.extend(account_columns)
            logger.info(f"Colonnes de comptes supprimées: {account_columns}")
        
        # 3. Détection et suppression des adresses
        if self.config.detect_addresses:
            address_findings = self.detect_addresses(df_anonymized)
            address_columns = list(address_findings.keys())
            # Option: supprimer ou anonymiser les colonnes d'adresses
            for col in address_columns:
                if len(address_findings[col]) / len(df_anonymized[col].dropna()) > 0.3:
                    df_anonymized = df_anonymized.drop(columns=[col])
                    self.report.columns_removed.append(col)
                else:
                    # Anonymiser les adresses dans le texte
                    df_anonymized[col] = df_anonymized[col].astype(str).apply(
                        self._anonymize_addresses_in_text
                    )
                    self.report.columns_anonymized.append(col)
        
        # 4. Traitement avancé des textes
        if preserve_utility:
            df_anonymized = self.process_text_fields_advanced(df_anonymized)
        
        # 5. Calcul du score d'anonymisation
        self.report.anonymization_score = self._calculate_anonymization_score(
            df, df_anonymized, name_analysis
        )
        
        logger.info(f"Anonymisation terminée: score={self.report.anonymization_score:.2f}, "
                   f"{len(self.report.columns_removed)} colonnes supprimées")
        
        return df_anonymized, self.report

    def detect_account_columns_enhanced(self, df: pd.DataFrame) -> List[str]:
        """Version améliorée de la détection de comptes avec patterns étendus."""
        account_columns = []
        
        for col in df.columns:
            if df[col].dtype not in ['object', 'int64', 'float64']:
                continue
            
            string_values = df[col].astype(str).str.strip()
            sensitive_count = 0
            total_non_null = len(string_values.dropna())
            
            if total_non_null == 0:
                continue
            
            # Patterns étendus
            for pattern in self.config.account_patterns or []:
                matches = string_values.str.contains(pattern, regex=True, na=False)
                sensitive_count += matches.sum()
            
            # Seuil adaptatif
            threshold = 0.3 if self.config.anonymization_mode == "permissive" else 0.2
            
            if sensitive_count / total_non_null > threshold:
                account_columns.append(col)
                self.report.sensitive_data_found[f"accounts_in_{col}"] = sensitive_count
        
        return account_columns

    def _anonymize_addresses_in_text(self, text: str) -> str:
        """Anonymise les adresses trouvées dans un texte."""
        if not isinstance(text, str):
            return text
        
        anonymized = text
        for pattern in self.config.address_patterns or []:
            anonymized = re.sub(pattern, '[ADRESSE_CENSUREE]', anonymized, flags=re.IGNORECASE)
        
        return anonymized

    def process_text_fields_advanced(self, df: pd.DataFrame) -> pd.DataFrame:
        """Traitement avancé des champs textuels avec détection contextuelle."""
        df_processed = df.copy()
        text_columns = df.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            if df[col].dtype != 'object':
                continue
            
            # Analyse contextuelle du contenu
            avg_length = df[col].astype(str).str.len().mean()
            unique_ratio = df[col].nunique() / len(df[col].dropna())
            
            # Traiter selon le type de contenu détecté
            if avg_length > 50 or unique_ratio > 0.8:  # Texte libre ou commentaires
                df_processed[col] = df[col].astype(str).apply(
                    self._anonymize_sensitive_text_advanced
                )
                self.report.columns_anonymized.append(col)
        
        return df_processed

    def _anonymize_sensitive_text_advanced(self, text: str) -> str:
        """Anonymisation avancée des textes avec détection contextuelle."""
        if not isinstance(text, str):
            return text
        
        anonymized = text
        
        # 1. Emails (pattern amélioré)
        anonymized = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
            '[EMAIL_CENSURE]',
            anonymized
        )
        
        # 2. Téléphones (patterns internationaux)
        phone_patterns = [
            r'\b(?:0[1-9]|(?:\+33|0033)[1-9])(?:[-.\s]?\d{2}){4}\b',  # Français
            r'\b\+\d{1,3}[-.\s]?\d{1,14}\b',  # International
            r'\b\d{10}\b',  # 10 chiffres d'affilée
        ]
        for pattern in phone_patterns:
            anonymized = re.sub(pattern, '[TELEPHONE_CENSURE]', anonymized)
        
        # 3. Comptes et identifiants
        for pattern in self.config.account_patterns or []:
            anonymized = re.sub(pattern, '[IDENTIFIANT_CENSURE]', anonymized)
        
        # 4. Adresses
        for pattern in self.config.address_patterns or []:
            anonymized = re.sub(pattern, '[ADRESSE_CENSUREE]', anonymized, flags=re.IGNORECASE)
        
        # 5. Noms dans le texte (utilisation de la détection avancée)
        words = anonymized.split()
        anonymized_words = []
        
        for word in words:
            # Nettoyer le mot pour l'analyse
            clean_word = re.sub(r'[^\w\s]', '', word)
            if len(clean_word) >= 2:
                is_name, confidence, _ = self.is_name_like_advanced(clean_word)
                if is_name and confidence > 0.6:
                    anonymized_words.append('[NOM_CENSURE]')
                else:
                    anonymized_words.append(word)
            else:
                anonymized_words.append(word)
        
        return ' '.join(anonymized_words)

    def _calculate_anonymization_score(
        self, 
        original_df: pd.DataFrame, 
        anonymized_df: pd.DataFrame,
        name_analysis: Dict[str, Dict[str, Any]]
    ) -> float:
        """Calcule un score de qualité de l'anonymisation (0-1)."""
        score = 0.0
        
        # 1. Colonnes supprimées vs détectées (30%)
        columns_removed_score = len(self.report.columns_removed) / max(len(original_df.columns), 1)
        score += min(columns_removed_score * 2, 0.3)  # Max 30%
        
        # 2. Qualité de la détection de noms (40%)
        total_confidence = 0.0
        total_analyses = 0
        for analysis in name_analysis.values():
            if analysis['is_name_column']:
                total_confidence += analysis['avg_confidence']
                total_analyses += 1
        
        if total_analyses > 0:
            avg_detection_confidence = total_confidence / total_analyses
            score += avg_detection_confidence * 0.4
        
        # 3. Préservation de l'utilité des données (20%)
        utility_score = len(anonymized_df.columns) / max(len(original_df.columns), 1)
        score += utility_score * 0.2
        
        # 4. Données sensibles trouvées et traitées (10%)
        sensitive_items = sum(self.report.sensitive_data_found.values())
        if sensitive_items > 0:
            score += min(sensitive_items / 100, 0.1)
        
        return min(score, 1.0)


def create_test_data_with_uncommon_names() -> pd.DataFrame:
    """Crée des données de test avec des noms non communs pour valider l'amélioration."""
    return pd.DataFrame({
        'client_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
        'nom_complet': [
            'Marie Martin',  # Nom français commun
            'Aleksandr Volkov',  # Nom russe/slave
            'Hiroshi Tanaka',  # Nom japonais
            'Kwame Asante',  # Nom africain
            'Zara Al-Rashid'  # Nom arabe
        ],
        'prenom_rare': [
            'Xylia',  # Prénom très rare
            'Zorion',  # Prénom basque
            'Nayeli',  # Prénom nahuatl
            'Cosmin',  # Prénom roumain
            'Thaddeus'  # Prénom anglais rare
        ],
        'email': ['marie@example.com', 'alex@example.com', 'h.tanaka@example.com', 'kwame@example.com', 'zara@example.com'],
        'adresse': [
            '123 rue de la Paix, 75001 Paris',
            '456 avenue des Champs, 69000 Lyon',
            '789 boulevard Voltaire, 13000 Marseille',
            '321 place de la République, 44000 Nantes',
            '654 allée des Tilleuls, 67000 Strasbourg'
        ],
        'telephone': ['0123456789', '+33123456789', '0987654321', '+41123456789', '0145678901'],
        'numero_compte': ['FR1420041010050500013M02606', 'GB82WEST12345698765432', 'DE89370400440532013000', 'CH9300762011623852957', 'IT60X0542811101000000123456'],
        'commentaire': [
            'Client Xylia très satisfait. Contact: marie@example.com, habite 123 rue de la Paix',
            'Aleksandr Volkov a appelé au +33123456789 pour son compte GB82WEST12345698765432',
            'Rendez-vous avec Hiroshi Tanaka prévu',
            'Kwame Asante domicilié 321 place de la République',
            'Zara Al-Rashid, nouvelle cliente'
        ],
        'montant': [150.50, 230.75, 89.90, 456.20, 78.30],
        'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
    })


if __name__ == "__main__":
    # Test du module d'anonymisation amélioré
    print("🚀 Test du module d'anonymisation amélioré")
    print("=" * 60)
    
    # Créer des données de test avec noms non communs
    test_data = create_test_data_with_uncommon_names()
    
    print("📊 Données originales:")
    print(test_data)
    print("\n" + "=" * 60)
    
    # Configuration pour les tests
    config = EnhancedAnonymizationConfig(
        detect_uncommon_names=True,
        anonymization_mode="balanced",
        detect_addresses=True
    )
    
    # Test de l'anonymiseur amélioré
    anonymizer = EnhancedDataAnonymizer(config)
    
    # Analyse préliminaire
    print("🔍 Analyse des noms détectés:")
    for col in ['nom_complet', 'prenom_rare']:
        if col in test_data.columns:
            print(f"\n--- Colonne: {col} ---")
            for value in test_data[col].dropna():
                is_name, confidence, reasons = anonymizer.is_name_like_advanced(value)
                print(f"'{value}': {is_name} (confiance: {confidence:.3f}) - {reasons}")
    
    print("\n" + "=" * 60)
    
    # Anonymisation complète
    df_anonymized, report = anonymizer.anonymize_dataframe_advanced(test_data)
    
    print("🛡️ Données anonymisées:")
    print(df_anonymized)
    print("\n" + "=" * 60)
    
    print("📈 Rapport d'anonymisation avancé:")
    print(f"• Colonnes supprimées: {report.columns_removed}")
    print(f"• Colonnes anonymisées: {report.columns_anonymized}")
    print(f"• Noms non communs détectés: {report.uncommon_names_detected}")
    print(f"• Adresses trouvées: {report.addresses_found}")
    print(f"• Données sensibles: {report.sensitive_data_found}")
    print(f"• Score d'anonymisation: {report.anonymization_score:.3f}/1.0")
    print(f"• Lignes traitées: {report.total_rows_processed}")
    print(f"• Colonnes finales: {len(df_anonymized.columns)}/{report.total_columns_processed}")