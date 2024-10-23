import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Set up the model
model = genai.GenerativeModel('gemini-1.5-pro')  # Changed to the new model

st.set_page_config(page_title="SaamChat AI", layout="wide")

st.title("SaamChat AI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# File uploader
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="file_uploader")

# Chat input
prompt = st.chat_input("Ask me something...")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display a placeholder for the assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Check if an image was uploaded
            if uploaded_file:
                image = Image.open(uploaded_file)
                
                # Generate response from Gemini with image
                response = model.generate_content([prompt, image])
                full_response = response.text
            else:
                # Generate response from Gemini without image
                response = model.generate_content(prompt, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            message_placeholder.markdown(error_message)
            full_response = error_message

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add some custom CSS to improve the UI
st.markdown("""
<style>
.stApp {
    max-width: 800px;
    margin: 0 auto;
}
.stChatMessage {
    background-color: black;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
}
.stChatMessage.user {
    background-color: black;
}
.stChatInputContainer {
    border-top: 1px solid black;
    padding-top: 20px;
}
</style>
""", unsafe_allow_html=True)
