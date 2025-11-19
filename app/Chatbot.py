import streamlit as st
from core.pipeline.pipeline import RAGPipeline
from core.vector_store.history import History
import uuid
from core.setup import Setup
from core.vector_store.logger import ActivityLogger
import traceback

st.title("Hi, ask me anything about your documents!")

with st.sidebar:
    if "setup_verified" not in st.session_state:
        with st.spinner("Vérification..."):
            try:
                setup = Setup()
                if setup.verify_setup():
                    st.session_state.setup_verified = True
                    st.success("Configuré", icon="✅")
                else:
                    st.error("Erreur config", icon="❌")
                    print("Setup verification failed")
                    st.stop()
            except Exception as e:
                error_msg = f"Erreur lors de la vérification de la configuration: {str(e)}"
                st.error(error_msg, icon="❌")
                print(f"Setup error: {str(e)}\n{traceback.format_exc()}")
                st.expander("Détails de l'erreur").code(traceback.format_exc())
                st.stop()
    else:
        st.success("Configuré", icon="✅")
        activity_logger = ActivityLogger(source="chatbot")

    if st.button("+ Nouvelle conversation"):
        try:
            activity_logger.log_interaction("New conversation started", "info")
            st.session_state.messages = []
            st.session_state.current_conversation_id = None
            if "pipeline" in st.session_state:
                    st.session_state.pipeline = RAGPipeline()
            st.rerun()
        except Exception as e:
            error_msg = f"Erreur lors de la création d'une nouvelle conversation: {str(e)}"
            st.error(error_msg)
            activity_logger.log_interaction(f"New conversation error: {str(e)}\n{traceback.format_exc()}", "error")



if "history" not in st.session_state:
    try:
        st.session_state.history = History()
    except Exception as e:
        error_msg = f"Erreur lors de l'initialisation de l'historique: {str(e)}"
        st.error(error_msg)
        activity_logger.log_interaction(f"History initialization error: {str(e)}\n{traceback.format_exc()}", "error")
        st.stop()
    
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

try:
    my_history = st.session_state.history.list_history()
except Exception as e:
    error_msg = f"Erreur lors du chargement de l'historique: {str(e)}"
    st.sidebar.error(error_msg)
    activity_logger.log_interaction(f"History loading error: {str(e)}\n{traceback.format_exc()}", "error")
    my_history = []
    
with st.sidebar:
    if my_history:
        for conversation in my_history:
            if st.button(conversation["title"], type="secondary"):
                try:
                    activity_logger.log_interaction(f"Switched to conversation {conversation['id']}", "info")
                    st.session_state.messages = []
                    st.session_state.current_conversation_id = conversation["id"]
                    st.session_state.messages = st.session_state.history.load_messages(conversation["id"]) # type: ignore
                    st.rerun()
                except Exception as e:
                    error_msg = f"Erreur lors du chargement de la conversation: {str(e)}"
                    st.error(error_msg)
                    activity_logger.log_interaction(f"Conversation loading error: {str(e)}\n{traceback.format_exc()}", "error")
    
if "pipeline" not in st.session_state:
    try:
        st.session_state.pipeline = RAGPipeline()
    except Exception as e:
        error_msg = f"Erreur lors de l'initialisation du pipeline RAG: {str(e)}"
        st.error(error_msg)
        activity_logger.log_interaction(f"Pipeline initialization error: {str(e)}\n{traceback.format_exc()}", "error")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if "sources" in message and message["sources"]:
                try:
                    st.markdown("**Documents sources :**")
                    documents = message["sources"][0].hits if message["sources"] else []
                    if documents:
                        cols = st.columns(len(documents))
                        for idx, doc in enumerate(documents):
                            with cols[idx]:
                                doc_title = doc.source.get('doc_title', 'Document sans titre')
                                st.markdown(f"📄 - {doc_title}")
                except Exception as e:
                    activity_logger.log_interaction(f"Error displaying sources: {str(e)}", "error")
                    st.caption("⚠️ Erreur lors de l'affichage des sources")
except Exception as e:
    error_msg = f"Erreur lors de l'affichage des messages: {str(e)}"
    st.error(error_msg)
    activity_logger.log_interaction(f"Message display error: {str(e)}\n{traceback.format_exc()}", "error")
        
if prompt := st.chat_input("Poser une question sur un document"):
    activity_logger.log_interaction(f"User asked a question: {prompt}", "info")
    
    try:
        # Gestion de la création de conversation
        if st.session_state.current_conversation_id is None:
            new_conversation_id = str(uuid.uuid4())
            st.session_state.current_conversation_id = new_conversation_id
            try:
                st.session_state.history.create_conversation(new_conversation_id, message=prompt)
            except Exception as e:
                error_msg = f"Erreur lors de la création de la conversation: {str(e)}"
                st.error(error_msg)
                activity_logger.log_interaction(f"Conversation creation error: {str(e)}\n{traceback.format_exc()}", "error")
                st.stop()
        
        # Ajout du message utilisateur à l'historique
        try:
            st.session_state.history.add_message(
                conversation_id=st.session_state.current_conversation_id,
                role="user",
                message=prompt
            )
        except Exception as e:
            activity_logger.log_interaction(f"Error saving user message to history: {str(e)}", "error")
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.status("Thinking...", expanded=True) as status: 
                status_placeholder = st.empty()
                
                def status_callback(message: str):
                    status_placeholder.text(message)
            
            try:
                response = st.session_state.pipeline.process_query(prompt, status_callback=status_callback)

                if response.error:
                    activity_logger.log_interaction(f"Error during processing: {response.details}", "info") # this is not really an error just a guardrail response
                    status.update(
                        label="Erreur lors du traitement",
                        state="error",
                        expanded=True
                    )
                    error_text = f"Details: {response.details}"
                    st.markdown(error_text)
                    
                    try:
                        st.session_state.history.add_message(
                            conversation_id=st.session_state.current_conversation_id,
                            role="assistant",
                            message=error_text
                        )
                    except Exception as e:
                        activity_logger.log_interaction(f"Error saving error message to history: {str(e)}", "error")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_text
                    })
                else:
                    activity_logger.log_interaction("Response generated successfully", "info")
                    status.update(
                        label="Traitement terminé ✓",
                        state="complete",
                        expanded=False
                    )
                    st.markdown(response.answer)
                    
                    try:
                        st.session_state.history.add_message(
                            conversation_id=st.session_state.current_conversation_id,
                            role="assistant",
                            message=response.answer
                        )
                    except Exception as e:
                        activity_logger.log_interaction(f"Error saving assistant message to history: {str(e)}", "error")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.answer,
                        "sources": response.source_documents
                    })
            except Exception as e:
                error_msg = f"Erreur critique lors du traitement de la question: {str(e)}"
                st.error(error_msg)
                activity_logger.log_interaction(f"Critical pipeline error: {str(e)}\n{traceback.format_exc()}", "error")
                status.update(
                    label="Erreur critique",
                    state="error",
                    expanded=True
                )
                with st.expander("Détails techniques de l'erreur"):
                    st.code(traceback.format_exc())
        
        st.rerun()
        
    except Exception as e:
        error_msg = f"Erreur inattendue: {str(e)}"
        st.error(error_msg)
        activity_logger.log_interaction(f"Unexpected error in chat input handler: {str(e)}\n{traceback.format_exc()}", "error")
        with st.expander("Détails techniques de l'erreur"):
            st.code(traceback.format_exc())