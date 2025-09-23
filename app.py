"""
Interface utilisateur Streamlit pour l'agent IA d'analyse de données.
Interface moderne et intuitive pour l'interaction en langage naturel.
"""

import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from typing import List
import logging

# Configuration de la page
st.set_page_config(
    page_title="Agent IA Local - Analyse de Données",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports des composants
from src.components.data_manager import DataManager
from src.components.simple_cache import SimpleCache
from src.components.ai_agent import LocalAIAgent
from src.utils.data_generator import DataGenerator
from src.utils.example_prompts import ExamplePrompts

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Configuration globale (sans OpenAI)
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
SEMANTIC_CACHE_THRESHOLD = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.85"))
CACHE_DIR = os.getenv("FAISS_INDEX_PATH", "./cache")


@st.cache_resource
def initialize_components():
    """Initialise les composants de l'application (mise en cache)."""
    try:
        # Initialiser les composants locaux
        data_manager = DataManager(db_path=CHROMA_DB_PATH)
        simple_cache = SimpleCache(
            cache_dir=CACHE_DIR
        )
        
        # Agent IA local (sans OpenAI)
        ai_agent = LocalAIAgent(
            data_manager=data_manager,
            simple_cache=simple_cache
        )
        
        return data_manager, simple_cache, ai_agent
    
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation: {e}")
        st.stop()


def main():
    """Fonction principale de l'application Streamlit."""
    _setup_page_header()
    
    # Initialiser les composants
    _, simple_cache, ai_agent = initialize_components()
    
    # Sidebar pour la gestion des fichiers
    uploaded_files = _setup_sidebar()
    
    # Traitement des fichiers uploadés
    if uploaded_files:
        _process_uploaded_files(uploaded_files, ai_agent)
    
    # Interface de chat
    _setup_chat_interface(simple_cache, ai_agent)

def _setup_page_header():
    """Configurer le titre et la description de la page."""
    st.title("🤖 Agent IA Local - Analyse de Données")
    st.markdown("Analysez vos données avec l'intelligence artificielle en langage naturel.")

def _setup_sidebar() -> List:
    """Configurer la barre latérale avec téléchargement de fichiers et configuration."""
    st.sidebar.header("📁 Configuration")
    st.sidebar.markdown("Téléchargez vos fichiers de données (CSV, Excel)")
    
    return st.sidebar.file_uploader(
        "Choisir des fichiers",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True
    )

def _process_uploaded_files(uploaded_files: List, ai_agent) -> None:
    """Traiter et indexer les fichiers uploadés."""
    success_count = 0
    
    with st.spinner("Traitement des fichiers..."):
        for file in uploaded_files:
            try:
                if _index_file(file, ai_agent):
                    success_count += 1
            except Exception as e:
                st.error(f"Erreur avec {file.name}: {str(e)}")
    
    if success_count > 0:
        st.success(f"{success_count} fichier(s) traité(s) avec succès!")

def _index_file(file, ai_agent) -> bool:
    """Indexer un seul fichier avec l'agent IA."""
    try:
        # Sauvegarder le fichier temporairement
        temp_path = f"temp_{file.name}"
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        
        # Indexer le fichier
        ai_agent.index_data(temp_path)
        return True
        
    except Exception as e:
        st.error(f"Erreur lors de l'indexation: {str(e)}")
        return False

def _setup_chat_interface(simple_cache, ai_agent) -> None:
    """Configurer et gérer l'interface de chat."""
    st.header("💬 Chat avec vos données")
    
    # Initialiser l'historique de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Afficher l'historique des messages
    _display_chat_history()
    
    # Gérer les nouvelles questions des utilisateurs
    if user_question := st.chat_input("Posez votre question sur les données..."):
        _handle_user_question(user_question, simple_cache, ai_agent)

def _display_chat_history() -> None:
    """Afficher les messages de chat existants."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "chart_path" in message:
                _display_chart_with_download(message["chart_path"])

def _handle_user_question(question: str, simple_cache, ai_agent) -> None:
    """Traiter la question de l'utilisateur et générer une réponse."""
    # Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": question})
    
    with st.chat_message("user"):
        st.markdown(question)
    
    # Générer la réponse de l'IA
    with st.chat_message("assistant"):
        with st.spinner("Réflexion..."):
            response_data = _get_ai_response(question, simple_cache, ai_agent)
            _display_ai_response(response_data)

def _get_ai_response(question: str, simple_cache, ai_agent) -> dict:
    """Obtenir une réponse de l'agent IA avec mise en cache."""
    try:
        # Vérifier le cache en premier
        cached_response = simple_cache.get_similar_response(question)
        if cached_response:
            return {
                "content": cached_response,
                "source": "cache",
                "chart_path": None
            }
        
        # Obtenir une nouvelle réponse de l'IA
        response = ai_agent.process_query(question)
        simple_cache.add_response(question, response)
        
        return {
            "content": response,
            "source": "ai",
            "chart_path": _extract_chart_path(response)
        }
        
    except Exception as e:
        return {
            "content": f"Erreur lors du traitement: {str(e)}",
            "source": "error",
            "chart_path": None
        }

def _display_ai_response(response_data: dict) -> None:
    """Afficher la réponse de l'IA avec un formatage approprié."""
    st.markdown(response_data["content"])
    
    # Ajouter un indicateur de source
    source_emoji = {"cache": "🔄", "ai": "🤖", "error": "❌"}
    st.caption(f"{source_emoji.get(response_data['source'], '❓')} Source: {response_data['source']}")
    
    # Afficher le graphique si disponible
    if response_data["chart_path"]:
        _display_chart_with_download(response_data["chart_path"])
    
    # Sauvegarder dans l'état de la session
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_data["content"],
        "chart_path": response_data["chart_path"]
    })

