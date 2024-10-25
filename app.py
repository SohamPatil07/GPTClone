import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
from docx import Document

# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Set up the model
model = genai.GenerativeModel('gemini-1.5-pro')

st.set_page_config(page_title="SaamChat AI", layout="wide")

# Initialize session state
if "chats" not in st.session_state:
    st.session_state.chats = [{"id": 0, "name": "Chat 1", "messages": []}]
if "current_chat" not in st.session_state:
    st.session_state.current_chat = 0

# Function to delete a chat
def delete_chat(chat_id):
    st.session_state.chats = [chat for chat in st.session_state.chats if chat['id'] != chat_id]
    if not st.session_state.chats:
        st.session_state.chats = [{"id": 0, "name": "Chat 1", "messages": []}]
    st.session_state.current_chat = st.session_state.chats[0]['id']

# Function to create a new chat
def create_new_chat():
    new_chat_id = max([chat['id'] for chat in st.session_state.chats]) + 1
    st.session_state.chats.append({"id": new_chat_id, "name": f"Chat {new_chat_id + 1}", "messages": []})
    st.session_state.current_chat = new_chat_id

# Function to extract text from PDF
def extract_text_from_pdf(file):
    return " ".join(page.extract_text() for page in PyPDF2.PdfReader(file).pages)

# Function to extract text from Word document
def extract_text_from_docx(file):
    return "\n".join(para.text for para in Document(file).paragraphs)

# Sidebar
with st.sidebar:
    st.title("Chat History")
    
    for chat in st.session_state.chats:
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(chat['name'], key=f"chat_{chat['id']}", use_container_width=True):
                st.session_state.current_chat = chat['id']
        with col2:
            if st.button("🗑️", key=f"delete_{chat['id']}", help="Delete chat"):
                delete_chat(chat['id'])
                st.experimental_rerun()

    if st.button("New Chat", use_container_width=True):
        create_new_chat()
        st.experimental_rerun()

# Main chat interface
st.title("SaamChat AI")

current_chat = next((chat for chat in st.session_state.chats if chat['id'] == st.session_state.current_chat), None)
if current_chat:
    # Display messages
    for message in current_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # File uploader
    uploaded_file = st.file_uploader("Upload an image, PDF, or Word document", type=["png", "jpg", "jpeg", "pdf", "docx"])

    # Chat input
    prompt = st.chat_input("Ask me something...")

    if prompt:
        current_chat["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                if uploaded_file:
                    file_type = uploaded_file.type
                    if file_type.startswith('image'):
                        image = Image.open(uploaded_file)
                        response = model.generate_content([prompt, image], stream=True)
                    elif file_type == 'application/pdf':
                        text = extract_text_from_pdf(uploaded_file)
                        response = model.generate_content([prompt, text], stream=True)
                    elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                        text = extract_text_from_docx(uploaded_file)
                        response = model.generate_content([prompt, text], stream=True)
                else:
                    response = model.generate_content(prompt, stream=True)

                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                current_chat["messages"].append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
else:
    st.write("No chat selected. Please create a new chat or select an existing one.")

# Add custom CSS for styling
st.markdown("""
<style>
body {
    color: #ffffff;
    background-color: #0e1117;
}
.stSidebar {
    background-color: #262730;
    padding: 1rem;
}
.stSidebar .stButton > button {
    background-color: transparent;
    border: 1px solid #4a4a4a;
    color: #ffffff;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    border-radius: 0.375rem;
    transition: all 0.2s;
    margin: 0.25rem 0;
    width: 100%;
    text-align: left;
}
.stSidebar .stButton > button:hover {
    background-color: #3a3a3a;
}
.stChatMessage {
    background-color: #262730;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.stChatMessage.user {
    background-color: #1e1e1e;
}
.stChatInputContainer {
    border-top: 1px solid #4a4a4a;
    padding-top: 1rem;
    margin-top: 1rem;
}
.main .block-container {
    max-width: 800px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.stTextInput > div > div > input {
    color: #ffffff;
    background-color: #3a3a3a;
}
.stMarkdown {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)
