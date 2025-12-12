import streamlit as st
from groq import Groq
import time
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="AI ChatBot",
    page_icon="🫶🏻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE "THINKLET" UI STYLING (Yellow/White Theme) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #F8F9FA;
        color: #212529;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E9ECEF;
    }
    
    /* User Message - The Yellow Bubble */
    div[data-testid="stChatMessage"] {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    div[data-testid="stChatMessage"][data-testid="user"] {
        background-color: #FFD54F;
        color: black;
    }
    
    /* Assistant Message - White Card style */
    div[data-testid="stChatMessage"][data-testid="assistant"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Input Box Styling */
    .stChatInput textarea {
        background-color: #FFFFFF;
        color: #333;
        border: 2px solid #E0E0E0;
        border-radius: 12px;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #FFD54F;
        color: black;
        border-radius: 8px;
        border: none;
        font-weight: 600;
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
    st.error("⚠️ GROQ_API_KEY missing in secrets.toml")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🫶🏻 ChatBot")
    st.markdown("### 📂 Workspaces")
    st.button("📝 UX Writing Guide", use_container_width=True)
    st.button("📊 Q3 Marketing Plan", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Controls")
    # Removed Voice Toggle to prevent errors
    typing_speed = st.slider("Typing Speed (ms)", 5, 50, 20)
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. MAIN CHAT LOGIC ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Title Area
st.markdown("## 🤖 AI Companion")
st.caption("Context aware AI Assistant")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image_url" in msg:
            st.image(msg["image_url"])
        st.markdown(msg["content"])

# --- INPUT AREA ---
# Image Uploader
with st.expander("📷 Upload Image (Optional)"):
    uploaded_file = st.file_uploader("Attach an image", type=['jpg', 'png'])

# Chat Input
if prompt := st.chat_input("Type your message..."):
    
    # 1. Handle User Input
    user_content = [{"type": "text", "text": prompt}]
    
    if uploaded_file:
        base64_image = get_base64_image(uploaded_file)
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })
        st.session_state.messages.append({"role": "user", "content": prompt + " [Image Uploaded]"})
        with st.chat_message("user"):
            st.markdown(prompt)
            st.image(uploaded_file, width=200)
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
        
        # Prepare Messages for API
        api_messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
        # Only add text history to avoid token errors with images
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
            
            # 3. Stream the Response (Fixing the JSON bug)
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(typing_speed / 1000) # Typing effect
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error: {e}")
