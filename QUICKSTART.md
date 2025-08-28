# 🚀 Guide de Démarrage Rapide

## Étapes d'Installation et Configuration

### 1. Configuration de l'Environnement

Copiez le fichier de configuration exemple :
```bash
copy .env.example .env
```

Éditez le fichier `.env` et ajoutez votre clé API OpenAI :
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Installation des Dépendances

Les dépendances sont déjà installées dans l'environnement conda configuré.

### 3. Démarrage de l'Application

**Option 1 - Script Batch (Windows) :**
```bash
start.bat
```

**Option 2 - Script PowerShell :**
```powershell
.\start.ps1
```

**Option 3 - Commande directe :**
```bash
streamlit run app.py
```

### 4. Accès à l'Application

Ouvrez votre navigateur sur : **http://localhost:8501**

## 🎯 Premier Test

### Charger des données d'exemple

1. Dans la sidebar, cliquez sur "Choisissez un fichier"
2. Sélectionnez le fichier `data/exemple_ventes.csv`
3. Cliquez sur "📤 Charger le fichier"

### Questions d'exemple à poser

```
📊 Questions d'analyse :
- "Montre-moi un résumé des données"
- "Quels sont les vendeurs les plus performants ?"
- "Quel est le chiffre d'affaires total par région ?"

📈 Demandes de visualisation :
- "Crée un graphique des ventes par produit"
- "Montre l'évolution des ventes dans le temps" 
- "Fais un histogramme des prix unitaires"
```

## 🔧 Configuration Avancée

### Variables d'environnement importantes

```env
# Seuil du cache sémantique (0.0 à 1.0)
SEMANTIC_CACHE_THRESHOLD=0.85

# Modèle LLM à utiliser
LLM_MODEL=gpt-3.5-turbo

# Modèle d'embedding
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Personnalisation de l'interface

Modifiez le fichier `.streamlit/config.toml` pour changer :
- Couleurs du thème
- Port d'écoute
- Taille maximale des fichiers

## 🆘 Dépannage

### Erreur : "Clé API manquante"
- Vérifiez que votre fichier `.env` existe
- Assurez-vous que la clé API OpenAI est correcte

### Erreur : "Module non trouvé"
- Réinstallez les dépendances avec : `pip install -r requirements.txt`

### Erreur : "Port déjà utilisé"
- Changez le port dans `.streamlit/config.toml`
- Ou utilisez : `streamlit run app.py --server.port 8502`

### Performance lente
- Réduisez `SEMANTIC_CACHE_THRESHOLD` pour plus de cache hits
- Utilisez des fichiers plus petits (<10MB)

## 📚 Ressources

- **Documentation complète** : Voir `README.md`
- **Exemples de données** : Dossier `data/`
- **Configuration** : Fichier `.env`

---

**🎉 Félicitations ! Votre agent IA est maintenant opérationnel !**
