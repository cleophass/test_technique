import streamlit as st
import os
from pathlib import Path
import pandas as pd
from core.config import DOCUMENTS_INDEX_NAME
from core.vector_store.documents_manager import DocumentsManager
from core.vector_store.logger import ActivityLogger
import traceback

activity_logger = ActivityLogger(source="documents_manager")

st.set_page_config(
    layout="wide"
)

if 'doc_manager' not in st.session_state:
    try:
        st.session_state.doc_manager = DocumentsManager(
            raw_path="data/raw",
            clean_path="data/clean"
        )
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation du gestionnaire de documents: {str(e)}")
        activity_logger.log_interaction(f"DocumentsManager initialization error: {str(e)}\n{traceback.format_exc()}", "error")
        st.stop()

if 'index_name' not in st.session_state:
    st.session_state.index_name = DOCUMENTS_INDEX_NAME


st.title("Gestionnaire de documents")

st.header("Config")
st.badge("Index :" + st.session_state.index_name, color="blue")

index_name = st.session_state.index_name

try:
    index_exists = st.session_state.doc_manager.es_client.verify_index(index_name)
    
    if index_exists:
        st.success("✅ Index connecté")
        try:
            documents = st.session_state.doc_manager.es_client.list_documents(index_name)
            st.metric("Nombre de documents", len(documents))
        except Exception as e:
            st.error(f"Erreur lors du chargement des documents: {str(e)}")
            activity_logger.log_interaction(f"Document list loading error: {str(e)}", "error")
    else:
        st.warning("⚠️ Index non trouvé")
except Exception as e:
    st.error(f"Erreur lors de la vérification de l'index: {str(e)}")
    activity_logger.log_interaction(f"Index verification error: {str(e)}\n{traceback.format_exc()}", "error")
    st.stop()

tab1, tab2 = st.tabs(["Liste des Documents", "Ajouter un Document"])

with tab1:
    st.header("Documents indexés")
    
    if index_exists:
        try:
            documents = st.session_state.doc_manager.es_client.list_documents(index_name)
            
            if documents:
                doc_data = []
                for idx, doc in enumerate(documents):
                    try:
                        doc_data.append({
                            "Index": idx,
                            "Titre": doc["_source"].get("doc_title", "Sans titre"),
                            "Source": doc["_source"].get("metadata", {}).get("source", "N/A"),
                            "Date": doc["_source"].get("metadata", {}).get("date", "N/A"),
                            "Indexé le": doc["_source"].get("indexed_at", "N/A"),
                            "Modèle": doc["_source"].get("metadata", {}).get("embedding_model", "N/A")
                        })
                    except Exception as e:
                        activity_logger.log_interaction(f"Error parsing document {idx}: {str(e)}", "error")
                        continue
                
                if doc_data:
                    df = pd.DataFrame(doc_data)
                    st.dataframe(df, hide_index=True)
                else:
                    st.warning("Aucun document valide trouvé.")
        except Exception as e:
            st.error(f"Erreur lors du chargement de la liste: {str(e)}")
            activity_logger.log_interaction(f"Documents list error: {str(e)}", "error")
            
        st.subheader("Détails et Actions")
        
        selected_idx = st.selectbox(
            "Sélectionner un document pour voir les détails",
            options=range(len(documents)),
            format_func=lambda x: documents[x]["_source"].get("doc_title", f"Document {x}")
        )
            
        if selected_idx is not None:
            selected_doc = documents[selected_idx]
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                with st.expander("Contenu du document", expanded=False):
                    content = selected_doc["_source"].get("content", "")
                    st.text_area(
                        "Contenu",
                        value=content[:1000] + ("..." if len(content) > 1000 else ""),
                        height=200,
                        disabled=True
                    )
                
                with st.expander("ℹMétadonnées", expanded=True):
                    metadata = selected_doc["_source"].get("metadata", {})
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Source:** {metadata.get('source', 'N/A')}")
                        st.write(f"**Date:** {metadata.get('date', 'N/A')}")
                        st.write(f"**Modifié:** {metadata.get('modified', 'N/A')}")
                    with col_b:
                        st.write(f"**Modèle d'embedding:** {metadata.get('embedding_model', 'N/A')}")
                        st.write(f"**Dimension:** {metadata.get('embedding_dimension', 'N/A')}")
                        st.write(f"**Date embedding:** {metadata.get('embedding_date', 'N/A')}")
            
            with col2:
                st.markdown("### 🗑️ Supprimer")
                if st.button("Supprimer ce document", type="secondary"):
                    try:
                        activity_logger.log_interaction(f"Document deleted: {selected_doc['_id']}", "info")
                        res = st.session_state.doc_manager.delete_document(
                            index_name, 
                            selected_doc["_id"], 
                            selected_doc["_source"].get("doc_title", ""),
                            selected_doc["_source"].get("metadata", {}).get("source", "")
                        )
                        if res:
                            st.success("Document supprimé!")
                            st.rerun()

                    except Exception as e:
                        st.error(f"Erreur lors de la suppression: {str(e)}")
                        activity_logger.log_interaction(f"Document deletion error: {str(e)}\n{traceback.format_exc()}", "error")
                    
                
        else:
            st.info("Aucun document trouvé dans l'index.")
    else:
        st.warning("L'index n'existe pas. Créez-le depuis la barre latérale.")

