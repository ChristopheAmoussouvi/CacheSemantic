"""
Version avancée du module d'anonymisation intégrant spaCy pour une détection
encore plus précise des entités nommées et des noms non communs.
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

# Import spaCy avec gestion d'erreur
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
    
    # Tentative de chargement des modèles spaCy
    try:
        # Modèle français
        nlp_fr = spacy.load("fr_core_news_sm")
        SPACY_FR_AVAILABLE = True
    except OSError:
        nlp_fr = None
        SPACY_FR_AVAILABLE = False
    
    try:
        # Modèle multilingue
        nlp_xx = spacy.load("xx_core_web_sm")
        SPACY_XX_AVAILABLE = True
    except OSError:
        nlp_xx = None
        SPACY_XX_AVAILABLE = False
        
except ImportError:
    spacy = None
    nlp_fr = None
    nlp_xx = None
    SPACY_AVAILABLE = False
    SPACY_FR_AVAILABLE = False
    SPACY_XX_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SpacyEnhancedAnonymizationConfig:
    """Configuration avancée pour l'anonymisation avec spaCy."""
    # Seuils de détection adaptatifs
    name_threshold_strict: float = 0.9
    name_threshold_loose: float = 0.6
    min_name_length: int = 2
    max_name_length: int = 50
    
    # Détection spaCy
    use_spacy: bool = True
    spacy_weight: float = 0.4  # Poids de spaCy dans le score final
    spacy_confidence_threshold: float = 0.7  # Seuil de confiance spaCy
    
    # Détection de noms avancée
    detect_uncommon_names: bool = True
    name_entropy_threshold: float = 2.3  # Réduit pour être plus permissif
    capitalization_weight: float = 0.2   # Réduit pour ne pas pénaliser les minuscules
    
    # Patterns étendus
    account_patterns: Optional[List[str]] = None
    sensitive_patterns: Optional[List[str]] = None
    address_patterns: Optional[List[str]] = None
    
    # Patterns spécifiques au Maghreb/monde arabe
    arabic_patterns: Optional[List[str]] = None
    
    # Options de préservation
    preserve_data_utility: bool = True
    preserve_statistical_properties: bool = True
    anonymization_mode: str = "balanced"
    
    # Nouvelles détections
    detect_addresses: bool = True
    detect_ids: bool = True
    detect_dates_of_birth: bool = True
    detect_biometric_data: bool = True

    def __post_init__(self):
        if self.account_patterns is None:
            self.account_patterns = [
                r'\b\d{10,20}\b',
                r'\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b',
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                r'\b\d{3}-\d{2}-\d{4}\b',
                r'\b\d{13}\b',
                r'\b[A-Z]{1,2}\d{6,12}[A-Z]?\b',
            ]

        if self.sensitive_patterns is None:
            self.sensitive_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                r'\b(?:0[1-9]|(?:\+33|0033)[1-9])(?:[-.\s]?\d{2}){4}\b',
                r'\b\+\d{1,3}[-.\s]?\d{1,14}\b',
                r'\b\d{1,3}[,.]\d{3}[,.]\d{3}[,.]\d{3}\b',
                r'\b\d{5}\b',
                r'\b\d{1,5}[-\s]?\d{3,5}\b',
            ]

        if self.address_patterns is None:
            self.address_patterns = [
                r'\b\d+\s+(?:rue|avenue|boulevard|place|allée|impasse|chemin|route)\s+[A-Za-zÀ-ÿ\s]+\b',
                r'\b\d+\s+[A-Za-zÀ-ÿ\s]+(?:street|avenue|boulevard|road|lane|drive|court)\b',
                r'\b\d{5}\s+[A-Za-zÀ-ÿ-]+\b',
                r'\b[A-Za-zÀ-ÿ-]+\s+\d{5}\b',
            ]
        
        if self.arabic_patterns is None:
            self.arabic_patterns = [
                # Patterns pour noms arabes/maghrébins
                r'\b(al|el)-[a-zA-ZÀ-ÿ]+\b',
                r'\babd\s+(al|el|allah|rahman|aziz|malik|karim)\b',
                r'\bben\s+[a-zA-ZÀ-ÿ]+\b',
                r'\bibn\s+[a-zA-ZÀ-ÿ]+\b',
                r'\bould\s+[a-zA-ZÀ-ÿ]+\b',
                r'\bbint\s+[a-zA-ZÀ-ÿ]+\b',
                r'\bsidi\s+[a-zA-ZÀ-ÿ]+\b',
                r'\b(abu|abou)\s+[a-zA-ZÀ-ÿ]+\b',
                r'\b(mohamed|mohammed|muhammad|ahmad|ahmed|omar|umar|ali|hassan|hussein|fatima|aisha|khadija|zahra|amina)\b',
                # Noms berbères/amazighs
                r'\b(tamazight|yemma|dda|lalla|amellal|azul|tanirt|tilelli)\b',
                # Particules de noblesse
                r'\b(moulay|lalla|sidi|sid)\s+[a-zA-ZÀ-ÿ]+\b'
            ]


