"""
Module d'anonymisation des données pour détecter et traiter les informations sensibles.
Supprime les colonnes de noms, numéros de comptes et censure les données sensibles dans les commentaires.
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnonymizationConfig:
    """Configuration pour l'anonymisation des données."""
    name_threshold: float = 0.8  # Seuil pour détecter les colonnes de noms
    min_name_length: int = 2     # Longueur minimale d'un nom
    max_name_length: int = 50    # Longueur maximale d'un nom
    account_patterns: Optional[List[str]] = None  # Patterns pour détecter les numéros de compte
    sensitive_patterns: Optional[List[str]] = None  # Patterns pour détecter les données sensibles
    preserve_data_utility: bool = True   # Conserver l'utilité des données pour l'analyse

    def __post_init__(self):
        if self.account_patterns is None:
            self.account_patterns = [
                r'\b\d{10,}\b',  # Numéros de compte (10+ chiffres)
                r'\b[A-Z]{2}\d{10,}\b',  # Format IBAN-like
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Numéros de carte
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN-like
            ]

        if self.sensitive_patterns is None:
            self.sensitive_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
                r'\b\d{10}\b',  # Téléphones français
                r'\b\d{1,3}[,.]\d{3}[,.]\d{3}[,.]\d{3}\b',  # Numéros avec séparateurs
                r'\b\d{5,}\b',  # Codes postaux ou autres numéros longs
            ]


@dataclass
class AnonymizationReport:
    """Rapport des actions d'anonymisation effectuées."""
    columns_removed: List[str]
    columns_anonymized: List[str]
    sensitive_data_found: Dict[str, int]
    total_rows_processed: int
    total_columns_processed: int


