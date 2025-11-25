import streamlit as st
from groq import Groq

# CONFIG 
client = Groq(api_key=st.secrets["Api_key"])
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

#STYLES
st.markdown("""
<style>

body {
    background-color: #0f0f10;
}

h2 {
    color: #f2f2f2;
    font-weight: 600;
}

.chat-wrapper {
    max-width: 900px;
    margin: auto;
    padding-top: 20px;
}

.chat-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 18px;
    height: 70vh;
    overflow-y: auto;
    backdrop-filter: blur(8px);
}

.user-msg {
    background: #006ee6;
    color: white;
    padding: 12px 16px;
    border-radius: 14px;
    max-width: 75%;
    margin-left: auto;
    margin-bottom: 12px;
    font-size: 16px;
}

.bot-msg {
    background: #eaeaea;
    color: #111;
    padding: 12px 16px;
    border-radius: 14px;
    max-width: 75%;
    margin-right: auto;
    margin-bottom: 12px;
    font-size: 16px;
}

.input-area {
    max-width: 900px;
    margin: 22px auto;
}

</style>
""", unsafe_allow_html=True)

#STATE 
if "history" not in st.session_state:
    st.session_state.history = []


#  MODEL LOGIC 
def ask_groq(query, history):
    messages = [{"role": "system", "content": "You are a helpful, friendly AI assistant."}]

    for h in history[-6:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["bot"]})

    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    return response.choices[0].message.content


#FRONT-END
st.markdown("<h2 style='text-align:center;'>🤖 AI Chatbot</h2>", unsafe_allow_html=True)

st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)


#CHAT DISPLAY (FIXED)

# Only show the chat box if there are messages
if len(st.session_state.history) > 0:

    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

# CHAT AREA 

if len(st.session_state.history) == 0:
    # Show a clean chatbot intro text instead of empty box
    st.markdown("""
        <div style='
            text-align:center; 
            margin-top:120px;
            color:#9fa3a8;
            font-size:20px;
            line-height:1.6;
        '>
            👋 <b>Welcome to your AI Chatbot</b><br>
            Ask anything to get started.<br>
            This assistant can answer questions, explain concepts, help with code,<br>
            and much more — just type below and press Enter.
        </div>
    """, unsafe_allow_html=True)
else:
    # Show chat messages normally
    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

    for chat in st.session_state.history:
        st.markdown(f"<div class='user-msg'>{chat['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bot-msg'>{chat['bot']}</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)




# Input box (Enter to send)
user_input = st.chat_input("Message the bot…")

if user_input:
    bot = ask_groq(user_input, st.session_state.history)
    st.session_state.history.append({"user": user_input, "bot": bot})
