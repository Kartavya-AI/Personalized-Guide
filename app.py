import streamlit as st
import re
from tool import get_guide_response, get_chat_response
from db import init_db, add_favorite, get_favorites, clear_favorites

st.set_page_config(page_title="Personalized AI Guide", page_icon="🤖", layout="centered")
init_db()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "city_context" not in st.session_state:
    st.session_state.city_context = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# --- Sidebar UI ---
with st.sidebar:
    st.header("🔑 Configuration")
    st.session_state.api_key = st.text_input("Enter your Google Gemini API Key:", type="password", value=st.session_state.api_key)
    st.caption("Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey).")
    st.markdown("---")
    st.header("❤️ My Saved Places")
    if st.button("Show My List"):
        favorites_df = get_favorites()
        if favorites_df.empty:
            st.info("Your list is empty. Ask the guide to save a place!")
        else:
            st.dataframe(favorites_df, use_container_width=True, hide_index=True)
            
    if st.button("Clear My List"):
        clear_favorites()
        st.success("Your favorites list has been cleared!")

# --- Main Chat Interface ---
st.title("🤖 AI Personal Guide")
st.subheader("Your interactive travel companion")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.messages:
    city = st.text_input("📍 Which city are you travelling to?", key="city_input")
    if st.button("Generate Guide", type="primary"):
        if not st.session_state.api_key:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
        elif not city:
            st.warning("Please enter a city name.")
        else:
            st.session_state.city_context = city
            with st.chat_message("assistant"):
                with st.spinner("Crafting your personal guide..."):
                    initial_guide = get_guide_response(st.session_state.api_key, city)
                    st.markdown(initial_guide)
                    st.session_state.messages.append({"role": "assistant", "content": initial_guide})
            st.rerun()

if prompt := st.chat_input("Ask me for details or to save a place..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            save_match = re.search(r"save\s+(.+)", prompt, re.IGNORECASE)
            
            if save_match:
                place_to_save = save_match.group(1).strip()
                response = add_favorite(st.session_state.city_context, place_to_save)
            else:
                response = get_chat_response(st.session_state.api_key, st.session_state.messages)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})