class DataAnonymizer:
    """
    Classe principale pour l'anonymisation des données.

    Détecte et traite automatiquement les informations sensibles dans les DataFrames pandas.
    """

    def __init__(self, config: Optional[AnonymizationConfig] = None):
        """
        Initialise l'anonymiseur avec une configuration.

        Args:
            config: Configuration d'anonymisation (optionnelle)
        """
        self.config = config or AnonymizationConfig()
        self.report = AnonymizationReport([], [], {}, 0, 0)

        # Liste de prénoms et noms français courants pour la détection
        self.french_first_names = self._load_french_names()
        self.french_last_names = self._load_french_last_names()

        logger.info("DataAnonymizer initialisé avec seuil de noms: %.2f", self.config.name_threshold)

    def _load_french_names(self) -> Set[str]:
        """Charge une liste de prénoms français courants."""
        # Prénoms français courants (liste non exhaustive)
        return {
            'marie', 'jean', 'pierre', 'paul', 'jacques', 'michel', 'andre', 'philippe',
            'anne', 'sophie', 'claire', 'emma', 'julie', 'sarah', 'lucas', 'thomas',
            'nicolas', 'antoine', 'camille', 'chloe', 'lea', 'manon', 'oceane', 'ambre',
            'louis', 'gabriel', 'raphael', 'arthur', 'hugo', 'mathis', 'noah', 'adam'
        }

    def _load_french_last_names(self) -> Set[str]:
        """Charge une liste de noms de famille français courants."""
        return {
            'martin', 'bernard', 'durand', 'petit', 'robert', 'richard', 'moreau',
            'simon', 'laurent', 'lefebvre', 'michel', 'garcia', 'david', 'bertrand',
            'roussel', 'vincent', 'fournier', 'morel', 'girard', 'andre', 'lefevre',
            'mercier', 'dupont', 'lambert', 'bonnet', 'francois', 'martinez', 'legrand'
        }

    def is_name_like(self, value: str) -> bool:
        """
        Détermine si une valeur ressemble à un nom.

        Args:
            value: Valeur à tester

        Returns:
            True si la valeur ressemble à un nom
        """
        if not isinstance(value, str) or len(value.strip()) < self.config.min_name_length:
            return False

        value = value.strip().lower()

        # Vérifier la longueur
        if len(value) > self.config.max_name_length:
            return False

        # Vérifier si c'est un prénom ou nom connu
        words = value.split()
        for word in words:
            if word in self.french_first_names or word in self.french_last_names:
                return True

        # Vérifier le pattern des noms (capitales, accents)
        name_pattern = r"^[A-Za-zÀ-ÿ]+(?:[-'\s][A-Za-zÀ-ÿ]+)*$"
        if re.match(name_pattern, value):
            # Vérifier si ça contient des caractères d'accent ou patterns français
            if any(char in value for char in ['é', 'è', 'ê', 'ë', 'à', 'â', 'ô', 'û', 'ù', 'î', 'ï']):
                return True

            # Vérifier la structure (Prénom Nom)
            if len(words) >= 2 and all(len(word) >= 2 for word in words):
                return True

        return False

    def detect_name_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Détecte les colonnes contenant principalement des noms.

        Args:
            df: DataFrame à analyser

        Returns:
            Liste des noms de colonnes identifiées comme contenant des noms
        """
        name_columns = []

        for col in df.columns:
            if df[col].dtype != 'object':
                continue

            # Échantillonner pour les grandes datasets
            sample_size = min(1000, len(df))
            sample = df[col].dropna().sample(n=sample_size, random_state=42) if len(df) > sample_size else df[col].dropna()

            if len(sample) == 0:
                continue

            # Compter les valeurs qui ressemblent à des noms
            name_count = sum(1 for value in sample if self.is_name_like(str(value)))

            # Calculer le ratio
            name_ratio = name_count / len(sample)

            logger.debug(f"Colonne '{col}': {name_ratio:.2%} valeurs ressemblent à des noms ({name_count}/{len(sample)})")

            # Si plus de 80% des valeurs ressemblent à des noms, considérer comme colonne de noms
            if name_ratio >= self.config.name_threshold:
                name_columns.append(col)
                logger.info(f"Colonne '{col}' détectée comme colonne de noms (ratio: {name_ratio:.2%})")

        return name_columns

    def detect_account_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Détecte les colonnes contenant des numéros de compte ou données financières sensibles.

        Args:
            df: DataFrame à analyser

        Returns:
            Liste des noms de colonnes identifiées comme contenant des numéros de compte
        """
        account_columns = []

        for col in df.columns:
            if df[col].dtype not in ['object', 'int64', 'float64']:
                continue

            # Convertir en string pour l'analyse
            string_values = df[col].astype(str).str.strip()

            # Compter les valeurs qui correspondent aux patterns de comptes
            sensitive_count = 0

            # S'assurer que les patterns sont disponibles
            account_patterns = self.config.account_patterns or []
            for pattern in account_patterns:
                matches = string_values.str.contains(pattern, regex=True, na=False)
                sensitive_count += matches.sum()

            # Si plus de 30% des valeurs correspondent à des patterns sensibles
            if len(string_values) > 0:
                sensitive_ratio = sensitive_count / len(string_values)

                if sensitive_ratio > 0.3:  # Seuil plus bas car les numéros de compte sont plus rares
                    account_columns.append(col)
                    logger.info(f"Colonne '{col}' détectée comme contenant des numéros de compte (ratio: {sensitive_ratio:.2%})")

        return account_columns

    def process_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Traite les colonnes de texte pour censurer les informations sensibles.

        Args:
            df: DataFrame à traiter

        Returns:
            DataFrame avec les colonnes de texte anonymisées
        """
        df_processed = df.copy()
        text_columns = df.select_dtypes(include=['object']).columns

        for col in text_columns:
            if df[col].dtype != 'object':
                continue

            # Vérifier si la colonne contient principalement du texte long (commentaires)
            avg_length = df[col].astype(str).str.len().mean()
            if avg_length > 50:  # Colonnes avec texte long = probablement des commentaires
                logger.info(f"Traitement de la colonne de commentaires '{col}' (longueur moyenne: {avg_length:.0f})")

                df_processed[col] = df[col].astype(str).apply(self._censor_sensitive_text)

        return df_processed

    def _censor_sensitive_text(self, text: str) -> str:
        """
        Censure les informations sensibles dans un texte.

        Args:
            text: Texte à censurer

        Returns:
            Texte avec les informations sensibles censurées
        """
        if not isinstance(text, str):
            return text

        censored_text = text

        # Censurer les emails
        censored_text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_CENSURE]',
            censored_text
        )

        # Censurer les téléphones
        censored_text = re.sub(
            r'\b\d{10}\b',
            '[TELEPHONE_CENSURE]',
            censored_text
        )

        # Censurer les numéros de compte
        account_patterns = self.config.account_patterns or []
        for pattern in account_patterns:
            censored_text = re.sub(pattern, '[NUMERO_COMPTE_CENSURE]', censored_text)

        # Censurer les noms propres (si détectés dans le texte)
        words = censored_text.split()
        censored_words = []

        for word in words:
            if self.is_name_like(word):
                # Remplacer par un nom générique
                censored_words.append('[NOM_CENSURE]')
            else:
                censored_words.append(word)

        return ' '.join(censored_words)

    def anonymize_dataframe(self, df: pd.DataFrame, preserve_utility: bool = True) -> Tuple[pd.DataFrame, AnonymizationReport]:
        """
        Anonymise un DataFrame en supprimant les colonnes sensibles et en traitant les textes.

        Args:
            df: DataFrame à anonymiser
            preserve_utility: Conserver l'utilité des données pour l'analyse

        Returns:
            Tuple (DataFrame anonymisé, rapport d'anonymisation)
        """
        logger.info(f"Début de l'anonymisation de {len(df)} lignes, {len(df.columns)} colonnes")

        # Réinitialiser le rapport
        self.report = AnonymizationReport([], [], {}, len(df), len(df.columns))

        df_anonymized = df.copy()

        # 1. Détecter et supprimer les colonnes de noms
        name_columns = self.detect_name_columns(df)
        if name_columns:
            df_anonymized = df_anonymized.drop(columns=name_columns)
            self.report.columns_removed.extend(name_columns)
            logger.info(f"Colonnes de noms supprimées: {name_columns}")

        # 2. Détecter et supprimer les colonnes de numéros de compte
        account_columns = self.detect_account_columns(df)
        if account_columns:
            df_anonymized = df_anonymized.drop(columns=account_columns)
            self.report.columns_removed.extend(account_columns)
            logger.info(f"Colonnes de comptes supprimées: {account_columns}")

        # 3. Traiter les colonnes de texte
        if preserve_utility:
            df_anonymized = self.process_text_fields(df_anonymized)

        # 4. Générer le rapport final
        self.report.total_rows_processed = len(df_anonymized)
        self.report.total_columns_processed = len(df_anonymized.columns)

        logger.info(f"Anonymisation terminée: {len(self.report.columns_removed)} colonnes supprimées, "
                   f"{len(df_anonymized.columns)} colonnes restantes")

        return df_anonymized, self.report

    def get_anonymization_report(self) -> AnonymizationReport:
        """Retourne le dernier rapport d'anonymisation."""
        return self.report

    def preview_anonymization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Prévisualise les actions d'anonymisation sans les appliquer.

        Args:
            df: DataFrame à analyser

        Returns:
            Dictionnaire avec les colonnes qui seraient supprimées/modifiées
        """
        name_columns = self.detect_name_columns(df)
        account_columns = self.detect_account_columns(df)

        # Analyser les colonnes de texte
        text_columns = df.select_dtypes(include=['object']).columns
        text_analysis = {}

        for col in text_columns:
            if df[col].dtype == 'object':
                avg_length = df[col].astype(str).str.len().mean()
                if avg_length > 50:
                    # Compter les patterns sensibles
                    sample_text = df[col].astype(str).dropna().head(10)
                    sensitive_count = 0

                    for text in sample_text:
                        sensitive_patterns = self.config.sensitive_patterns or []
                        for pattern in sensitive_patterns:
                            if re.search(pattern, text):
                                sensitive_count += 1
                                break

                    text_analysis[col] = {
                        'avg_length': avg_length,
                        'sensitive_patterns_found': sensitive_count,
                        'would_be_processed': True
                    }

        return {
            'name_columns': name_columns,
            'account_columns': account_columns,
            'text_columns_to_process': text_analysis,
            'total_columns_to_remove': len(name_columns) + len(account_columns),
            'remaining_columns': len(df.columns) - len(name_columns) - len(account_columns)
        }


def anonymize_csv_file(file_path: str, output_path: Optional[str] = None,
                      config: Optional[AnonymizationConfig] = None) -> Tuple[bool, str]:
    """
    Anonymise un fichier CSV et sauvegarde le résultat.

    Args:
        file_path: Chemin vers le fichier CSV d'origine
        output_path: Chemin de sortie (optionnel)
        config: Configuration d'anonymisation

    Returns:
        Tuple (succès, message)
    """
    try:
        # Charger le fichier
        df = pd.read_csv(file_path)
        logger.info(f"Fichier chargé: {file_path} ({len(df)} lignes)")

        # Anonymiser
        anonymizer = DataAnonymizer(config)
        df_anonymized, report = anonymizer.anonymize_dataframe(df)

        # Déterminer le chemin de sortie
        if output_path is None:
            base_name = file_path.rsplit('.', 1)[0]
            output_path = f"{base_name}_anonymized.csv"

        # Sauvegarder
        df_anonymized.to_csv(output_path, index=False)
        logger.info(f"Fichier anonymisé sauvegardé: {output_path}")

        # Message de succès
        message = f"""
        Anonymisation réussie:
        - Colonnes supprimées: {len(report.columns_removed)}
        - Colonnes restantes: {report.total_columns_processed}
        - Lignes traitées: {report.total_rows_processed}
        """

        return True, message

    except Exception as e:
        error_msg = f"Erreur lors de l'anonymisation: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


if __name__ == "__main__":
    # Test du module d'anonymisation
    print("🛡️ Test du module d'anonymisation")
    print("=" * 50)

    # Créer des données de test avec des informations sensibles
    test_data = pd.DataFrame({
        'client_id': ['C001', 'C002', 'C003'],
        'nom_complet': ['Marie Martin', 'Jean Dupont', 'Sophie Bernard'],
        'email': ['marie@email.com', 'jean@email.com', 'sophie@email.com'],
        'telephone': ['0123456789', '0987654321', '0112233445'],
        'numero_compte': ['FR1420041010050500013M02606', '123456789012', '987654321098'],
        'commentaire': [
            'Client très satisfait du service. Email: marie@email.com, Tel: 0123456789',
            'Problème résolu rapidement par téléphone',
            'Merci pour l\'aide apportée'
        ],
        'montant': [150.50, 230.75, 89.90],
        'date': ['2024-01-15', '2024-01-16', '2024-01-17']
    })

    print("Données originales:")
    print(test_data)
    print()

    # Tester l'anonymisation
    anonymizer = DataAnonymizer()
    preview = anonymizer.preview_anonymization(test_data)

    print("Analyse d'anonymisation:")
    print(f"Colonnes de noms détectées: {preview['name_columns']}")
    print(f"Colonnes de comptes détectées: {preview['account_columns']}")
    print(f"Colonnes de texte à traiter: {list(preview['text_columns_to_process'].keys())}")
    print()

    # Appliquer l'anonymisation
    df_anonymized, report = anonymizer.anonymize_dataframe(test_data)

    print("Données anonymisées:")
    print(df_anonymized)
    print()

    print("Rapport d'anonymisation:")
    print(f"Colonnes supprimées: {report.columns_removed}")
    print(f"Colonnes restantes: {report.total_columns_processed}")
    print(f"Lignes traitées: {report.total_rows_processed}")
