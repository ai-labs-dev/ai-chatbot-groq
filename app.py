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

# --- 2. CSS STYLING (Adaptive & Professional) ---
st.markdown("""
<style>
    /* Transparent Background for Theme Compatibility */
    .stApp {
        background: transparent;
    }
    
    /* Sidebar Border */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* User Message - Blue Tint */
    div[data-testid="stChatMessage"][data-testid="user"] {
        background-color: rgba(74, 144, 226, 0.1);
        border: 1px solid rgba(74, 144, 226, 0.2);
        border-radius: 12px;
    }
    
    /* Assistant Message - Neutral Tint */
    div[data-testid="stChatMessage"][data-testid="assistant"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    
    /* Thinking Animation Style */
    .thinking {
        font-style: italic;
        color: #888;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    
    /* Input Box */
    .stChatInput textarea {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    /* Hide Footer */
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem;}
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

# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🧠 AI Workspace")
    
    st.caption("MODEL SETTINGS")
    text_model = st.selectbox(
        "Text Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        index=0
    )
    
    vision_model = st.selectbox(
        "Vision Model",
        ["llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview"],
        index=1
    )
    
    st.markdown("---")
    st.caption("INTERFACE")
    # Set default to 45ms as requested
    typing_speed = st.slider("Response Speed (ms)", 10, 100, 45)
    
    if st.button("🗑️ Reset Conversation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. MAIN CHAT LOGIC ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("### 👋 Intelligent Assistant")
st.markdown(f"Using **{vision_model if 'messages' in st.session_state and len(st.session_state.messages) > 0 and 'image_url' in str(st.session_state.messages) else text_model}** logic.")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image_url" in msg:
            st.image(msg["image_url"])
        st.markdown(msg["content"])

# --- INPUT AREA ---
with st.expander("📎 Attach Image"):
    uploaded_file = st.file_uploader("Analyze an image", type=['jpg', 'png', 'jpeg'])

if prompt := st.chat_input("Type your message..."):
    
    # 1. Handle User Input
    user_content = [{"type": "text", "text": prompt}]
    
    if uploaded_file:
        base64_image = get_base64_image(uploaded_file)
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })
        st.session_state.messages.append({"role": "user", "content": prompt + " [Image Attached]"})
        with st.chat_message("user"):
            st.markdown(prompt)
            st.image(uploaded_file, width=250)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        # A. Thinking Animation
        response_placeholder = st.empty()
        response_placeholder.markdown("<span class='thinking'>Thinking...</span>", unsafe_allow_html=True)
        
        # Artificial delay to make the 'Thinking' visible and feel natural (optional)
        time.sleep(0.5) 
        
        full_response = ""
        active_model = vision_model if uploaded_file else text_model
        
        # Build API Messages
        api_messages = [
            {"role": "system", "content": "You are a helpful, professional AI assistant."}
        ]
        for m in st.session_state.messages[-5:]:
            if "image_url" not in m:
                api_messages.append({"role": m["role"], "content": m["content"]})
        
        api_messages.append({"role": "user", "content": user_content if uploaded_file else prompt})

        try:
            stream = client.chat.completions.create(
                model=active_model,
                messages=api_messages,
                stream=True
            )
            
            # B. Stream Parsing with Speed Control
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    # Overwrite the 'Thinking...' with the actual text
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(typing_speed / 1000)
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            response_placeholder.empty() # Clear thinking animation if error
            st.error(f"❌ API Error: {str(e)}")
