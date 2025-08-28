# Contributing to AI Data Interaction Agent

Merci de votre intérêt pour contribuer à ce projet ! 🚀

## Comment Contribuer

### 🐛 Signaler un Bug
1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](https://github.com/ChristopheAmoussouvi/CacheSemantic/issues)
2. Créez une nouvelle issue avec :
   - Description claire du problème
   - Étapes pour reproduire
   - Comportement attendu vs actuel
   - Informations sur votre environnement

### 💡 Proposer une Fonctionnalité
1. Créez une issue avec le label "enhancement"
2. Décrivez clairement la fonctionnalité souhaitée
3. Expliquez pourquoi cette fonctionnalité serait utile

### 🔧 Contribuer au Code
1. **Fork** le repository
2. Créez une branche pour votre fonctionnalité : `git checkout -b feature/ma-fonctionnalite`
3. Implémentez vos changements
4. Ajoutez des tests si nécessaire
5. Assurez-vous que tous les tests passent : `python validate.py`
6. Committez vos changements : `git commit -m "feat: description de la fonctionnalité"`
7. Poussez vers votre fork : `git push origin feature/ma-fonctionnalite`
8. Créez une **Pull Request**

## Standards de Code

### Style de Code
- Suivez les conventions PEP 8 pour Python
- Utilisez des type hints
- Documentez vos fonctions avec des docstrings
- Gardez les fonctions courtes et focalisées

### Messages de Commit
Utilisez les conventions suivantes :
- `feat:` pour une nouvelle fonctionnalité
- `fix:` pour une correction de bug
- `docs:` pour la documentation
- `style:` pour le formatage
- `refactor:` pour la refactorisation
- `test:` pour les tests
- `chore:` pour les tâches de maintenance

### Tests
- Ajoutez des tests pour toute nouvelle fonctionnalité
- Assurez-vous que tous les tests existants passent
- Visez une couverture de code élevée

## Structure du Projet

```
ChatPOC2/
├── src/components/          # Composants principaux
│   ├── semantic_cache.py   # Cache sémantique FAISS
│   ├── data_manager.py     # Gestionnaire ChromaDB
│   └── ai_agent.py         # Agent IA LangChain
├── app.py                  # Interface Streamlit
├── validate.py             # Tests de validation
└── README.md               # Documentation
```

## Environnement de Développement

1. **Cloner le repository** :
```bash
git clone https://github.com/ChristopheAmoussouvi/CacheSemantic.git
cd CacheSemantic
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Configurer l'environnement** :
```bash
cp .env.example .env
# Éditer .env avec votre clé API OpenAI
```

4. **Valider l'installation** :
```bash
python validate.py
```

5. **Lancer l'application** :
```bash
streamlit run app.py
```

## Questions ?

N'hésitez pas à :
- Créer une issue pour toute question
- Rejoindre les discussions
- Proposer des améliorations

Merci de contribuer à rendre cet outil encore meilleur ! 🙏
