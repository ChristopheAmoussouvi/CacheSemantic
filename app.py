"""
Interface utilisateur Streamlit pour l'agent IA d'analyse de données.
Interface moderne et intuitive pour l'interaction en langage naturel.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
from typing import List
import logging
import json
import importlib
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# Constantes UI réutilisées
MAP_MODE_POINTS = "Points (valeur par agence)"
MAP_MODE_POLY = "Polygones + Points (agg par zone)"
NONE_LABEL = "(aucune)"

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
from src.components.auto_plotter import AutoPlotter
# DataGenerator import retiré (non utilisé)
from src.utils.example_prompts import ExamplePrompts
from src.components.choropleth_map import (
    build_agencies_choropleth,
    build_region_choropleth_with_points,
    export_map_html_bytes,
)

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
    
    except (OSError, RuntimeError) as e:
        st.error(f"Erreur lors de l'initialisation: {e}")
        st.stop()


def main():
    """Fonction principale de l'application Streamlit."""
    _setup_page_header()

    data_manager, simple_cache, ai_agent = initialize_components()

    uploaded_files = _setup_sidebar()
    if uploaded_files:
        _process_uploaded_files(uploaded_files, data_manager, ai_agent)

    _setup_chat_interface(simple_cache, ai_agent)

def _setup_page_header():
    """Configurer le titre et la description de la page."""
    st.title("🤖 Agent IA Local - Analyse de Données")
    st.markdown("Analysez vos données avec l'intelligence artificielle en langage naturel.")

def _setup_sidebar() -> List:
    """Configurer la barre latérale avec téléchargement et prompts rapides."""
    st.sidebar.header("📁 Données")
    st.sidebar.markdown("Téléchargez vos fichiers de données (CSV, Excel)")
    uploader = st.sidebar.file_uploader(
        "Choisir des fichiers",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True
    )

    st.sidebar.markdown("---")
    st.sidebar.header("⚡ Prompts rapides")
    if 'example_prompts' not in st.session_state:
        st.session_state.example_prompts = ExamplePrompts()
    ep: ExamplePrompts = st.session_state.example_prompts

    # Sélection de catégorie
    categories = ep.get_categories()
    selected_cat = st.sidebar.selectbox("Catégorie", categories)
    prompts_list = ep.get_prompts_by_category(selected_cat)
    if prompts_list:
        # Préparer affichage avec marquage custom
        display_titles = []
        for title, _body in prompts_list:
            if ep.is_custom(selected_cat, title):
                display_titles.append(f"{title} (custom)")
            else:
                display_titles.append(title)
        # Fonction locale pour retirer le suffixe custom
        def _real_title(display: str) -> str:
            return display.replace(" (custom)", "")
        selected_display_title = st.sidebar.selectbox("Prompt", display_titles, key="quick_prompt_title")
        true_title = _real_title(selected_display_title) if selected_display_title else ""
        if true_title:
            selected_prompt = next((p[1] for p in prompts_list if p[0] == true_title), "")
        else:
            selected_prompt = ""
        send_quick_prompt = st.sidebar.button("➡️ Envoyer ce prompt")
        if send_quick_prompt and selected_prompt:
            st.session_state.queued_prompt = selected_prompt
    else:
        st.sidebar.info("Aucun prompt dans cette catégorie")

    st.sidebar.markdown("---")
    if st.sidebar.button("🎲 Prompt aléatoire"):
        cat, title, pr = ep.get_random_prompt()
        st.session_state.queued_prompt = pr
        st.sidebar.success(f"{title} ({cat})")

    return uploader

def _process_uploaded_files(uploaded_files: List, data_manager: DataManager, ai_agent: LocalAIAgent) -> None:
    """Traiter et indexer les fichiers uploadés (ChromaDB + chargement agent) + génération auto de plots."""
    success_count = 0
    errors: list[str] = []
    auto_plotter = AutoPlotter(export_dir="./exports")
    
    with st.spinner("Traitement des fichiers..."):
        for file in uploaded_files:
            try:
                if _index_file(file, data_manager, ai_agent, auto_plotter):
                    success_count += 1
            except (OSError, ValueError) as e:  # pragma: no cover
                errors.append(f"{file.name}: {e}")
    
    if success_count > 0:
        st.success(f"{success_count} fichier(s) traité(s) avec succès !")
    for err in errors:
        st.error(f"Erreur fichier - {err}")

