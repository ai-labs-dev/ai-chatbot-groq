import streamlit as st
from groq import Groq

# --- 1. CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="Gemini-Pro Clone",
    page_icon="✨",
    layout="wide",  # This makes the input bar longer
    initial_sidebar_state="collapsed"
)

# --- 2. CSS STYLING (Gemini Dark Theme) ---
st.markdown("""
<style>
    /* Gemini Dark Background */
    .stApp {
        background-color: #131314;
        color: #E3E3E3;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1E1F20;
    }

    /* Input Bar Styling - Make it blend in */
    .stChatInput textarea {
        background-color: #1E1F20;
        color: white;
        border: 1px solid #444746;
    }
    
    /* Remove the top padding to make it look like an app */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Hide the default hamburger menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 3. API SETUP ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"⚠️ API Key Error: Please check your secrets.toml file.")
    st.stop()

# --- 4. STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("✨ Settings")
    
    # Simple clear button (No red color)
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Model: Llama-3.1-8b-instant")

# --- 6. MAIN CHAT AREA ---

# Header (Centered like Gemini)
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style='text-align: center; margin-top: 100px;'>
        <h1 style='background: linear-gradient(to right, #4285F4, #9B72CB); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Hello, Human.</h1>
        <h3 style='color: #888;'>How can I help you today?</h3>
    </div>
    """, unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. INPUT & LOGIC (The Fix) ---
if prompt := st.chat_input("Message Gemini..."):
    
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response
    with st.chat_message("assistant"):
        # Create a container for the result
        response_placeholder = st.empty()
        
        # Build context
        messages_for_api = [
            {"role": "system", "content": "You are a helpful, smart AI assistant. Be concise and friendly."}
        ] + st.session_state.messages

        try:
            # Call Groq API with streaming
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages_for_api,
                stream=True,
            )
            
            # --- THE CRITICAL FIX --- 
            # We must iterate the stream and extract ONLY the text content
            def stream_generator():
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

            # Write the clean text stream
            full_response = st.write_stream(stream_generator())
            
            # Save assistant message
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error: {str(e)}")
