import time
import os
import joblib
import streamlit as st
from google import genai
from dotenv import load_dotenv

# --- LOGO PATH ---
# Ensure this path is correct relative to your main script
LOGO_PATH = "docs/Orizon-com.jpg" 
# ---------------------

# --- NEW LOGO SETTINGS ---
LOGO_URL = "https://orizon-aix.com" # The destination URL
LOGO_WIDTH = 140 # Set the logo width in pixels (e.g., 100px)
# -----------------------------

# ------------------------------
# Streamlit Initial Configuration
# ------------------------------
st.set_page_config(
    page_title="🤖 Gemini Chatbot",
    page_icon="✨",
    layout="wide"
)

# ------------------------------
# Load API Key
# ------------------------------
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ Error: GOOGLE_API_KEY environment variable not found. Check your .env file.")
    st.stop()

# ------------------------------
# Initialize Gemini client (New SDK) in session state
# ------------------------------
if "gemini_client" not in st.session_state:
    try:
        st.session_state.gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.error(f"Client initialization error: {e}")
        st.stop()

client = st.session_state.gemini_client

# ------------------------------
# Chat Settings
# ------------------------------
MODEL_NAME = "gemini-2.5-flash" 
AI_AVATAR_ICON = "✨"
MODEL_ROLE = "ai"

# ------------------------------
# Data Preparation
# ------------------------------
os.makedirs("data", exist_ok=True)

# Load past chats
try:
    past_chats: dict = joblib.load("data/past_chats_list")
except:
    past_chats = {}

# Unique chat ID for new session
new_chat_id = str(time.time())

# ------------------------------
# Sidebar Chat List + Rename Functionality
# ------------------------------
with st.sidebar:
    
    st.write("## 📜 Chat History") # The header is here

    options = [new_chat_id] + list(past_chats.keys())
    
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = options[0]

    try:
        current_index = options.index(st.session_state.chat_id)
    except ValueError:
        current_index = 0
    
    selected_chat_id = st.selectbox(
        "Select or create a chat",
        options=options,
        index=current_index,
        format_func=lambda x: past_chats.get(x, "➕ New Chat"),
        key="selectbox_chat" # Adding a key
    )
    
    st.session_state.chat_id = selected_chat_id

    # Update the title of the selected chat
    if st.session_state.chat_id == new_chat_id:
         st.session_state.chat_title = "New Chat"
    elif st.session_state.chat_id in past_chats:
         st.session_state.chat_title = past_chats[st.session_state.chat_id]

    # --- Rename Chat Functionality ---
    if st.session_state.chat_id != new_chat_id:
        st.markdown("---")
        
        new_title = st.text_input(
            "✏️ Rename Chat",
            value=st.session_state.chat_title,
            max_chars=50,
            key="rename_input"
        )
        
        # Logic to save the new name
        if new_title and new_title != st.session_state.chat_title:
            past_chats[st.session_state.chat_id] = new_title
            st.session_state.chat_title = new_title
            joblib.dump(past_chats, "data/past_chats_list")
            
            # Necessary to immediately update the selectbox and title
            st.toast(f"Chat renamed to '{new_title}'", icon='✅')
            
            # 🟢 CORREZIONE APPLICATA: st.rerun() è la funzione corretta
            st.rerun() # Reruns the script to show the new name

    st.markdown("---")
    st.markdown(f"**Model:** `{MODEL_NAME}`")
    
    # --- LOGO PLACEMENT AT THE BOTTOM LEFT (LAST ELEMENT) ---
    st.markdown("---") # Visual separator
    
    if os.path.exists(LOGO_PATH):
        
        # 1. Use st.image to load the image locally (Streamlit displays it)
        # st.image is not clickable, so we just display it:
        st.image(LOGO_PATH, width=LOGO_WIDTH)
        
        # 2. Use st.markdown to create a clickable link RIGHT AFTER
        # (Ideally we want the image to be clickable, but this is a good compromise)
        st.markdown(
            f'<div style="text-align: center; margin-top: -10px; margin-bottom: 5px;">'
            f'<a href="{LOGO_URL}" target="_blank" style="font-size:16px; color: grey; text-decoration: none;">Go to Orizon AI</a>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # If you want the image *and* the "Powered by Gemini" text:
        st.markdown(f'<p style="font-size: 10px; color: grey; text-align: center;">Powered by Gemini</p>', unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Logo not found. Ensure the file exists at path: `{LOGO_PATH}`")
    # -----------------------------------------------------------------


# ------------------------------
# Main Area
# ------------------------------
st.title("🤖 Chat with Gemini")
st.caption(f"You are using the **{MODEL_NAME}** model.")

# ------------------------------
# Load chat history for the selected ID
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
# Initialize chat session (Client)
# ------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL_NAME,
        history=st.session_state.gemini_history
    )

# ------------------------------
# Display past messages
# ------------------------------
for message in st.session_state.messages:
    avatar = message.get("avatar", "👤" if message["role"] == "user" else AI_AVATAR_ICON)
    with st.chat_message(name=message["role"], avatar=avatar):
        st.markdown(message["content"])

# ------------------------------
# User Input and Response Generation
# ------------------------------
if prompt := st.chat_input("Write your message here..."):

    # 1. Display and save the user's message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    st.session_state.messages.append(
        dict(role="user", content=prompt)
    )

    # 2. Send the message in streaming
    with st.chat_message(name=MODEL_ROLE, avatar=AI_AVATAR_ICON):
        
        try:
            response = st.session_state.chat.send_message_stream(
                prompt
            )
        except Exception as e:
            st.error(f"API Error while sending message: {e}")
            st.stop() 
            
        container = st.empty()
        full_text = ""
        
        # 3. Process the streaming chunks (typing effect)
        for chunk in response:
            if not chunk.text:
                continue
            for word in chunk.text.split(" "):
                full_text += word + " "
                container.write(full_text + "▌")
                time.sleep(0.01)

        container.write(full_text)
        

    # 4. Save the assistant's message
    st.session_state.messages.append(
        dict(
            role=MODEL_ROLE,
            content=full_text,
            avatar=AI_AVATAR_ICON,
        )
    )

    # 5. Update and save Gemini history
    st.session_state.gemini_history = st.session_state.chat.get_history()
    
    # 6. Save the session (Storage)
    if st.session_state.chat_id not in past_chats:
        # When a New Chat receives the first message, it is given an automatic title
        new_title = " ".join(prompt.split()[:5]) + "..."
        past_chats[st.session_state.chat_id] = new_title
        st.session_state.chat_title = new_title
        joblib.dump(past_chats, "data/past_chats_list")

    # Save messages and history
    joblib.dump(
        st.session_state.messages,
        f"data/{st.session_state.chat_id}-st_messages",
    )
    joblib.dump(
        st.session_state.gemini_history,
        f"data/{st.session_state.chat_id}-gemini_messages",
    )
    
    # Rerunning is not necessary here if the chat has been renamed
    st.rerun()