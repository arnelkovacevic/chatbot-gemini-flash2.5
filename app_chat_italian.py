import time
import os
import joblib
import streamlit as st
from google import genai
from dotenv import load_dotenv

# --- PERCORSO LOGO ---
# Assicurati che questo percorso sia corretto rispetto al tuo script principale
LOGO_PATH = "docs/Orizon-com.jpg" 
# ---------------------

# --- NUOVE IMPOSTAZIONI LOGO ---
LOGO_URL = "https://orizon-aix.com" # L'URL di destinazione
LOGO_WIDTH = 140 # Imposta la larghezza del logo in pixel (es. 140px)
# -----------------------------

# ------------------------------
# Configurazione Iniziale di Streamlit
# ------------------------------
st.set_page_config(
    page_title="🤖 Chatbot Gemini",
    page_icon="✨",
    layout="wide"
)

# ------------------------------
# Carica Chiave API
# ------------------------------
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ Errore: Variabile d'ambiente GOOGLE_API_KEY non trovata. Controlla il tuo file .env.")
    st.stop()

# ------------------------------
# Inizializza client Gemini (Nuovo SDK) nello stato di sessione
# ------------------------------
if "gemini_client" not in st.session_state:
    try:
        st.session_state.gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.error(f"Errore di inizializzazione del client: {e}")
        st.stop()

client = st.session_state.gemini_client

# ------------------------------
# Impostazioni Chat
# ------------------------------
MODEL_NAME = "gemini-2.5-flash" 
AI_AVATAR_ICON = "✨"
MODEL_ROLE = "ai"

# ------------------------------
# Preparazione Dati
# ------------------------------
os.makedirs("data", exist_ok=True)

# Carica chat precedenti
try:
    past_chats: dict = joblib.load("data/past_chats_list")
except:
    past_chats = {}

# ID chat univoco per nuova sessione
new_chat_id = str(time.time())

