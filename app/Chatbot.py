import streamlit as st
from core.pipeline.pipeline import RAGPipeline
from core.vector_store.history import History
import uuid
from core.setup import Setup

st.title("Hi, ask me anything about your documents!")

with st.sidebar:
    if "setup_verified" not in st.session_state:
        with st.spinner("Vérification..."):
            setup = Setup()
            if setup.verify_setup():
                st.session_state.setup_verified = True
                st.success("Configuré", icon="✅")
            else:
                st.error("Erreur config", icon="❌")
                st.stop()
    else:
        st.success("Configuré", icon="✅")
    if st.button("+ Nouvelle conversation"):
        st.session_state.messages = []
        st.session_state.current_conversation_id = None
        if "pipeline" in st.session_state:
                st.session_state.pipeline = RAGPipeline()
        st.rerun()
        
if "history" not in st.session_state:
    st.session_state.history = History()
    
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

my_history = st.session_state.history.list_history()
    
with st.sidebar:
    if my_history:
        for conversation in my_history:
            if st.button(conversation["title"], type="secondary"):
                st.session_state.messages = []
                st.session_state.current_conversation_id = conversation["id"]
                st.session_state.messages = st.session_state.history.load_messages(conversation["id"]) # type: ignore
                st.rerun() 
    
if "pipeline" not in st.session_state:
    st.session_state.pipeline = RAGPipeline()

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if "sources" in message and message["sources"]:
            st.markdown("**Documents sources :**")
            documents = message["sources"][0].hits if message["sources"] else []
            if documents:
                cols = st.columns(len(documents))
                for idx, doc in enumerate(documents):
                    with cols[idx]:
                        st.markdown(f"📄 - {doc.source['doc_title']}")
        
if prompt := st.chat_input("Poser une question sur un document"):
    if st.session_state.current_conversation_id is None:
        new_conversation_id = str(uuid.uuid4())
        st.session_state.current_conversation_id = new_conversation_id
        st.session_state.history.create_conversation(new_conversation_id, message=prompt)
        
    st.session_state.history.add_message(
        conversation_id=st.session_state.current_conversation_id,
        role="user",
        message=prompt
    )
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.status("Thinking...", expanded=True) as status: 
            status_placeholder = st.empty()
            
            def status_callback(message: str):
                status_placeholder.text(message)
            
        response = st.session_state.pipeline.process_query(prompt, status_callback=status_callback)

        if response.error:
            status.update(
                label="Erreur lors du traitement",
                state="error",
                expanded=True
            )
            error_text = f"Details: {response.details}"
            st.markdown(error_text)
            st.session_state.history.add_message(
                conversation_id=st.session_state.current_conversation_id,
                role="assistant",
                message=error_text
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_text
            })
        else:
            status.update(
                label="Traitement terminé ✓",
                state="complete",
                expanded=False
            )
            st.markdown(response.answer)
            st.session_state.history.add_message(
                conversation_id=st.session_state.current_conversation_id,
                role="assistant",
                message=response.answer
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.answer,
                "sources": response.source_documents
            })
    st.rerun()