def _index_file(file, data_manager: DataManager, ai_agent: LocalAIAgent, auto_plotter: AutoPlotter) -> bool:
    """Indexer le fichier dans ChromaDB, charger dans l'agent et générer des visualisations auto."""
    try:
        temp_path = f"temp_{file.name}"
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        
        indexed = data_manager.load_data_file(temp_path)
        loaded = ai_agent.load_data_for_analysis(temp_path)
        
        if indexed and loaded:
            st.info(f"Fichier '{file.name}' indexé et chargé")
            
            # Générer automatiquement des visualisations
            with st.spinner("📊 Génération automatique de visualisations..."):
                try:
                    # Charger le DataFrame pour analyse
                    if temp_path.endswith('.csv'):
                        df = pd.read_csv(temp_path)
                    else:
                        df = pd.read_excel(temp_path)
                    
                    # Générer les plots automatiques
                    plots = auto_plotter.generate_auto_plots(df, max_plots=6)
                    
                    if plots:
                        st.success(f"✅ {len(plots)} visualisations générées automatiquement !")
                        
                        # Afficher les visualisations dans une section expandable
                        with st.expander(f"📊 Visualisations automatiques de {file.name}", expanded=True):
                            # Créer une grille 2x3
                            cols_per_row = 2
                            for i in range(0, len(plots), cols_per_row):
                                cols = st.columns(cols_per_row)
                                for j, (title, filepath) in enumerate(plots[i:i+cols_per_row]):
                                    with cols[j]:
                                        st.image(filepath, caption=title, use_container_width=True)
                    else:
                        st.info("ℹ️ Aucune visualisation automatique générée")
                        
                except Exception as e:
                    logger.error(f"Erreur lors de la génération des plots automatiques: {e}")
                    st.warning(f"⚠️ Impossible de générer les visualisations automatiques: {e}")
            
            return True
        
        st.warning(f"Fichier '{file.name}' partiellement traité (indexed={indexed}, loaded={loaded})")
        return False
    
    except (OSError, ValueError) as e:  # pragma: no cover
        st.error(f"Erreur lors de l'indexation: {e}")
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
    queued = st.session_state.pop('queued_prompt', None) if 'queued_prompt' in st.session_state else None
    user_question = st.chat_input("Posez votre question sur les données...")
    if user_question is not None:
        _handle_user_question(user_question, simple_cache, ai_agent)
    elif queued is not None:
        _handle_user_question(str(queued), simple_cache, ai_agent)

def _display_chat_history() -> None:
    """Afficher les messages de chat existants."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message.get("content", "(vide)"))
            viz_b64 = message.get("visualization")
            if viz_b64:
                try:
                    img_bytes = base64.b64decode(viz_b64)
                    st.image(img_bytes, caption="Visualisation (cache)")
                except ValueError:
                    pass

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

def _get_ai_response(question: str, simple_cache: SimpleCache, ai_agent: LocalAIAgent) -> dict:
    """Obtenir une réponse de l'agent IA avec mise en cache simple."""
    try:
        cached_entry = simple_cache.get(question)
        if cached_entry:
            cached_result = cached_entry.get('response', {})
            cached_result['source'] = 'cache'
            return cached_result
        result = ai_agent.process_query(question)
        simple_cache.put(question, result)
        return result
    except (OSError, RuntimeError, ValueError) as e:  # pragma: no cover
        return {
            'response': f"Erreur lors du traitement: {e}",
            'source': 'error',
            'success': False
        }