with tab2:
    st.header("Ajouter un nouveau document")
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier",
        type=["txt", "csv", "html"],
        help="Formats supportés: TXT, CSV, HTML",
        accept_multiple_files=False
    )
    
    if uploaded_file:
        st.success(f"Fichier chargé: {uploaded_file.name}")
        
        with st.expander("Aperçu du fichier"):
            try:
                if uploaded_file.type == "text/plain":
                    content = uploaded_file.read().decode("utf-8")
                    st.text_area("Contenu", content[:500] + "...", height=150)
                elif uploaded_file.type == "text/csv":
                    df_preview = pd.read_csv(uploaded_file, nrows=5)
                    st.dataframe(df_preview)
                    uploaded_file.seek(0)  # Reset pour la lecture suivante
                elif uploaded_file.type == "text/html":
                    content = uploaded_file.read().decode("utf-8")
                    st.code(content[:500] + "...", language="html")
                    uploaded_file.seek(0)
            except Exception as e:
                activity_logger.log_interaction(f"Error during file preview: {str(e)}", "error")
                st.error(f"Erreur lors de l'aperçu: {e}")


    
    if uploaded_file and st.button("Indexer", type="primary"):
        activity_logger.log_interaction(f"Document uploaded: {uploaded_file.name}", "info")
        with st.spinner("Traitement en cours..."):
            try:
                raw_path = Path("data/raw")
                raw_path.mkdir(parents=True, exist_ok=True)
                
                file_path = raw_path / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("📄 Fichier sauvegardé...")
                    progress_bar.progress(20)
                    
                    status_text.text("🔄 Preprocessing en cours...")
                    progress_bar.progress(40)
                    
                    status_text.text("🧮 Génération des embeddings...")
                    progress_bar.progress(60)
                    
                    success = st.session_state.doc_manager.add_document(
                        index_name,
                        str(file_path)
                    )
                    
                    progress_bar.progress(80)
                    status_text.text("📊 Indexation dans Elasticsearch...")
                    
                    progress_bar.progress(100)
                    
                    if success:
                        activity_logger.log_interaction(f"Document indexed successfully: {uploaded_file.name}", "info")
                        st.success("✅ Document traité et indexé avec succès!")
                        st.balloons()
                    else:
                        activity_logger.log_interaction(f"Document indexing failed: {uploaded_file.name}", "error")
                        st.error("❌ Erreur lors du traitement du document.")
                        
                except Exception as e:
                    activity_logger.log_interaction(f"Document processing error: {str(e)}\n{traceback.format_exc()}", "error")
                    st.error(f"❌ Erreur lors du traitement: {str(e)}")
                    with st.expander("Détails de l'erreur"):
                        st.code(traceback.format_exc())
                finally:
                    progress_bar.empty()
                    status_text.empty()
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la sauvegarde du fichier: {str(e)}")
                activity_logger.log_interaction(f"File save error: {str(e)}\n{traceback.format_exc()}", "error")
