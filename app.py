import streamlit as st
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Initialize Groq Client
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 GROQ_API_KEY not found in secrets.toml")
    st.stop()

# --- CUSTOM STYLES (Professional Dark Mode) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Input Box Styling */
    .stChatInput {
        position: fixed;
        bottom: 20px;
    }
    
    /* Header Adjustment */
    header {visibility: hidden;}
    
    /* Clean up top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (Optional Controls) ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("Model: `llama-3.1-8b-instant`")
    
    # Add a clear chat button
    if st.button("🗑️ Clear Conversation", type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN CHAT INTERFACE ---

st.title("🤖 AI Assistant")
st.caption("Powered by Groq & Llama 3")

# 1. Display existing chat history
# This loops through the history and displays it cleanly
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Handle User Input
if prompt := st.chat_input("Type your message here..."):
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Generate and Display Assistant Response
    with st.chat_message("assistant"):
        
        # Prepare context for the AI
        chat_history = [
            {"role": "system", "content": "You are a helpful, professional AI assistant."}
        ]
        # Append the last few messages for context (context window management)
        for msg in st.session_state.messages[-10:]:
            chat_history.append(msg)

        try:
            # Create a placeholder for the streaming text
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=chat_history,
                stream=True, # Enable streaming for "typing" effect
            )
            
            # Streamlit's magic command to write stream directly
            response = st.write_stream(stream)
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error generating response: {e}")