# ------------------------------
# Sidebar Elenco Chat + Funzione Rinomina
# ------------------------------
with st.sidebar:
    
    st.write("## 📜 Storico Chat") # Intestazione

    options = [new_chat_id] + list(past_chats.keys())
    
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = options[0]

    try:
        current_index = options.index(st.session_state.chat_id)
    except ValueError:
        current_index = 0
    
    selected_chat_id = st.selectbox(
        "Seleziona o crea una chat",
        options=options,
        index=current_index,
        format_func=lambda x: past_chats.get(x, "➕ Nuova Chat"),
        key="selectbox_chat" # Aggiungiamo una chiave
    )
    
    st.session_state.chat_id = selected_chat_id

    # Aggiorna il titolo della chat selezionata
    if st.session_state.chat_id == new_chat_id:
         st.session_state.chat_title = "Nuova Chat"
    elif st.session_state.chat_id in past_chats:
         st.session_state.chat_title = past_chats[st.session_state.chat_id]

    # --- Funzionalità Rinomina Chat ---
    if st.session_state.chat_id != new_chat_id:
        st.markdown("---")
        
        new_title = st.text_input(
            "✏️ Rinomina Chat",
            value=st.session_state.chat_title,
            max_chars=50,
            key="rename_input"
        )
        
        # Logica per salvare il nuovo nome
        if new_title and new_title != st.session_state.chat_title:
            past_chats[st.session_state.chat_id] = new_title
            st.session_state.chat_title = new_title
            joblib.dump(past_chats, "data/past_chats_list")
            
            # Necessario per aggiornare immediatamente la selectbox e il titolo
            st.toast(f"Chat rinominata in '{new_title}'", icon='✅')
            
            # Ricarica lo script per mostrare il nuovo nome
            st.rerun() 

    st.markdown("---")
    st.markdown(f"**Modello:** `{MODEL_NAME}`")
    
    # --- INSERIMENTO LOGO IN BASSO A SINISTRA (ULTIMO ELEMENTO) ---
    st.markdown("---") # Separatore visivo
    
    if os.path.exists(LOGO_PATH):
        
        # 1. Usa st.image per caricare l'immagine localmente (Streamlit la visualizza)
        st.image(LOGO_PATH, width=LOGO_WIDTH)
        
        # 2. Usa st.markdown per creare un link cliccabile SUBITO DOPO
        st.markdown(
            f'<div style="text-align: center; margin-top: -10px; margin-bottom: 5px;">'
            f'<a href="{LOGO_URL}" target="_blank" style="font-size:16px; color: grey; text-decoration: none;">Vai a Orizon AI</a>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # Testo "Powered by Gemini"
        st.markdown(f'<p style="font-size: 10px; color: grey; text-align: center;">Powered by Gemini</p>', unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Logo non trovato. Assicurati che il file esista al percorso: `{LOGO_PATH}`")
    # -----------------------------------------------------------------


# ------------------------------
# Area Principale
# ------------------------------
st.title("🤖 Chat con Gemini")
st.caption(f"Stai usando il modello **{MODEL_NAME}**.")

# ------------------------------
# Carica cronologia chat per l'ID selezionato
# ------------------------------
try:
    st.session_state.messages = joblib.load(
        f"data/{st.session_state.chat_id}-st_messages"
    )
    st.session_state.gemini_history = joblib.load(
        f"data/{st.session_state.chat_id}-gemini_messages"
    )
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []
    if "chat" in st.session_state:
         del st.session_state.chat

# ------------------------------
# Inizializza sessione chat (Client)
# ------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL_NAME,
        history=st.session_state.gemini_history
    )

# ------------------------------
# Visualizza messaggi passati
# ------------------------------
for message in st.session_state.messages:
    avatar = message.get("avatar", "👤" if message["role"] == "user" else AI_AVATAR_ICON)
    with st.chat_message(name=message["role"], avatar=avatar):
        st.markdown(message["content"])

# ------------------------------
# Input Utente e Generazione Risposta
# ------------------------------
if prompt := st.chat_input("Scrivi qui il tuo messaggio..."):

    # 1. Visualizza e salva il messaggio dell'utente
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    st.session_state.messages.append(
        dict(role="user", content=prompt)
    )

    # 2. Invia il messaggio in streaming
    with st.chat_message(name=MODEL_ROLE, avatar=AI_AVATAR_ICON):
        
        try:
            response = st.session_state.chat.send_message_stream(
                prompt
            )
        except Exception as e:
            st.error(f"Errore API durante l'invio del messaggio: {e}")
            st.stop() 
            
        container = st.empty()
        full_text = ""
        
        # 3. Processa i chunk in streaming (effetto digitazione)
        for chunk in response:
            if not chunk.text:
                continue
            for word in chunk.text.split(" "):
                full_text += word + " "
                container.write(full_text + "▌")
                time.sleep(0.01)

        container.write(full_text)

    # 4. Salva il messaggio dell'assistente
    st.session_state.messages.append(
        dict(
            role=MODEL_ROLE,
            content=full_text,
            avatar=AI_AVATAR_ICON,
        )
    )

    # 5. Aggiorna e salva la cronologia di Gemini
    st.session_state.gemini_history = st.session_state.chat.get_history()
    
    # 6. Salvataggio della sessione (Storage)
    if st.session_state.chat_id not in past_chats:
        # Quando una Nuova Chat riceve il primo messaggio, le viene dato un titolo automatico
        new_title = " ".join(prompt.split()[:5]) + "..."
        past_chats[st.session_state.chat_id] = new_title
        st.session_state.chat_title = new_title
        joblib.dump(past_chats, "data/past_chats_list")

    # Salva messaggi e cronologia
    joblib.dump(
        st.session_state.messages,
        f"data/{st.session_state.chat_id}-st_messages",
    )
    joblib.dump(
        st.session_state.gemini_history,
        f"data/{st.session_state.chat_id}-gemini_messages",
    )
    
    # Ricarica lo script se necessario (già corretto)
    st.rerun()