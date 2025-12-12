import time
import os
import joblib
import streamlit as st
from google import genai
from dotenv import load_dotenv

# --- PUTANJA DO LOGA ---
# Provjerite je li ova putanja točna u odnosu na vašu glavnu skriptu
LOGO_PATH = "docs/Orizon-com.jpg" 
# ---------------------

# --- NOVE POSTAVKE LOGA ---
LOGO_URL = "https://orizon-aix.com" # Odredišni URL
LOGO_WIDTH = 140 # Postavite širinu loga u pikselima (npr. 140px)
# -----------------------------

# ------------------------------
# Inicijalna konfiguracija Streamlita
# ------------------------------
st.set_page_config(
    page_title="🤖 Gemini Chatbot",
    page_icon="✨",
    layout="wide"
)

# ------------------------------
# Učitavanje API ključa
# ------------------------------
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ Greška: Varijabla okoline GOOGLE_API_KEY nije pronađena. Provjerite svoju .env datoteku.")
    st.stop()

# ------------------------------
# Inicijalizacija Gemini klijenta (Novi SDK) u stanju sesije
# ------------------------------
if "gemini_client" not in st.session_state:
    try:
        st.session_state.gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.error(f"Greška pri inicijalizaciji klijenta: {e}")
        st.stop()

client = st.session_state.gemini_client

# ------------------------------
# Postavke chata
# ------------------------------
MODEL_NAME = "gemini-2.5-flash" 
AI_AVATAR_ICON = "✨"
MODEL_ROLE = "ai"

# ------------------------------
# Priprema podataka
# ------------------------------
os.makedirs("data", exist_ok=True)

# Učitavanje prošlih chatova
try:
    past_chats: dict = joblib.load("data/past_chats_list")
except:
    past_chats = {}

# Jedinstveni ID chata za novu sesiju
new_chat_id = str(time.time())

# ------------------------------
# Bočna traka: Popis chatova + Funkcionalnost preimenovanja
# ------------------------------
with st.sidebar:
    
    st.write("## 📜 Povijest chatova") # Zaglavlje

    options = [new_chat_id] + list(past_chats.keys())
    
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = options[0]

    try:
        current_index = options.index(st.session_state.chat_id)
    except ValueError:
        current_index = 0
    
    selected_chat_id = st.selectbox(
        "Odaberite ili kreirajte chat",
        options=options,
        index=current_index,
        format_func=lambda x: past_chats.get(x, "➕ Novi Chat"),
        key="selectbox_chat" # Dodajemo ključ
    )
    
    st.session_state.chat_id = selected_chat_id

    # Ažuriranje naslova odabranog chata
    if st.session_state.chat_id == new_chat_id:
         st.session_state.chat_title = "Novi Chat"
    elif st.session_state.chat_id in past_chats:
         st.session_state.chat_title = past_chats[st.session_state.chat_id]

    # --- Funkcionalnost preimenovanja chata ---
    if st.session_state.chat_id != new_chat_id:
        st.markdown("---")
        
        new_title = st.text_input(
            "✏️ Preimenuj Chat",
            value=st.session_state.chat_title,
            max_chars=50,
            key="rename_input"
        )
        
        # Logika za spremanje novog imena
        if new_title and new_title != st.session_state.chat_title:
            past_chats[st.session_state.chat_id] = new_title
            st.session_state.chat_title = new_title
            joblib.dump(past_chats, "data/past_chats_list")
            
            # Potrebno za trenutno ažuriranje selectboxa i naslova
            st.toast(f"Chat preimenovan u '{new_title}'", icon='✅')
            
            # Ponovno pokreće skriptu kako bi se prikazalo novo ime
            st.rerun() 

    st.markdown("---")
    st.markdown(f"**Model:** `{MODEL_NAME}`")
    
    # --- POSTAVLJANJE LOGA DOLJE LIJEVO (POSLJEDNJI ELEMENT) ---
    st.markdown("---") # Vizualni separator
    
    if os.path.exists(LOGO_PATH):
        
        # 1. Koristite st.image za lokalno učitavanje slike (Streamlit je prikazuje)
        st.image(LOGO_PATH, width=LOGO_WIDTH)
        
        # 2. Koristite st.markdown za kreiranje linka koji se može kliknuti ODMAH NAKON
        st.markdown(
            f'<div style="text-align: center; margin-top: -10px; margin-bottom: 5px;">'
            f'<a href="{LOGO_URL}" target="_blank" style="font-size:16px; color: grey; text-decoration: none;">Idi na Orizon AI</a>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # Tekst "Powered by Gemini"
        st.markdown(f'<p style="font-size: 10px; color: grey; text-align: center;">Powered by Gemini</p>', unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Logo nije pronađen. Provjerite da datoteka postoji na putanji: `{LOGO_PATH}`")
    # -----------------------------------------------------------------


# ------------------------------
# Glavno područje
# ------------------------------
st.title("🤖 Chat s Geminijem")
st.caption(f"Koristite model **{MODEL_NAME}**.")

# ------------------------------
# Učitavanje povijesti chata za odabrani ID
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
# Inicijalizacija chat sesije (Klijent)
# ------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL_NAME,
        history=st.session_state.gemini_history
    )

# ------------------------------
# Prikaz prošlih poruka
# ------------------------------
for message in st.session_state.messages:
    avatar = message.get("avatar", "👤" if message["role"] == "user" else AI_AVATAR_ICON)
    with st.chat_message(name=message["role"], avatar=avatar):
        st.markdown(message["content"])

# ------------------------------
# Korisnički unos i generiranje odgovora
# ------------------------------
if prompt := st.chat_input("Napišite svoju poruku ovdje..."):

    # 1. Prikažite i spremite poruku korisnika
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    st.session_state.messages.append(
        dict(role="user", content=prompt)
    )

    # 2. Pošaljite poruku u streamingu
    with st.chat_message(name=MODEL_ROLE, avatar=AI_AVATAR_ICON):
        
        try:
            response = st.session_state.chat.send_message_stream(
                prompt
            )
        except Exception as e:
            st.error(f"API greška prilikom slanja poruke: {e}")
            st.stop() 
            
        container = st.empty()
        full_text = ""
        
        # 3. Obradite streaming dijelove (efekt tipkanja)
        for chunk in response:
            if not chunk.text:
                continue
            for word in chunk.text.split(" "):
                full_text += word + " "
                container.write(full_text + "▌")
                time.sleep(0.01)

        container.write(full_text)

    # 4. Spremite poruku asistenta
    st.session_state.messages.append(
        dict(
            role=MODEL_ROLE,
            content=full_text,
            avatar=AI_AVATAR_ICON,
        )
    )

    # 5. Ažurirajte i spremite povijest Geminija
    st.session_state.gemini_history = st.session_state.chat.get_history()
    
    # 6. Spremanje sesije (Pohrana)
    if st.session_state.chat_id not in past_chats:
        # Kada Novi Chat primi prvu poruku, dobiva automatski naslov
        new_title = " ".join(prompt.split()[:5]) + "..."
        past_chats[st.session_state.chat_id] = new_title
        st.session_state.chat_title = new_title
        joblib.dump(past_chats, "data/past_chats_list")

    # Spremite poruke i povijest
    joblib.dump(
        st.session_state.messages,
        f"data/{st.session_state.chat_id}-st_messages",
    )
    joblib.dump(
        st.session_state.gemini_history,
        f"data/{st.session_state.chat_id}-gemini_messages",
    )
    
    # Ponovno pokretanje nije potrebno ovdje ako je chat preimenovan
    st.rerun()