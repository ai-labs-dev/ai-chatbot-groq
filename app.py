import streamlit as st
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Professional AI Assistant",
    page_icon="🤖",
    layout="centered", # 'centered' focuses the chat and looks better on standard screens
    initial_sidebar_state="auto"
)

# --- 2. PROFESSIONAL STYLING ---
# This CSS ensures the input box looks clean and removes any default red borders
st.markdown("""
<style>
    /* Force the input box focus color to a professional blue instead of default red */
    .stChatInput textarea:focus {
        border-color: #4A90E2 !important;
        box-shadow: 0 0 0 1px #4A90E2 !important;
    }
    
    /* Hide the default 'Made with Streamlit' footer for a cleaner look */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. API SETUP ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"⚠️ Configuration Error: Please check your API key.")
    st.stop()

# --- 4. STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("Control Panel")
    
    # A standard, professional button style
    if st.button("🗑️ Reset Conversation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("**Model:** `Llama-3.1-8b-instant`")
    st.caption("A high-speed model optimized for chat.")

# --- 6. MAIN INTERFACE ---

# Professional Header
st.title("AI Assistant")
st.markdown("Welcome. How can I assist you with your tasks today?")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. CHAT LOGIC ---
if prompt := st.chat_input("Type your message here..."):
    
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate Assistant Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Build context for the AI
        messages_for_api = [
            {"role": "system", "content": "You are a helpful and professional AI assistant."}
        ] + st.session_state.messages

        try:
            # Call Groq API with streaming
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages_for_api,
                stream=True,
            )
            
            # Helper function to extract text from the stream safely
            def stream_parser(stream):
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

            # Write the stream to the UI
            full_response = st.write_stream(stream_parser(stream))
            
            # Save the full response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
