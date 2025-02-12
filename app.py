import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)
import uuid
from datetime import datetime

# Configuration de l'application
st.set_page_config(
    page_title="Ala Eddine Local Chatbot",
    page_icon="🤖",  # Vous pouvez garder cet emoji ou le changer
    layout="centered",
    initial_sidebar_state="expanded"
)

# Ajouter Boxicons CDN
st.markdown("""
    <link href='https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css' rel='stylesheet'>
    
""", unsafe_allow_html=True)

# Charger le CSS personnalisé
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Titre stylisé avec l'icône Boxicons
st.markdown("""
    <h1 style='text-align: center; color: #2B7A78; 
    border-bottom: 3px solid #17252A; padding-bottom: 10px;'>
    <i class='bx bxs-bot' style='font-size: 55px; vertical-align: middle;'></i>
    Ala Eddine Local Chatbot
    </h1>
""", unsafe_allow_html=True)


# Initialisation du modèle
@st.cache_resource
def load_model():
    return ChatOllama(
        model="llama3.2:1b",
        base_url="http://localhost:11434/",
        temperature=0.7,
        num_ctx=1000
    )

model = load_model()

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
            {
                "role": "system",
                "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets.",
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        ],
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

# Sidebar - Gestion des sessions
with st.sidebar:
    st.header("💬 Historique des discussions")
    
    # Bouton Nouvelle discussion
    if st.button("➕ Nouvelle discussion", use_container_width=True):
        new_chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chat_sessions[new_chat_id] = {
            "id": new_chat_id,
            "name": f"Discussion {len(st.session_state.chat_sessions)+1}",
            "messages": [
                {
                    "role": "system",
                    "content": "Vous êtes un tuteur IA expert pour collégiens. Expliquez de manière claire et concise, avec des exemples concrets.",
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
            ],
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        st.rerun()
    
    # Liste des discussions
    for chat_id, chat in st.session_state.chat_sessions.items():
        is_selected = chat_id == st.session_state.current_chat_id
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
                messages = [
                    SystemMessagePromptTemplate.from_template(selected_chat['messages'][0]['content'])
                ]
                for msg in selected_chat['messages'][1:]:
                    if msg["role"] == "user":
                        messages.append(HumanMessagePromptTemplate.from_template(msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessagePromptTemplate.from_template(msg["content"]))

                chain = ChatPromptTemplate.from_messages(messages) | model | StrOutputParser()

                for chunk in chain.stream({}):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")

                response_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"❌ Erreur: {str(e)}"
                response_placeholder.error(full_response)
            
            selected_chat['messages'].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
            })