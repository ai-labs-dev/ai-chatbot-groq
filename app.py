import streamlit as st
from groq import Groq
import time
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Professional AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PROFESSIONAL ADAPTIVE STYLING ---
# This CSS uses transparent backgrounds so it matches ANY Streamlit theme automatically.
st.markdown("""
<style>
    /* 1. Main Background - Transparent to let Streamlit theme show */
    .stApp {
        background: transparent;
    }
    
    /* 2. Sidebar - Subtle, Professional Border */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 3. User Chat Message - Professional Blue Accent */
    div[data-testid="stChatMessage"][data-testid="user"] {
        background-color: rgba(74, 144, 226, 0.1); /* Subtle Blue Tint */
        border: 1px solid rgba(74, 144, 226, 0.2);
        border-radius: 12px;
    }
    
    /* 4. Assistant Chat Message - Clean Neutral */
    div[data-testid="stChatMessage"][data-testid="assistant"] {
        background-color: rgba(255, 255, 255, 0.05); /* Subtle White/Grey Tint */
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    
    /* 5. Input Box - Matches Theme */
    .stChatInput textarea {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* 6. Buttons - Professional & Minimal */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.2s;
    }
    .stButton button:hover {
        border-color: #4A90E2; /* Blue hover glow */
        color: #4A90E2;
    }
    
    /* Remove default top padding */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Hide Footer */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_base64_image(file_obj):
    if file_obj:
        return base64.b64encode(file_obj.getvalue()).decode('utf-8')
    return None

# --- 4. SETUP CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ GROQ_API_KEY missing. Please check your secrets.toml.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🧠 AI Workspace")
    
    st.caption("PROJECTS")
    st.button("📄 Document Analysis", use_container_width=True)
    st.button("📊 Market Research", use_container_width=True)
    st.button("💻 Code Assistant", use_container_width=True)
    
    st.markdown("---")
    st.caption("SETTINGS")
    
    # Speed Control
    typing_speed = st.slider("Response Speed (ms)", 5, 50, 20)
    
    # Clear Chat Button (Primary color used for emphasis)
    if st.button("🗑️ Reset Conversation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. MAIN CHAT INTERFACE ---

# Initialize History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("### 👋 Welcome Back")
st.markdown("I am your professional AI assistant. Attach images or type below to begin.")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image_url" in msg:
            st.image(msg["image_url"])
        st.markdown(msg["content"])

# --- INPUT AREA ---

# Image Uploader (Clean expander)
with st.expander("📎 Attach Image (Optional)"):
    uploaded_file = st.file_uploader("Upload an image for analysis", type=['jpg', 'png', 'jpeg'])

# Chat Input
if prompt := st.chat_input("Type your message here..."):
    
    # 1. Handle User Input
    user_content = [{"type": "text", "text": prompt}]
    
    # Prepare visual display
    if uploaded_file:
        base64_image = get_base64_image(uploaded_file)
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })
        st.session_state.messages.append({"role": "user", "content": prompt + " [Image Attached]"})
        
        # Immediate Feedback
        with st.chat_message("user"):
            st.markdown(prompt)
            st.image(uploaded_file, width=250) # Smaller, cleaner preview
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Select Model (Vision or Text)
        model_choice = "llama-3.2-11b-vision-preview" if uploaded_file else "llama-3.1-8b-instant"
        
        # Build API Messages (Text History Only to save tokens/errors)
        api_messages = [
            {"role": "system", "content": "You are a precise, professional AI assistant."}
        ]
        for m in st.session_state.messages[-5:]:
            if "image_url" not in m:
                api_messages.append({"role": m["role"], "content": m["content"]})
        
        api_messages.append({"role": "user", "content": user_content if uploaded_file else prompt})

        try:
            stream = client.chat.completions.create(
                model=model_choice,
                messages=api_messages,
                stream=True
            )
            
            # Streaming Loop
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(typing_speed / 1000)
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error: {e}")
