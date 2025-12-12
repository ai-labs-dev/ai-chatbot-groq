import streamlit as st
from groq import Groq
from gtts import gTTS
import time
import base64
import io

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Thinklet AI",
    page_icon="🌼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE "THINKLET" UI STYLING (Yellow/White Theme) ---
st.markdown("""
<style>
    /* Main Background - Light Mode Force */
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
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #FFD54F; /* Yellow */
        color: black;
        border-radius: 20px;
        padding: 10px;
        border: none;
    }
    
    /* Assistant Message - White Card style */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 20px;
        padding: 10px;
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
    .stButton button:hover {
        background-color: #FFC107;
    }

    /* Hide Footer */
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---

def get_base64_image(file_obj):
    """Convert uploaded file to base64 for the API"""
    if file_obj:
        return base64.b64encode(file_obj.getvalue()).decode('utf-8')
    return None

def text_to_speech(text):
    """Convert text to speech audio using gTTS"""
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except Exception as e:
        st.error(f"Audio Error: {e}")
        return None

# --- 4. SETUP CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ GROQ_API_KEY missing in secrets.toml")
    st.stop()

# --- 5. SIDEBAR (Dashboard Navigation) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=50)
    st.title("Thinklet")
    
    st.markdown("### 📂 My Workspaces")
    st.button("📝 UX Writing Guide", use_container_width=True)
    st.button("📊 Q3 Marketing Plan", use_container_width=True)
    st.button("💻 Python Scripts", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Capabilities")
    enable_voice = st.toggle("Enable Voice Response", value=False)
    typing_speed = st.slider("Typing Speed (ms)", 10, 100, 30)
    
    st.markdown("---")
    # UPGRADE BANNER
    st.markdown("""
    <div style='background-color: #FFE082; padding: 15px; border-radius: 10px; color: black; text-align: center;'>
        <strong>🚀 Upgrade to Pro</strong><br>
        <span style='font-size: 12px;'>Unlock reasoning & custom features.</span>
    </div>
    """, unsafe_allow_html=True)

# --- 6. MAIN CHAT LOGIC ---

# Initialize State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title Area
st.markdown("## 🤖 AI Chat Helper")
st.caption("Capabilities: 👁️ Vision | 🎨 Image Gen | 🗣️ Voice | ✍️ Text")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Check if message contains an image URL (for generated images)
        if "image_url" in msg:
            st.image(msg["image_url"])
        st.markdown(msg["content"])
        # Check if message has audio
        if "audio" in msg:
            st.audio(msg["audio"], format='audio/mp3')

# --- INPUT AREA (Voice + Text + Image) ---

# 1. Image Uploader (Collapsible to keep UI clean)
with st.expander("📷 Upload Image for Analysis"):
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg'])

# 2. Input Box
prompt = st.chat_input("Type a message or describe an image...")

# 3. Logic
if prompt:
    
    # --- A. HANDLE USER INPUT ---
    user_content = [{"type": "text", "text": prompt}]
    
    # If image is attached, process it for Vision Model
    if uploaded_file:
        base64_image = get_base64_image(uploaded_file)
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })
        st.session_state.messages.append({"role": "user", "content": prompt + " [Image Uploaded]"})
        # Show immediate user feedback
        with st.chat_message("user"):
            st.markdown(prompt)
            st.image(uploaded_file, width=200)
            
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # --- B. DETERMINE INTENT (Generate Image vs Chat) ---
    
    if "generate image" in prompt.lower() or "create an image" in prompt.lower():
        # --- IMAGE GENERATION PATH ---
        with st.chat_message("assistant"):
            st.markdown("🎨 **Generating your masterpiece...**")
            
            # We use Pollinations AI (Free API) for demo purposes
            # Logic: We encode the prompt into the URL
            img_prompt = prompt.replace("generate image", "").replace("create an image", "").strip()
            image_url = f"https://image.pollinations.ai/prompt/{img_prompt}?nologo=true"
            
            # Display
            st.image(image_url, caption=f"Generated: {img_prompt}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Here is your image for: {img_prompt}",
                "image_url": image_url
            })

    else:
        # --- TEXT/VISION CHAT PATH ---
        with st.chat_message("assistant"):
            status_text = st.empty()
            status_text.markdown("typing...") # Fake typing indicator
            
            # Choose Model: Vision if image uploaded, else Text
            model_choice = "llama-3.2-11b-vision-preview" if uploaded_file else "llama-3.1-8b-instant"
            
            # Prepare API Messages
            api_messages = [
                {"role": "system", "content": "You are a helpful, friendly AI assistant."}
            ]
            # Add simple history (excluding complex image history for this demo to save tokens)
            for m in st.session_state.messages[-5:]: 
                if "image_url" not in m: # Avoid re-sending generated image URLs to text model
                    api_messages.append({"role": m["role"], "content": m["content"]})
            
            # Add current query
            api_messages.append({"role": "user", "content": user_content if uploaded_file else prompt})

            try:
                stream = client.chat.completions.create(
                    model=model_choice,
                    messages=api_messages,
                    stream=True
                )
                
                # Manual Streaming with Delay (The "Slow" Effect)
                full_response = ""
                response_placeholder = st.empty()
                
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(typing_speed / 1000) # Control speed here
                
                response_placeholder.markdown(full_response)
                
                # --- VOICE REPLY ---
                audio_data = None
                if enable_voice:
                    audio_fp = text_to_speech(full_response)
                    if audio_fp:
                        st.audio(audio_fp, format='audio/mp3')
                        # Note: We don't save binary audio to history in this simple demo to avoid memory bloat
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Error: {e}")