def _display_ai_response(response_data: dict) -> None:
    """Afficher la réponse de l'IA avec support des visualisations base64."""
    text = response_data.get('response') or response_data.get('content') or ''
    st.markdown(text if text else "(Réponse vide)")
    source_emoji = {"cache": "🔄", "local_agent": "🤖", "chatbot": "🧠", "error": "❌"}
    raw_source = response_data.get('source') or 'inconnue'
    st.caption(f"{source_emoji.get(str(raw_source), '❓')} Source: {raw_source}")
    viz_b64 = response_data.get('visualization')
    if viz_b64 and isinstance(viz_b64, str) and len(viz_b64) > 20:
        try:
            img_bytes = base64.b64decode(viz_b64)
            st.image(img_bytes, caption="Visualisation")
            st.download_button(
                "📥 Télécharger le graphique",
                data=img_bytes,
                file_name="visualisation.png",
                mime="image/png"
            )
        except ValueError as e:  # pragma: no cover
            st.warning(f"Impossible d'afficher la visualisation: {e}")
    st.session_state.messages.append({
        "role": "assistant",
        "content": text,
        "visualization": response_data.get('visualization')
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
    except (OSError, IOError, ValueError) as e:
        st.error(f"Erreur d'affichage du graphique: {str(e)}")


def show_data_preview():
    """Affiche un aperçu des données chargées."""
    _, _, ai_agent = initialize_components()
    
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
ALL_CATS_LABEL = "(Toutes)"
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["💬 Chat", "📊 Aperçu Données", "🧪 Prompts", "🗺️ Carte Choropleth", "📈 Support Analytics", "⚙️ Configuration"])

with tab1:
    # Le contenu principal est déjà affiché
    pass

with tab2:
    show_data_preview()

with tab3:
    st.header("🧪 Gestion des Prompts")
    if 'example_prompts' not in st.session_state:
        st.session_state.example_prompts = ExamplePrompts()
    ep: ExamplePrompts = st.session_state.example_prompts
    # Récupérer le dataframe courant (si chargé) pour validation/suggestions
    _, _, _agent_for_prompts = initialize_components()
    current_df = getattr(_agent_for_prompts, 'current_dataframe', None)

    st.subheader("➕ Ajouter un nouveau prompt")
    with st.form("add_prompt_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            new_cat = st.text_input("Catégorie", placeholder="Nouvelle catégorie ou existante")
        with col_b:
            new_title = st.text_input("Titre du prompt")
        prompt_body = st.text_area("Texte du prompt")
        with st.expander("Métadonnées visualisation (optionnel)"):
            viz_key = "add_prompt_viz_type"
            df_columns = list(current_df.columns) if current_df is not None else []
            if not df_columns:
                st.info("Chargez un fichier pour sélectionner les colonnes dynamiquement.")
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                x_col = st.selectbox("Colonne X", [""] + df_columns, index=0, key="prompt_x_col") if df_columns else ""
            with col_sel2:
                y_col = st.selectbox("Colonne Y", [""] + df_columns, index=0, key="prompt_y_col") if df_columns else ""
            multi_cols = st.multiselect("Colonnes multiples (pour heatmap / analyses)", df_columns, key="prompt_multi_cols") if df_columns else []

            # Construire le mapping courant
            parsed_columns = {}
            if x_col:
                parsed_columns['x'] = x_col
            if y_col:
                parsed_columns['y'] = y_col
            if multi_cols:
                parsed_columns['columns'] = multi_cols

            # Validation colonnes
            validation = ep.validate_columns(current_df, parsed_columns) if parsed_columns else {"valid": [], "invalid": []}
            suggested_viz, reason = ep.suggest_viz_type(current_df, parsed_columns) if parsed_columns else ("", "")
            viz_options = ["", "histogram", "scatter", "bar_chart", "line_chart", "heatmap", "boxplot"]
            current_viz_state = st.session_state.get(viz_key, "")
            viz_type = st.selectbox("Type de visualisation", viz_options, index=viz_options.index(current_viz_state) if current_viz_state in viz_options else 0, key=viz_key)
            if suggested_viz:
                c1, c2 = st.columns([3,1])
                with c1:
                    st.caption(f"Suggestion: {suggested_viz} ({reason})")
                with c2:
                    if st.button("Appliquer suggestion"):
                        st.session_state[viz_key] = suggested_viz
                        viz_type = suggested_viz
            # Feedback validation
            if validation["valid"]:
                st.success("Colonnes valides: " + ", ".join(validation['valid']))
            if validation["invalid"]:
                st.error("Colonnes invalides: " + ", ".join(validation['invalid']))
        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            # Parser colonnes
            columns = parsed_columns if parsed_columns else None
            added = ep.add_prompt(new_cat or "Divers", new_title, prompt_body, st.session_state.get(viz_key) or None, columns)
            if added:
                st.success("Prompt ajouté")
            else:
                st.error("Impossible d'ajouter (vide ou doublon)")

    st.subheader("📚 Liste des prompts")
    search_query = st.text_input("Recherche (titre / texte / catégorie)", "", key="prompt_search")
    selected_view_cat = st.selectbox("Filtrer par catégorie", [ALL_CATS_LABEL] + ep.get_categories(), key="view_cat")
    if search_query.strip():
        # Recherche globale puis filtrage catégorie si nécessaire
        search_results = ep.search_prompts(search_query.strip())
        if selected_view_cat != ALL_CATS_LABEL:
            search_results = [r for r in search_results if r[0] == selected_view_cat]
        all_prompts = search_results
    else:
        if selected_view_cat == ALL_CATS_LABEL:
            all_prompts = ep.get_all_prompts()
        else:
            cat_prompts = ep.get_prompts_by_category(selected_view_cat)
            all_prompts = [(selected_view_cat, t, p) for t, p in cat_prompts]
    if all_prompts:
        for cat, title, pr in all_prompts[:200]:
            is_custom = ep.is_custom(cat, title)
            custom_mark = " (custom)" if is_custom else ""
            with st.expander(f"{title}{custom_mark} | {cat}"):
                st.write(pr)
                if is_custom:
                    meta = ep.get_metadata(cat, title) or {}
                    with st.form(f"edit_form_{cat}_{title}"):
                        new_title_val = st.text_input("Titre", value=title, key=f"edit_title_{cat}_{title}")
                        new_body_val = st.text_area("Texte", value=pr, height=120, key=f"edit_body_{cat}_{title}")
                        viz_type_val = st.selectbox(
                            "Type de visualisation",
                            ["", "histogram", "scatter", "bar_chart", "line_chart", "heatmap", "boxplot"],
                            index=0 if not meta.get('viz_type') else ["", "histogram", "scatter", "bar_chart", "line_chart", "heatmap", "boxplot"].index(meta.get('viz_type','')),
                            key=f"edit_viz_{cat}_{title}"
                        )
                        columns_meta = meta.get('columns') or {}
                        columns_json = st.text_input("Colonnes (JSON)", value=json.dumps(columns_meta) if columns_meta else "", key=f"edit_cols_{cat}_{title}")
                        c_upd, c_del = st.columns(2)
                        with c_upd:
                            do_update = st.form_submit_button("💾 Mettre à jour")
                        with c_del:
                            do_delete = st.form_submit_button("🗑️ Supprimer")
                        if do_update:
                            # Parse columns JSON
                            parsed_cols = None
                            if columns_json.strip():
                                try:
                                    candidate = json.loads(columns_json)
                                    if isinstance(candidate, dict):
                                        parsed_cols = candidate
                                    else:
                                        st.error("Le JSON des colonnes doit être un objet {key: valeur}")
                                except json.JSONDecodeError as je:
                                    st.error(f"JSON invalide: {je}")
                            success = ep.update_prompt(cat, title, new_title_val, new_body_val, viz_type_val or None, parsed_cols)
                            if success:
                                st.success("Prompt mis à jour")
                                if new_title_val != title:
                                    try:
                                        st.rerun()
                                    except Exception:
                                        pass
                            else:
                                st.error("Échec de la mise à jour (doublon ou données invalides)")
                        if do_delete:
                            if ep.delete_prompt(cat, title):
                                st.warning("Prompt supprimé")
                                try:
                                    st.rerun()
                                except Exception:
                                    pass
                            else:
                                st.error("Suppression impossible")
    else:
        st.info("Aucun prompt disponible")

with tab4:
    st.header("🗺️ Carte Choropleth - Agences bancaires")
    _, _, agent_for_map = initialize_components()
    df_map = getattr(agent_for_map, 'current_dataframe', None)
    if df_map is None or getattr(df_map, 'empty', True):
        st.info("Chargez d'abord un fichier contenant des colonnes latitude, longitude et un taux de réclamations.")
    else:
        st.markdown("Choisissez le type de carte, sélectionnez les colonnes et appliquez un seuil optionnel.")
        mode = st.radio("Type de carte", [MAP_MODE_POINTS, MAP_MODE_POLY])
        cols = list(df_map.columns)
        # Colonnes communes
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            lat_col = st.selectbox("Colonne latitude", cols, index=cols.index('latitude') if 'latitude' in cols else 0)
        with c2:
            lon_col = st.selectbox("Colonne longitude", cols, index=cols.index('longitude') if 'longitude' in cols else 0)
        with c3:
            val_col = st.selectbox("Colonne valeur (taux)", cols, index=cols.index('reclamation_rate') if 'reclamation_rate' in cols else 0)
        with c4:
            name_col = st.selectbox("Colonne nom (optionnel)", [NONE_LABEL] + cols)

        threshold = st.number_input("Seuil minimum", min_value=0.0, step=0.1, value=0.0)

        m = None
        count_points = 0
        count_polygons = 0

        if mode == MAP_MODE_POINTS:
            if st.button("Afficher la carte (Points)"):
                ncol = None if name_col == NONE_LABEL else name_col
                if lat_col and lon_col and val_col:
                    m, count_points = build_agencies_choropleth(
                        df_map, lat_col=lat_col, lon_col=lon_col, value_col=val_col, name_col=ncol, threshold=threshold
                    )
                else:
                    st.warning("Veuillez sélectionner les colonnes latitude, longitude et valeur.")
        else:
            st.markdown("---")
            st.markdown("Choropleth par polygones : importez un GeoJSON et précisez les clés de jointure.")
            gj_file = st.file_uploader("GeoJSON des communes/régions", type=["geojson", "json"])
            polygons = None
            gj_key = ""
            df_key = ""
            if gj_file is not None:
                try:
                    polygons = json.loads(gj_file.getvalue().decode("utf-8"))
                    props_keys = []
                    try:
                        # Collecter clés de properties depuis le premier feature
                        features = polygons.get("features", [])
                        if features and isinstance(features[0], dict):
                            props = features[0].get("properties", {})
                            if isinstance(props, dict):
                                props_keys = list(props.keys())
                    except (KeyError, AttributeError, TypeError):
                        props_keys = []
                    cpa, cpb = st.columns(2)
                    with cpa:
                        gj_key = st.selectbox("Propriété GeoJSON (clé de jointure)", props_keys or [""], index=0)
                    with cpb:
                        df_key = st.selectbox("Colonne DataFrame (clé de jointure)", cols, index=0)
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    st.error(f"GeoJSON invalide: {e}")
            if st.button("Afficher la carte (Polygones + Points)"):
                if polygons and gj_key and df_key and lat_col and lon_col and val_col:
                    ncol = None if name_col == NONE_LABEL else name_col
                    m, count_points, count_polygons = build_region_choropleth_with_points(
                        df_map,
                        polygons_geojson=polygons,
                        join_key_geo=gj_key,
                        join_key_df=df_key,
                        lat_col=lat_col,
                        lon_col=lon_col,
                        value_col=val_col,
                        name_col=ncol,
                        threshold=threshold,
                    )
                else:
                    st.warning("Veuillez fournir un GeoJSON et sélectionner les clés de jointure ainsi que les colonnes latitude/longitude/valeur.")

        # Rendu et export (si la carte est générée)
        if m is not None:
            # Affichage de la carte: utiliser streamlit-folium si disponible, sinon fallback HTML autonome
            try:
                st_folium = getattr(importlib.import_module("streamlit_folium"), "st_folium", None)
            except Exception:
                st_folium = None
            if callable(st_folium):
                try:
                    st_folium(m, width=1200, height=650)
                except Exception:
                    map_html = m.get_root().render()
                    components.html(map_html, height=650)
            else:
                map_html = m.get_root().render()
                components.html(map_html, height=650)

            if mode == MAP_MODE_POINTS:
                st.caption(f"Points affichés: {count_points}")
            else:
                st.caption(f"Zones: {count_polygons} | Points: {count_points}")

            # Export HTML autonome
            try:
                html_bytes = export_map_html_bytes(m)
                st.download_button(
                    label="📥 Télécharger la carte (HTML)",
                    data=html_bytes,
                    file_name="carte_choropleth.html",
                    mime="text/html"
                )
            except (OSError, ValueError) as e:
                st.warning(f"Export HTML indisponible: {e}")

with tab5:
    st.header("📈 Enhanced Support Analytics Dashboard")
    
    # Import du dashboard analytics amélioré
    try:
        from src.components.enhanced_dashboard import EnhancedAnalyticsDashboard
        
        # Initialiser le dashboard
        if 'enhanced_dashboard' not in st.session_state:
            st.session_state.enhanced_dashboard = EnhancedAnalyticsDashboard()
        
        dashboard = st.session_state.enhanced_dashboard
        
        # Obtenir les données courantes
        _, _, agent_for_analytics = initialize_components()
        current_df = getattr(agent_for_analytics, 'current_dataframe', None)
        
        if current_df is None or current_df.empty:
            st.info("📊 **Enhanced Support Analytics Dashboard** - Comprehensive KPI tracking and performance analytics")
            
            # Afficher un aperçu des fonctionnalités
            st.subheader("🚀 Dashboard Features")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **� Key Performance Indicators**
                - Customer Satisfaction Scores (CSAT)
                - First Call Resolution Rates (FCR)
                - Average Handle Time (AHT)
                - Net Promoter Score (NPS)
                - Ticket Volumes & Resolution Times
                """)
                
                st.markdown("""
                **� Customer Satisfaction Trends**
                - CSAT & NPS tracking over time
                - Dual y-axis line charts
                - Trend analysis with markers
                - Daily/weekly/monthly views
                """)
            
            with col2:
                st.markdown("""
                **� Channel Performance Analysis**
                - Ticket volumes by channel (Phone, Email, Chat, Social, Branch)
                - Channel-specific metrics
                - Performance comparison charts
                - Handle time analysis by channel
                """)
                
                st.markdown("""
                **� Agent Performance Metrics**
                - Individual agent statistics
                - Performance scoring system
                - Top performer identification
                - Tickets resolved, handle times, satisfaction ratings
                """)
            
            st.markdown("""
            **🔍 Advanced Filtering & Analytics**
            - Time range selectors with quick ranges
            - Multi-select channel, agent, and category filters
            - Interactive date pickers
            - Real-time dashboard updates
            - Ticket analytics with pie charts and trends
            - Performance patterns by hour analysis
            - Resolution time distribution analysis
            """)
            
            # Bouton pour charger des données d'exemple avec le nouveau dashboard
            if st.button("📊 Launch Enhanced Dashboard with Sample Data"):
                st.success("✅ Enhanced Dashboard activated with comprehensive sample data!")
                st.rerun()
        
        else:
            # Utiliser les données courantes ou lancer avec des données d'exemple
            df_to_use = current_df
            
            # Rendre le dashboard amélioré
            dashboard.render_dashboard(df_to_use)
    
    except ImportError as e:
        st.error(f"Erreur d'import du dashboard: {e}")
        st.info("Assurez-vous que toutes les dépendances sont installées (plotly, scikit-learn)")
    except Exception as e:
        st.error(f"Erreur dans le dashboard analytics: {e}")
        st.info("Rechargez la page ou contactez l'administrateur.")

with tab6:
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
    st.info("🧠 **Cache local simple** : Réponses répétées servies immédiatement")
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
