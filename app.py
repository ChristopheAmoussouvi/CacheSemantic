"""
Interface utilisateur Streamlit pour l'agent IA d'analyse de données.
Interface moderne et intuitive pour l'interaction en langage naturel.
"""

import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configuration de la page
st.set_page_config(
    page_title="Agent IA - Analyse de Données",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports des composants
from src.components.data_manager import DataManager
from src.components.semantic_cache import SemanticCache
from src.components.ai_agent import AIAgent

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Configuration globale
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
SEMANTIC_CACHE_THRESHOLD = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.85"))
CACHE_DIR = os.getenv("FAISS_INDEX_PATH", "./cache")


@st.cache_resource
def initialize_components():
    """Initialise les composants de l'application (mise en cache)."""
    try:
        # Initialiser les composants
        data_manager = DataManager(db_path=CHROMA_DB_PATH)
        semantic_cache = SemanticCache(
            threshold=SEMANTIC_CACHE_THRESHOLD,
            cache_dir=CACHE_DIR
        )
        
        if not OPENAI_API_KEY:
            st.error("⚠️ Clé API OpenAI manquante. Veuillez configurer votre fichier .env")
            st.stop()
        
        ai_agent = AIAgent(
            openai_api_key=OPENAI_API_KEY,
            data_manager=data_manager,
            semantic_cache=semantic_cache
        )
        
        return data_manager, semantic_cache, ai_agent
    
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation: {e}")
        st.stop()


def main():
    """Fonction principale de l'application Streamlit."""
    
    # Titre de l'application
    st.title("🤖 Agent IA - Analyse de Données")
    st.markdown("""
    **Interagissez avec vos données en langage naturel**  
    Chargez vos fichiers CSV ou Excel et posez des questions en français !
    """)
    
    # Initialiser les composants
    data_manager, semantic_cache, ai_agent = initialize_components()
    
    # Sidebar pour la gestion des fichiers
    with st.sidebar:
        st.header("📁 Gestion des Fichiers")
        
        # Upload de fichier
        uploaded_file = st.file_uploader(
            "Choisissez un fichier CSV ou Excel",
            type=['csv', 'xlsx', 'xls'],
            help="Formats supportés: CSV, XLSX, XLS"
        )
        
        # Traitement du fichier uploadé
        if uploaded_file is not None:
            if st.button("📤 Charger le fichier"):
                with st.spinner("Chargement et indexation du fichier..."):
                    # Sauvegarder le fichier temporairement
                    temp_path = f"./data/{uploaded_file.name}"
                    os.makedirs("./data", exist_ok=True)
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Charger dans ChromaDB
                    success_db = data_manager.load_data_file(temp_path)
                    
                    # Charger pour l'analyse pandas
                    success_agent = ai_agent.load_data_for_analysis(temp_path)
                    
                    if success_db and success_agent:
                        st.success(f"✅ Fichier '{uploaded_file.name}' chargé avec succès!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Erreur lors du chargement du fichier")
        
        # Affichage des fichiers chargés
        st.subheader("📊 Fichiers Chargés")
        files_info = data_manager.get_file_info()
        
        if files_info:
            for file_id, info in files_info.items():
                with st.expander(f"📄 {info['file_name']}"):
                    st.write(f"**Lignes:** {info['num_rows']:,}")
                    st.write(f"**Colonnes:** {info['num_cols']}")
                    st.write("**Colonnes disponibles:**")
                    st.write(", ".join(info['columns']))
                    
                    if st.button(f"🗑️ Supprimer", key=f"delete_{file_id}"):
                        data_manager.remove_file(file_id)
                        st.success(f"Fichier {info['file_name']} supprimé")
                        st.experimental_rerun()
        else:
            st.info("Aucun fichier chargé")
        
        # Statistiques du cache
        st.subheader("🧠 Cache Sémantique")
        cache_stats = semantic_cache.get_stats()
        st.metric("Entrées en cache", cache_stats['total_entries'])
        st.metric("Seuil de similarité", f"{cache_stats['threshold']:.2f}")
        
        if st.button("🧹 Vider le cache"):
            semantic_cache.clear()
            st.success("Cache vidé !")
    
    # Interface de chat principale
    st.header("💬 Chat avec vos Données")
    
    # Initialiser l'historique de chat dans la session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Afficher la visualisation si présente
            if "visualization" in message:
                display_visualization(message["visualization"])
    
    # Interface de saisie
    if prompt := st.chat_input("Posez votre question sur les données..."):
        # Ajouter le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Traiter la requête
        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                result = ai_agent.process_query(prompt)
                
                # Afficher la réponse
                st.markdown(result['response'])
                
                # Afficher la source
                source_emoji = {
                    'cache': '🧠 (Cache)',
                    'pandas_agent': '🐼 (Analyse)',
                    'llm_with_context': '🤖 (IA)',
                    'agent': '🔧 (Agent)',
                    'error': '⚠️ (Erreur)'
                }
                st.caption(f"Source: {source_emoji.get(result.get('source', 'unknown'), '❓')}")
                
                # Afficher la visualisation si présente
                if 'visualization' in result and result['visualization']:
                    display_visualization(result['visualization'])
                    
                    # Sauvegarder le message avec visualisation
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result['response'],
                        "visualization": result['visualization']
                    })
                else:
                    # Sauvegarder le message sans visualisation
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result['response']
                    })
    
    # Section d'exemples de requêtes
    if not files_info:
        st.info("💡 **Astuce:** Chargez d'abord un fichier CSV ou Excel pour commencer l'analyse !")
    else:
        st.subheader("💡 Exemples de Requêtes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 Analyse Descriptive**
            - "Montre-moi un résumé des données"
            - "Quelles sont les colonnes disponibles ?"
            - "Combien de lignes contient le dataset ?"
            """)
        
        with col2:
            st.markdown("""
            **📈 Visualisations**
            - "Crée un histogramme de [colonne]"
            - "Montre la corrélation entre les variables"
            - "Fais un graphique en barres des catégories"
            """)
        
        with col3:
            st.markdown("""
            **🔍 Questions Métier**
            - "Quelle est la tendance des ventes ?"
            - "Trouve les valeurs aberrantes"
            - "Compare les performances par région"
            """)


def display_visualization(plot_base64: str):
    """Affiche une visualisation encodée en base64 avec bouton d'export."""
    try:
        # Décoder et afficher l'image
        image_data = base64.b64decode(plot_base64)
        st.image(image_data, caption="Visualisation générée", use_column_width=True)
        
        # Bouton de téléchargement
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visualization_{timestamp}.png"
        
        st.download_button(
            label="📥 Télécharger l'image",
            data=image_data,
            file_name=filename,
            mime="image/png",
            key=f"download_{timestamp}"
        )
        
    except Exception as e:
        st.error(f"Erreur lors de l'affichage de la visualisation: {e}")


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
    data_manager, semantic_cache, _ = initialize_components()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Statistiques ChromaDB")
        db_stats = data_manager.get_stats()
        st.json(db_stats)
    
    with col2:
        st.subheader("🧠 Statistiques Cache")
        cache_stats = semantic_cache.get_stats()
        st.json(cache_stats)
    
    # Boutons d'administration
    st.subheader("🔧 Administration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Réinitialiser la base de données"):
            if st.checkbox("Confirmer la réinitialisation"):
                data_manager.reset_database()
                st.success("Base de données réinitialisée !")
    
    with col2:
        if st.button("🧹 Vider le cache sémantique"):
            semantic_cache.clear()
            st.success("Cache sémantique vidé !")
    
    with col3:
        if st.button("📝 Effacer l'historique de chat"):
            st.session_state.messages = []
            st.success("Historique effacé !")


if __name__ == "__main__":
    main()