@dataclass
class SpacyEnhancedAnonymizationReport:
    """Rapport détaillé avec informations spaCy."""
    columns_removed: List[str] = field(default_factory=list)
    columns_anonymized: List[str] = field(default_factory=list)
    sensitive_data_found: Dict[str, int] = field(default_factory=dict)
    uncommon_names_detected: Dict[str, List[str]] = field(default_factory=dict)
    spacy_detections: Dict[str, List[str]] = field(default_factory=dict)
    addresses_found: int = 0
    ids_found: int = 0
    total_rows_processed: int = 0
    total_columns_processed: int = 0
    anonymization_score: float = 0.0
    spacy_model_used: Optional[str] = None
    spacy_availability: Dict[str, bool] = field(default_factory=dict)


class SpacyEnhancedDataAnonymizer:
    """
    Anonymiseur de données avancé intégrant spaCy pour la reconnaissance d'entités nommées.
    
    Combine l'analyse heuristique avec la puissance de spaCy pour une détection
    ultra-précise des noms propres et entités sensibles.
    """

    def __init__(self, config: Optional[SpacyEnhancedAnonymizationConfig] = None):
        """
        Initialise l'anonymiseur avec spaCy.

        Args:
            config: Configuration d'anonymisation avancée
        """
        self.config = config or SpacyEnhancedAnonymizationConfig()
        self.report = SpacyEnhancedAnonymizationReport()

        # Bases de données de noms étendues
        self.french_first_names = self._load_french_names()
        self.french_last_names = self._load_french_last_names()
        self.arabic_names = self._load_arabic_names()
        self.international_patterns = self._load_international_name_patterns()
        
        # Configuration spaCy
        self.spacy_available = SPACY_AVAILABLE
        self.nlp_fr = nlp_fr if SPACY_FR_AVAILABLE else None
        self.nlp_xx = nlp_xx if SPACY_XX_AVAILABLE else None
        
        # Informations sur la disponibilité
        self.report.spacy_availability = {
            'spacy_installed': SPACY_AVAILABLE,
            'french_model': SPACY_FR_AVAILABLE,
            'multilingual_model': SPACY_XX_AVAILABLE
        }
        
        # Cache pour les analyses
        self._name_analysis_cache: Dict[str, Tuple[bool, float, List[str]]] = {}
        self._entropy_cache: Dict[str, float] = {}
        self._spacy_cache: Dict[str, List[str]] = {}

        # Log de la configuration spaCy
        if self.spacy_available and self.config.use_spacy:
            models = []
            if self.nlp_fr:
                models.append("fr_core_news_sm")
            if self.nlp_xx:
                models.append("xx_core_web_sm")
            self.report.spacy_model_used = ", ".join(models) if models else "None"
            logger.info("SpacyEnhancedDataAnonymizer initialisé avec spaCy: %s", self.report.spacy_model_used)
        else:
            logger.warning("SpaCy non disponible - utilisation des heuristiques uniquement")

    def _load_arabic_names(self) -> Set[str]:
        """Charge une base de noms arabes/maghrébins/berbères."""
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
            'khaldoun', 'ibn-khaldoun', 'benaissa', 'bouazza', 'meziane',
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
            'marie', 'jean', 'pierre', 'paul', 'jacques', 'michel', 'andre', 'philippe',
            'anne', 'sophie', 'claire', 'emma', 'julie', 'sarah', 'lucas', 'thomas',
            'nicolas', 'antoine', 'camille', 'chloe', 'lea', 'manon', 'oceane', 'ambre',
            'louis', 'gabriel', 'raphael', 'arthur', 'hugo', 'mathis', 'noah', 'adam',
            'enzo', 'theo', 'liam', 'nathan', 'maxime', 'ethan', 'timothe', 'tom',
            'lola', 'jade', 'louise', 'alice', 'celia', 'rose', 'anna', 'lina',
            'jean-luc', 'marie-claire', 'anne-sophie', 'jean-pierre', 'marie-france',
            'élise', 'andré', 'cécile', 'rené', 'agnès', 'hélène', 'jérôme', 'françois'
        }

    def _load_french_last_names(self) -> Set[str]:
        """Charge une liste étendue de noms de famille français."""
        return {
            'martin', 'bernard', 'durand', 'petit', 'robert', 'richard', 'moreau',
            'simon', 'laurent', 'lefebvre', 'michel', 'garcia', 'david', 'bertrand',
            'roussel', 'vincent', 'fournier', 'morel', 'girard', 'andre', 'lefevre',
            'mercier', 'dupont', 'lambert', 'bonnet', 'francois', 'martinez', 'legrand',
            'de-la-fontaine', 'du-moulin', 'le-roy', 'saint-martin', 'van-den-berg',
            'françois', 'müller', 'josé', 'garcía', 'gonzález'
        }

    def _load_international_name_patterns(self) -> Dict[str, List[str]]:
        """Charge des patterns étendus pour détecter les noms internationaux."""
        return {
            'arabic': [
                r'[A-Za-z]*(?:mohamed|ahmed|omar|hassan|ali|fatima|aisha|khadija|zahra|amina|hassan|hussein|youssef|khalid|karim|tarek|samir|amin|nasser|said|mahmoud|mustafa|abdullah|abderrahman|abdelkader|abdelaziz)[A-Za-z]*',
                r'[A-Za-z]*(?:al|el)-[A-Za-z]+',
                r'[A-Za-z]*(?:ben|ibn|ould|bint)\s+[A-Za-z]+',
                r'[A-Za-z]*(?:sidi|moulay|lalla)\s+[A-Za-z]+'
            ],
            'berber': [
                r'[A-Za-z]*(?:tamazight|amellal|azul|tanirt|tilelli|yemma|gouraya|akli|mohand|ouali|amazigh)[A-Za-z]*'
            ],
            'asian': [r'[A-Za-z]*(?:chen|wang|li|zhang|kim|park|tanaka|sato|hiroshi|yuki|takeshi)[A-Za-z]*'],
            'african': [r'[A-Za-z]*(?:kone|traore|diallo|barry|camara|diouf|kwame|asante|kofi|ama)[A-Za-z]*'],
            'eastern_european': [r'[A-Za-z]*(?:ovski|ovsky|enko|ić|escu|ski|aleksandr|vladimir|dmitri)[A-Za-z]*'],
            'hispanic': [r'[A-Za-z]*(?:rodriguez|gonzalez|lopez|martinez|garcia|fernando|alejandro|carmen)[A-Za-z]*'],
        }

    def analyze_with_spacy(self, text: str) -> Tuple[List[str], float]:
        """
        Analyse un texte avec spaCy pour détecter les entités nommées.
        
        Returns:
            Tuple (entités_détectées, score_confiance)
        """
        if not self.spacy_available or not self.config.use_spacy:
            return [], 0.0
        
        # Cache pour éviter les recomputations
        if text in self._spacy_cache:
            entities = self._spacy_cache[text]
            confidence = 0.9 if entities else 0.0
            return entities, confidence
        
        entities = []
        max_confidence = 0.0
        
        # Essayer le modèle français en priorité
        if self.nlp_fr and any(char in text.lower() for char in 'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'):
            doc = self.nlp_fr(text)
        # Sinon utiliser le modèle multilingue
        elif self.nlp_xx:
            doc = self.nlp_xx(text)
        else:
            # Fallback sur le modèle français s'il est disponible
            if self.nlp_fr:
                doc = self.nlp_fr(text)
            else:
                return [], 0.0
        
        # Extraire les entités de type PERSON
        for ent in doc.ents:
            if ent.label_ == "PERSON" or ent.label_ == "PER":
                entities.append(ent.text.strip())
                # spaCy ne fournit pas toujours de score de confiance, utiliser un score fixe
                max_confidence = max(max_confidence, 0.8)
        
        # Analyser aussi les tokens étiquetés comme noms propres
        for token in doc:
            if token.pos_ == "PROPN" and token.text.strip() not in entities:
                # Vérifier si c'est vraiment un nom (pas une marque, lieu, etc.)
                if self._looks_like_person_name(token.text):
                    entities.append(token.text.strip())
                    max_confidence = max(max_confidence, 0.6)
        
        # Mettre en cache
        self._spacy_cache[text] = entities
        
        return entities, max_confidence

    def _looks_like_person_name(self, token: str) -> bool:
        """Vérifie si un token ressemble à un nom de personne."""
        if len(token) < 2:
            return False
        
        # Pattern basique pour noms
        if re.match(r'^[A-Za-zÀ-ÿ\-\']+$', token):
            # Éviter les mots trop communs qui ne sont pas des noms
            common_words = {'paris', 'france', 'europe', 'google', 'microsoft', 'apple'}
            return token.lower() not in common_words
        
        return False

    def calculate_name_entropy(self, text: str) -> float:
        """Calcule l'entropie d'un texte pour détecter les noms propres."""
        if text in self._entropy_cache:
            return self._entropy_cache[text]
        
        if not text or len(text) < 2:
            return 0.0
        
        text_clean = re.sub(r'[^a-zA-ZÀ-ÿ]', '', text.lower())
        
        if not text_clean:
            return 0.0
        
        char_counts = Counter(text_clean)
        text_length = len(text_clean)
        
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
        """Analyse les patterns de capitalisation - version plus permissive."""
        if not text or len(text) < 2:
            return 0.0
        
        score = 0.0
        words = text.split()
        
        for word in words:
            if len(word) < 2:
                continue
                
            # Première lettre majuscule (même si le reste est en minuscules)
            if word[0].isupper():
                score += 0.4  # Réduit de 0.5 à 0.4
                
            # Reste en minuscules (pattern nom propre classique)
            if word[1:].islower():
                score += 0.2  # Réduit de 0.3 à 0.2
                
            # NOUVEAU: Bonus pour mots entièrement en minuscules dans certains contextes
            elif word.islower() and self._is_known_name_word(word):
                score += 0.3  # Nouveau bonus pour noms connus en minuscules
                
            # Mélange majuscules/minuscules (noms composés)
            elif any(c.isupper() for c in word[1:]) and any(c.islower() for c in word[1:]):
                score += 0.1  # Réduit de 0.2 à 0.1
        
        return min(score, 1.0)

    def _is_known_name_word(self, word: str) -> bool:
        """Vérifie si un mot en minuscules est un nom connu."""
        word_lower = word.lower()
        return (word_lower in self.french_first_names or 
                word_lower in self.french_last_names or 
                word_lower in self.arabic_names)

    def detect_international_name_patterns(self, text: str) -> Tuple[bool, List[str]]:
        """Détecte les noms selon des patterns internationaux étendus."""
        text_lower = text.lower()
        detected_origins = []
        
        # Patterns arabes/maghrébins prioritaires
        for pattern in self.config.arabic_patterns or []:
            if re.search(pattern, text_lower, re.IGNORECASE):
                detected_origins.append('arabic_maghreb')
                break
        
        # Autres patterns internationaux
        for origin, patterns in self.international_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected_origins.append(origin)
                    break
        
        return len(detected_origins) > 0, detected_origins

    def is_name_like_advanced_spacy(self, value: str) -> Tuple[bool, float, List[str]]:
        """
        Détection avancée des noms avec spaCy intégré.
        
        Returns:
            Tuple (is_name, confidence_score, detection_reasons)
        """
        if not isinstance(value, str) or len(value.strip()) < self.config.min_name_length:
            return False, 0.0, []

        value_clean = value.strip()
        
        if len(value_clean) > self.config.max_name_length:
            return False, 0.0, ["too_long"]

        # Cache
        cache_key = value_clean.lower()
        if cache_key in self._name_analysis_cache:
            cached_result = self._name_analysis_cache[cache_key]
            return cached_result[0], cached_result[1], cached_result[2]

        confidence_score = 0.0
        detection_reasons = []

        # 1. Analyse spaCy (prioritaire si disponible)
        spacy_entities, spacy_confidence = self.analyze_with_spacy(value_clean)
        if spacy_entities and spacy_confidence >= self.config.spacy_confidence_threshold:
            confidence_score += self.config.spacy_weight
            detection_reasons.append(f"spacy_person_{spacy_confidence:.2f}")
            # Stocker les détections spaCy pour le rapport
            col_key = "individual_analysis"
            if col_key not in self.report.spacy_detections:
                self.report.spacy_detections[col_key] = []
            self.report.spacy_detections[col_key].extend(spacy_entities)

        # 2. Vérifier les noms connus (poids réduit si spaCy confirme)
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
            elif word_lower in self.arabic_names:
                known_name_score += 0.8
                detection_reasons.append("known_arabic_name")
        
        if len(words) > 0:
            known_name_score /= len(words)
        confidence_score += known_name_score * 0.3  # Poids réduit si spaCy est actif

        # 3. Analyse des patterns internationaux (avec focus Maghreb/arabe)
        is_international, origins = self.detect_international_name_patterns(value_clean)
        if is_international:
            confidence_score += 0.25  # Légèrement réduit
            for origin in origins:
                detection_reasons.append(f"pattern_{origin}")

        # 4. Analyse de l'entropie
        entropy = self.calculate_name_entropy(value_clean)
        if entropy >= self.config.name_entropy_threshold:
            entropy_boost = min((entropy - self.config.name_entropy_threshold) / 2.0, 0.2)
            confidence_score += entropy_boost
            detection_reasons.append(f"high_entropy_{entropy:.2f}")

        # 5. Analyse de la capitalisation (poids réduit)
        cap_score = self.analyze_capitalization_pattern(value_clean)
        confidence_score += cap_score * self.config.capitalization_weight
        if cap_score > 0.4:  # Seuil réduit
            detection_reasons.append("capitalization_pattern")

        # 6. Pattern structurel des noms
        name_pattern = r"^[A-Za-zÀ-ÿ]+(?:[-'\s][A-Za-zÀ-ÿ]+)*$"
        if re.match(name_pattern, value_clean):
            confidence_score += 0.1
            detection_reasons.append("name_structure")
            
            # Bonus pour les caractères accentués
            if any(char in value_clean for char in 'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'):
                confidence_score += 0.05
                detection_reasons.append("accented_chars")

        # 7. Structure multi-mots
        if len(words) >= 2:
            if all(len(word) >= 2 for word in words):
                confidence_score += 0.05
                detection_reasons.append("multi_word_structure")
            
            if 2 <= len(words) <= 3:
                confidence_score += 0.03
                detection_reasons.append("optimal_word_count")

        # 8. Détection des initiales
        initial_pattern = r'\b[A-Z]\.\s*[A-Z]\.?\s*[A-Za-zÀ-ÿ]+\b'
        if re.search(initial_pattern, value_clean):
            confidence_score += 0.15
            detection_reasons.append("initials_pattern")

        # Normaliser le score
        confidence_score = min(confidence_score, 1.0)

        # Décision avec seuils adaptatifs
        is_name = (confidence_score >= self.config.name_threshold_strict or 
                   (confidence_score >= self.config.name_threshold_loose and 
                    self.config.detect_uncommon_names))

        # Mettre en cache
        result = (is_name, confidence_score, detection_reasons)
        self._name_analysis_cache[cache_key] = result

        return result

    def detect_name_columns_advanced_spacy(self, df: pd.DataFrame) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
        """
        Détection avancée des colonnes de noms avec spaCy intégré.
        
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

            # Analyse détaillée avec spaCy
            name_detections = []
            confidence_scores = []
            detection_reasons_all = []
            spacy_detections = []

            for value in sample:
                is_name, confidence, reasons = self.is_name_like_advanced_spacy(str(value))
                if is_name:
                    name_detections.append(value)
                    confidence_scores.append(confidence)
                    detection_reasons_all.extend(reasons)
                    
                    # Vérifier les détections spaCy spécifiques
                    entities, _ = self.analyze_with_spacy(str(value))
                    spacy_detections.extend(entities)

            # Stocker les détections spaCy pour cette colonne
            if spacy_detections:
                self.report.spacy_detections[col] = spacy_detections

            # Statistiques de la colonne
            name_ratio = len(name_detections) / len(sample)
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            reason_counts = Counter(detection_reasons_all)

            # Analyse contextuelle du nom de colonne
            col_name_hints = self._analyze_column_name(col)
            context_boost = col_name_hints.get('name_likelihood', 0.0)

            # Score final ajusté
            final_score = (name_ratio * 0.6 + avg_confidence * 0.3 + context_boost * 0.1)

            # Seuil adaptatif
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
                'sample_names': name_detections[:5],
                'detection_reasons': dict(reason_counts),
                'column_name_hints': col_name_hints,
                'spacy_detections': len(spacy_detections),
                'total_samples': len(sample)
            }

            if is_name_column:
                name_columns.append(col)
                # Stocker les noms détectés pour le rapport
                self.report.uncommon_names_detected[col] = name_detections[:10]

            logger.debug("Colonne '%s': score=%.3f, seuil=%.3f, ratio_noms=%.2f%%, confiance=%.3f, spacy=%d", 
                        col, final_score, threshold, name_ratio, avg_confidence, len(spacy_detections))

        return name_columns, detailed_analysis

    def _analyze_column_name(self, col_name: str) -> Dict[str, Any]:
        """Analyse le nom de la colonne pour détecter les indices de noms."""
        col_lower = col_name.lower()
        
        obvious_name_keywords = [
            'nom', 'name', 'prenom', 'firstname', 'lastname', 'surname',
            'client', 'customer', 'user', 'person', 'people', 'individu'
        ]
        
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
            return base_threshold * 0.8
        elif self.config.anonymization_mode == "permissive":
            return base_threshold * 1.2
        
        # Mode balancé - ajustement contextuel
        col_hints = self._analyze_column_name(col_name)
        if col_hints['name_likelihood'] > 0.5:
            return base_threshold * 0.9
        
        return base_threshold


def install_spacy_models():
    """Fonction utilitaire pour installer les modèles spaCy nécessaires."""
    
    import subprocess
    import sys
    
    models_to_install = [
        "fr_core_news_sm",  # Modèle français
        "xx_core_web_sm"    # Modèle multilingue
    ]
    
    print("🚀 Installation des modèles spaCy...")
    
    for model in models_to_install:
        try:
            print(f"Installation de {model}...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model])
            print(f"✅ {model} installé avec succès")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation de {model}: {e}")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
    
    print("🏁 Installation terminée. Redémarrez votre application.")


if __name__ == "__main__":
    print("🤖 TEST DU MODULE D'ANONYMISATION AVEC SPACY")
    print("=" * 60)
    
    # Vérifier la disponibilité de spaCy
    print(f"SpaCy disponible: {SPACY_AVAILABLE}")
    print(f"Modèle français: {SPACY_FR_AVAILABLE}")
    print(f"Modèle multilingue: {SPACY_XX_AVAILABLE}")
    
    if not SPACY_AVAILABLE:
        print("\n❌ spaCy n'est pas installé.")
        print("Installation: pip install spacy")
        print("Puis: python -m spacy download fr_core_news_sm")
        print("Et: python -m spacy download xx_core_web_sm")
        
    elif not (SPACY_FR_AVAILABLE or SPACY_XX_AVAILABLE):
        print("\n⚠️ Aucun modèle spaCy disponible.")
        print("Utilisation: install_spacy_models()")
        
    else:
        # Test avec des noms du Maghreb/arabes
        test_names = [
            "Mohamed Ben Ali",
            "mohamed ben ali",  # minuscules
            "Fatima Al-Zahra",
            "fatima al-zahra",  # minuscules
            "Ahmed El Mansouri",
            "Omar Ibn Khaldoun",
            "Aisha Bint Rashid",
            "Tamazight Amellal",  # Berbère
            "J.K. Rowling",
            "Aleksandr Volkov"
        ]
        
        config = SpacyEnhancedAnonymizationConfig(use_spacy=True)
        anonymizer = SpacyEnhancedDataAnonymizer(config)
        
        print("\n🧪 Test de détection avec spaCy:")
        print("-" * 40)
        
        for name in test_names:
            is_name, confidence, reasons = anonymizer.is_name_like_advanced_spacy(name)
            status = "✅ DÉTECTÉ" if is_name else "❌ RATÉ"
            print(f"{status} '{name}' (confiance: {confidence:.3f})")
            print(f"    Raisons: {reasons[:4]}")
            
            # Test spaCy direct
            entities, spacy_conf = anonymizer.analyze_with_spacy(name)
            if entities:
                print(f"    SpaCy: {entities} (conf: {spacy_conf:.2f})")
            print()