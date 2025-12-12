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

# --- 2. CSS STYLING ---
st.markdown("""
<style>
    /* Transparent Background */
    .stApp { background: transparent; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { border-right: 1px solid rgba(255, 255, 255, 0.1); }
    
    /* User Message */
    div[data-testid="stChatMessage"][data-testid="user"] {
        background-color: rgba(74, 144, 226, 0.1);
        border: 1px solid rgba(74, 144, 226, 0.2);
        border-radius: 12px;
    }
    
    /* Assistant Message */
    div[data-testid="stChatMessage"][data-testid="assistant"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    
    /* Thinking Animation */
    .thinking {
        font-style: italic;
        color: #888;
        font-size: 0.9em;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    
    /* Input Box */
    .stChatInput textarea { border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2); }
    
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🧠 AI Workspace")
    
    st.caption("MODEL SETTINGS")
    
    # TEXT MODEL
    text_model = st.selectbox(
        "Chat Model (Text)",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0
    )
    
    # VISION MODEL
    vision_model = st.selectbox(
        "Vision Model (Images)",
        ["llama-3.2-90b-vision-preview", "llama-3.2-11b-vision-preview"],
        index=0,
        help="90b is usually smarter but might be slower. 11b is faster."
    )
    
    st.markdown("---")
    typing_speed = st.slider("Response Speed (ms)", 10, 100, 45)
    
    if st.button("🗑️ Reset Chat", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. MAIN CHAT LOGIC ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("### 👋 Intelligent Assistant")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image_url" in msg:
            st.image(msg["image_url"], width=250)
        st.markdown(msg["content"])

# --- INPUT AREA ---
with st.expander("📎 Attach Image (Vision Beta)"):
    uploaded_file = st.file_uploader("Upload image", type=['jpg', 'png', 'jpeg'])

if prompt := st.chat_input("Type your message..."):
    
    # 1. Handle User Input
    user_content = [{"type": "text", "text": prompt}]
    has_image = False
    
    if uploaded_file:
        try:
            base64_image = get_base64_image(uploaded_file)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
            has_image = True
            
            # Show user message immediately
            with st.chat_message("user"):
                st.markdown(prompt)
                st.image(uploaded_file, width=250)
                
            st.session_state.messages.append({"role": "user", "content": prompt + " [Image]", "image_url": uploaded_file})
            
        except Exception as e:
            st.error(f"Failed to process image: {e}")
            st.stop()
    else:
        # Show text message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate Response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("<span class='thinking'>Thinking...</span>", unsafe_allow_html=True)
        time.sleep(0.5) # Cosmetic delay
        
        # Decide Model
        active_model = vision_model if has_image else text_model
        
        # Build Context (Text Only for history to avoid format errors)
        api_messages = [{"role": "system", "content": "You are a helpful AI."}]
        for m in st.session_state.messages[-6:]:
            if "image_url" not in m:
                api_messages.append({"role": m["role"], "content": m["content"]})
        
        # Add Current Request
        api_messages.append({"role": "user", "content": user_content})

        try:
            # API CALL
            stream = client.chat.completions.create(
                model=active_model,
                messages=api_messages,
                stream=True,
                temperature=0.7
            )
            
            full_response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    placeholder.markdown(full_response + "▌")
                    time.sleep(typing_speed / 1000)
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_msg = str(e)
            placeholder.empty()
            if "404" in error_msg:
                st.error(f"❌ **Model Error:** Groq cannot find model `{active_model}`. It might be down for maintenance.")
                st.info("👉 **Try this:** Go to the Sidebar and switch the 'Vision Model' to the other option.")
            elif "400" in error_msg:
                st.error("❌ **Image Error:** The image format was rejected by Groq. Try a smaller JPG or PNG.")
            else:
                st.error(f"❌ **API Error:** {error_msg}")
