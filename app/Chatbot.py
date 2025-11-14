import streamlit as st
from core.pipeline.pipeline import RAGPipeline


st.title("Hi, ask me anything about your documents!")


with st.sidebar:
    if st.button("Nouvelle conversation"):
        st.session_state.messages = []
        if "pipeline" in st.session_state:
                st.session_state.pipeline = RAGPipeline()
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
                        st.markdown(f"<span style='background-color: #e0e0e0; padding: 5px 10px; border-radius: 15px; font-size: 12px;'>📄 {doc.source['doc_title']}</span>", unsafe_allow_html=True)
        
if prompt := st.chat_input("Poser une question sur un document"):
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
                st.markdown(f"Error: {response.error}\nDetails: {response.details}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Error: {response.error}\nDetails: {response.details}"
                })
        else:
            status.update(
                label="Traitement terminé ✓", 
                state="complete", 
                expanded=False
            )
            st.markdown(response.answer)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response.answer,
                "sources" : response.source_documents
            })
    st.rerun()