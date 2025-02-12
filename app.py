import streamlit as st
from openai import OpenAI
from datetime import datetime
import uuid

# Configuration de l'application
st.set_page_config(
    page_title="Ala Eddine Local Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialisation du client OpenAI
@st.cache_resource
def load_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

client = load_openai_client()

# Gestion des sessions de chat
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    
if "current_chat_id" not in st.session_state:
    new_chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = new_chat_id
    st.session_state.chat_sessions[new_chat_id] = {
        "id": new_chat_id,
        "name": "Discussion 1",
        "messages": [
            {"role": "system", "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets.", "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")}
        ],
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

# Sidebar - Gestion des sessions
with st.sidebar:
    st.header("💬 Historique des discussions")
    
    if st.button("➕ Nouvelle discussion", use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chat_sessions[new_chat_id] = {
            "id": new_chat_id,
            "name": f"Discussion {len(st.session_state.chat_sessions)+1}",
            "messages": [
                {"role": "system", "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets.", "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")}
            ],
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        st.rerun()
    
    for chat_id, chat in st.session_state.chat_sessions.items():
        if st.button(chat['name'], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# Affichage de la discussion sélectionnée
if selected_chat := st.session_state.chat_sessions.get(st.session_state.current_chat_id):
    for msg in selected_chat['messages']:
        if msg['role'] in ['user', 'assistant']:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

# Gestion des questions utilisateur
if prompt := st.chat_input("Posez votre question..."):
    selected_chat = st.session_state.chat_sessions.get(st.session_state.current_chat_id)
    
    if selected_chat:
        selected_chat['messages'].append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Utilise GPT-4 pour des réponses optimales
                    messages=[{"role": msg["role"], "content": msg["content"]} for msg in selected_chat["messages"]]
                )
                full_response = response.choices[0].message.content
                response_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"❌ Erreur: {str(e)}"
                response_placeholder.error(full_response)
            
            selected_chat['messages'].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
            })