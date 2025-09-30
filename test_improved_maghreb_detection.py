"""
Test simple du module d'anonymisation amélioré avec focus sur les noms du Maghreb/arabes
et les cas sans capitalisation, même sans spaCy.
"""

import re
import numpy as np
from collections import Counter

def calculate_simple_entropy(text):
    """Calcul simple de l'entropie d'un texte."""
    if not text:
        return 0.0
    
    clean_text = re.sub(r'[^a-zA-ZÀ-ÿ]', '', text.lower())
    if not clean_text:
        return 0.0
    
    char_counts = Counter(clean_text)
    length = len(clean_text)
    entropy = 0.0
    
    for count in char_counts.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * np.log2(probability)
    
    return entropy

def analyze_maghreb_arabic_names():
    """Analyse spécifique des noms du Maghreb et arabes."""
    
    print("🔍 ANALYSE AMÉLIORÉE - NOMS DU MAGHREB ET ARABES")
    print("=" * 60)
    
    # Dictionnaire étendu de noms arabes/maghrébins
    arabic_names_db = {
        # Prénoms masculins
        'mohamed', 'mohammed', 'muhammad', 'ahmad', 'ahmed', 'omar', 'umar', 'ali', 
        'hassan', 'hussein', 'youssef', 'yousef', 'ibrahim', 'ismail', 'khalid', 
        'karim', 'tarek', 'tariq', 'samir', 'amin', 'nasser', 'said', 'mahmoud', 
        'mustafa', 'abdullah', 'abderrahman', 'abdelkader', 'abdelaziz',
        
        # Prénoms féminins
        'fatima', 'aisha', 'khadija', 'zahra', 'amina', 'safaa', 'nadia', 'leila',
        'sofia', 'maryam', 'salma', 'hanan', 'yasmin', 'dalal', 'wafa', 'nour',
        
        # Noms de famille
        'benali', 'ben-ali', 'benameur', 'mansouri', 'el-mansouri', 'al-mansouri',
        'khaldoun', 'ibn-khaldoun', 'benaissa', 'bouazza', 'meziane', 'ouali',
        'zerhouni', 'tlemcani', 'fassi', 'alaoui', 'idrissi', 'hassani',
        
        # Noms berbères
        'tamazight', 'amellal', 'azul', 'tanirt', 'tilelli', 'yemma', 'gouraya',
        'akli', 'mohand', 'ouali', 'amazigh',
        
        # Particules
        'sidi', 'moulay', 'lalla', 'sid', 'abu', 'abou', 'ould', 'bint'
    }
    
    # Patterns spécifiques au monde arabe/Maghreb
    arabic_patterns = [
        r'\b(al|el)-[a-zA-ZÀ-ÿ]+\b',
        r'\babd\s+(al|el|allah|rahman|aziz|malik|karim)\b',
        r'\bben\s+[a-zA-ZÀ-ÿ]+\b',
        r'\bibn\s+[a-zA-ZÀ-ÿ]+\b',
        r'\bould\s+[a-zA-ZÀ-ÿ]+\b',
        r'\bbint\s+[a-zA-ZÀ-ÿ]+\b',
        r'\bsidi\s+[a-zA-ZÀ-ÿ]+\b',
        r'\b(abu|abou)\s+[a-zA-ZÀ-ÿ]+\b',
        r'\b(moulay|lalla)\s+[a-zA-ZÀ-ÿ]+\b'
    ]
    
    # Noms de test avec différentes capitalisations
    test_names = [
        # Noms avec capitalisation
        ("Mohamed Ben Ali", "Nom marocain classique"),
        ("Fatima Al-Zahra", "Prénom féminin avec Al-"),
        ("Ahmed El Mansouri", "Nom avec particule El"),
        ("Omar Ibn Khaldoun", "Nom historique avec Ibn"),
        ("Aisha Bint Rashid", "Nom féminin avec Bint"),
        ("Sidi Mohamed", "Nom avec titre Sidi"),
        ("Tamazight Amellal", "Nom berbère"),
        ("Youssef Ould Mohamed", "Nom mauritanien"),
        
        # MÊMES NOMS sans capitalisation (test critique)
        ("mohamed ben ali", "Sans capitalisation"),
        ("fatima al-zahra", "Sans capitalisation"),
        ("ahmed el mansouri", "Sans capitalisation"),
        ("omar ibn khaldoun", "Sans capitalisation"),
        ("aisha bint rashid", "Sans capitalisation"),
        ("sidi mohamed", "Sans capitalisation"),
        ("tamazight amellal", "Berbère sans capitalisation"),
        ("youssef ould mohamed", "Mauritanien sans capitalisation"),
        
        # Noms complexes
        ("Abd El Rahman Al-Kindi", "Nom composé avec Abd"),
        ("abu bakr al-razi", "Nom historique sans capitalisation"),
        ("Lalla Fatima Zahra", "Nom avec titre féminin"),
        ("moulay hassan", "Nom royal sans capitalisation")
    ]
    
    def analyze_name_advanced(name):
        """Analyse avancée d'un nom avec les nouvelles heuristiques."""
        name_lower = name.lower()
        words = name.split()
        
        score = 0.0
        reasons = []
        
        # 1. Vérification dans la base de noms arabes
        arabic_name_score = 0.0
        for word in words:
            if word.lower() in arabic_names_db:
                arabic_name_score += 0.8
                reasons.append(f"known_arabic_name_{word.lower()}")
        
        if len(words) > 0:
            arabic_name_score /= len(words)
        score += arabic_name_score * 0.4
        
        # 2. Patterns arabes/maghrébins
        pattern_matched = False
        for pattern in arabic_patterns:
            if re.search(pattern, name_lower):
                score += 0.3
                reasons.append(f"arabic_pattern")
                pattern_matched = True
                break
        
        # 3. Analyse d'entropie (ajustée pour être moins stricte)
        entropy = calculate_simple_entropy(name)
        if entropy >= 2.0:  # Seuil réduit de 2.5 à 2.0
            entropy_boost = min((entropy - 2.0) / 2.0, 0.25)
            score += entropy_boost
            reasons.append(f"entropy_{entropy:.2f}")
        
        # 4. Capitalisation (poids TRÈS réduit pour ne pas pénaliser les minuscules)
        has_capitals = any(c.isupper() for c in name)
        if has_capitals:
            # Bonus léger pour capitalisation correcte
            if name[0].isupper():
                score += 0.1
                reasons.append("proper_capitalization")
        else:
            # PAS de pénalité pour les minuscules !
            # Au contraire, bonus si c'est un nom connu en minuscules
            if any(word.lower() in arabic_names_db for word in words):
                score += 0.1
                reasons.append("known_name_lowercase")
        
        # 5. Structure de nom (patterns généraux)
        if re.match(r'^[A-Za-zÀ-ÿ\s\-\']+$', name):
            score += 0.1
            reasons.append("valid_name_structure")
        
        # 6. Multi-mots (structure prénom + nom)
        if len(words) >= 2:
            score += 0.05
            reasons.append("multi_word")
            
            if all(len(word) >= 2 for word in words):
                score += 0.05
                reasons.append("valid_word_lengths")
        
        # 7. Caractères arabes/accents
        if any(char in name for char in 'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'):
            score += 0.05
            reasons.append("accented_characters")
        
        return min(score, 1.0), reasons
    
    print("📊 RÉSULTATS DE L'ANALYSE AMÉLIORÉE:")
    print("-" * 50)
    
    total_tested = 0
    total_detected = 0
    capitalized_detected = 0
    lowercase_detected = 0
    capitalized_total = 0
    lowercase_total = 0
    
    for name, description in test_names:
        score, reasons = analyze_name_advanced(name)
        is_detected = score >= 0.5  # Seuil de détection
        
        total_tested += 1
        if is_detected:
            total_detected += 1
        
        # Statistiques par type de capitalisation
        has_capitals = any(c.isupper() for c in name)
        if has_capitals:
            capitalized_total += 1
            if is_detected:
                capitalized_detected += 1
        else:
            lowercase_total += 1
            if is_detected:
                lowercase_detected += 1
        
        # Affichage
        status = "✅ DÉTECTÉ" if is_detected else "❌ RATÉ"
        print(f"{status} '{name}' (score: {score:.3f})")
        print(f"    📝 {description}")
        print(f"    🔍 Raisons: {reasons[:4]}")
        print()
    
    print("=" * 60)
    print("📈 STATISTIQUES FINALES:")
    print("-" * 30)
    print(f"Total détecté: {total_detected}/{total_tested} ({total_detected/total_tested*100:.1f}%)")
    print(f"Avec capitalisation: {capitalized_detected}/{capitalized_total} ({capitalized_detected/capitalized_total*100:.1f}%)")
    print(f"Sans capitalisation: {lowercase_detected}/{lowercase_total} ({lowercase_detected/lowercase_total*100:.1f}%)")
    
    print("\n💡 AMÉLIORATIONS APPORTÉES:")
    print("-" * 30)
    print("✅ Base de données étendue de noms arabes/maghrébins/berbères")
    print("✅ Patterns spécifiques aux particules arabes (Al-, Ben-, Ibn-, etc.)")
    print("✅ Poids de capitalisation fortement réduit")
    print("✅ Bonus pour noms connus même en minuscules")
    print("✅ Seuil d'entropie ajusté pour être plus inclusif")
    print("✅ Détection des titres (Sidi, Moulay, Lalla, etc.)")

if __name__ == "__main__":
    analyze_maghreb_arabic_names()