def _extract_chart_path(response: str) -> str | None:
    """Extraire le chemin du graphique de la réponse de l'IA si présent."""
    # L'implémentation dépend de la façon dont votre agent IA renvoie les chemins de graphique
    # Ceci est un espace réservé - ajustez en fonction de votre format réel
    if "exports/" in response:
        import re
        match = re.search(r'exports/[^\s]+\.png', response)
        return match.group(0) if match else None
    return None

def _display_chart_with_download(chart_path: str) -> None:
    """Afficher le graphique avec un bouton de téléchargement."""
    try:
        st.image(chart_path, caption="Graphique généré")
        
        with open(chart_path, "rb") as file:
            st.download_button(
                label="📥 Télécharger le graphique",
                data=file.read(),
                file_name=chart_path.split("/")[-1],
                mime="image/png"
            )
    except Exception as e:
        st.error(f"Erreur d'affichage du graphique: {str(e)}")


def show_data_preview():
    """Affiche un aperçu des données chargées."""
    data_manager, _, ai_agent = initialize_components()
    
    summary = ai_agent.get_data_summary()
    if 'message' not in summary:
        st.subheader("📋 Aperçu des Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Nombre de lignes", f"{summary['shape'][0]:,}")
            st.metric("Nombre de colonnes", summary['shape'][1])
        
        with col2:
            missing_total = sum(summary['missing_values'].values())
            st.metric("Valeurs manquantes", f"{missing_total:,}")
        
        # Afficher les types de colonnes
        st.subheader("🏷️ Types de Colonnes")
        dtypes_df = pd.DataFrame(list(summary['dtypes'].items()), 
                                columns=['Colonne', 'Type'])
        st.dataframe(dtypes_df, use_container_width=True)
        
        # Échantillon de données
        st.subheader("👁️ Échantillon de Données")
        sample_df = pd.DataFrame(summary['sample'])
        st.dataframe(sample_df, use_container_width=True)


# Interface de navigation par onglets
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Aperçu Données", "⚙️ Configuration"])

with tab1:
    # Le contenu principal est déjà affiché
    pass

with tab2:
    show_data_preview()

with tab3:
    st.header("⚙️ Configuration")
    
    # Statistiques générales
    data_manager, simple_cache, ai_agent = initialize_components()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Statistiques ChromaDB")
        db_stats = data_manager.get_stats()
        st.json(db_stats)
    
    with col2:
        st.subheader("🧠 Statistiques Cache")
        cache_stats = simple_cache.get_stats()
        st.json(cache_stats)
    
    with col3:
        st.subheader("📈 Visualisations")
        viz_stats = ai_agent.get_viz_stats()
        st.json(viz_stats)
    
    # Information sur l'architecture locale
    st.subheader("🏠 Architecture Locale")
    st.success("✅ **Agent IA 100% Local**")
    st.info("🎯 **Chatbot à arbre de décision** : Logique déterministe pour analyser les requêtes")
    st.info("💾 **ChromaDB** : Base de données vectorielle locale pour données et visualisations")
    st.info("🧠 **Cache FAISS** : Cache sémantique intelligent pour optimiser les réponses")
    st.info("📊 **Visualisations Seaborn** : Graphiques générés et stockés localement")
    
    # Boutons d'administration
    st.subheader("🔧 Administration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Réinitialiser la base de données"):
            if st.checkbox("Confirmer la réinitialisation"):
                data_manager.reset_database()
                st.success("Base de données réinitialisée !")
    
    with col2:
        if st.button("🧹 Vider le cache simple"):
            simple_cache.clear()
            st.success("Cache simple vidé !")
    
    with col3:
        if st.button("📝 Effacer l'historique de chat"):
            st.session_state.messages = []
            st.success("Historique effacé !")


if __name__ == "__main__":
    main()
