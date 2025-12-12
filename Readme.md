# ⭐ Gemini Chatbot - Orizon AIX User Interface

## 👨‍💻 Project Lead
**Arnel Kovacevic**

## 🗓️ Project Year
2025 December

---

## 📘 1. Project Overview

This project implements a **Streamlit-based conversational chat interface** that leverages the **Gemini 2.5 Flash** model by Google.

The application is designed to offer a fluid user experience with essential features for professional use:
* **Chat History Management:** Every chat session is saved locally, allowing users to revisit or continue past conversations.
* **Streaming Response:** Model responses are displayed in real-time for dynamic interaction.
* **Custom UI:** Includes specific branding and links for **orizon-aix.com**.

### Key Features
* **AI Model:** `gemini-2.5-flash`
* **UI Framework:** Streamlit
* **Persistence:** History saving using `joblib`
* **Company Link:** [Visit Orizon AIX](https://orizon-aix.com)

---

## 🚀 2. Prerequisites

### 🔧 2.1. Python Dependencies
Ensure you have Python 3.8+ installed. The necessary libraries are:
* `streamlit`
* `google-generativeai` (for the Gemini API)
* `python-dotenv`
* `joblib`

### 🔑 2.2. API Key
A Google Gemini API key is required.
👉 Get it here: https://ai.google.dev/tutorials/setup

---

## ⚙️ 3. Setup and Installation

Follow these steps to set up and run the project locally.

### **3.1. Clone the Repository (or create the folder)**

If you haven't already:
```bash
git clone [INSERT YOUR REPO URL]
cd [PROJECT FOLDER NAME]
```


## 3.2. Create a Virtual Environment and Install Dependencies

# Create and activate the virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
# Windows: .\venv\Scripts\activate
```

# Install required packages
pip install streamlit google-generativeai python-dotenv joblib

## 3.3. Configure the API Key

Create a file named .env in the project's root directory and insert your API key:
```bash
.env
```

# Replace [YOUR API KEY] with your Gemini key
```bash

GOOGLE_API_KEY="[YOUR API KEY]"
```

##  3.4. Prepare File Structure

Ensure the application has the necessary folders:

Create the docs/ directory for the logo:
```bash
mkdir docs
```

Place the your logo file (Orizon-com.jpg) inside docs/.

The data/ directory will be created automatically to save the chat history.

## ▶️ 4. Running the Application
Execute the Streamlit application from your terminal:
```bash
streamlit run app_chat.py
```

## 5. Chat Management

The chat history (st.session_state.messages and st.session_state.gemini_history) is managed using joblib to save state files in the data/ folder. Each new chat gets a unique ID based on the timestamp.

# Example state files:
data/[chat_id]-st_messages
data/[chat_id]-gemini_messages
data/past_chats_list (Dictionary of titles)

