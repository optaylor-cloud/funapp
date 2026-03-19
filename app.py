import json
import os
import time
from datetime import datetime

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

ENDPOINT = "https://router.huggingface.co/v1/chat/completions"
MODEL = "meta-llama/Llama-3.2-1B-Instruct"

st.set_page_config(page_title="My AI Chat", layout="wide")

st.markdown(
    """
<style>
    .stApp {
        background-color: #0b2416;
        color: #cfe9ff;
    }
    .stMarkdown, .stText, .stCaption, .stChatMessage, .stChatMessage p {
        color: #cfe9ff;
    }
    .stChatMessage.user, .stChatMessage.assistant {
        background: transparent;
    }
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stChatInput input {
        color: #d6f7d0;
        background-color: #0f2e1b;
        border: 1px solid #1b5d3a;
    }
    .stSidebar {
        background-color: #0a1b12;
    }
    .stSidebar .stMarkdown, .stSidebar .stText {
        color: #bfe7ff;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("My AI Chat")
st.caption("Foundational chat app using Hugging Face Inference Router")

# ---- Persistence helpers ----
CHATS_DIR = "chats"
os.makedirs(CHATS_DIR, exist_ok=True)
MEMORY_PATH = "memory.json"


def _chat_path(chat_id: str) -> str:
    return os.path.join(CHATS_DIR, f"{chat_id}.json")


def _save_chat(chat: dict) -> None:
    data = {
        "id": chat["id"],
        "title": chat["title"],
        "created_at": chat["created_at"],
        "messages": chat["messages"],
    }
    with open(_chat_path(chat["id"]), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_chats() -> list[dict]:
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(CHATS_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if {"id", "title", "created_at", "messages"} <= data.keys():
                chats.append(data)
        except (OSError, json.JSONDecodeError, KeyError):
            continue
    chats.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    return chats


def _delete_chat_file(chat_id: str) -> None:
    try:
        os.remove(_chat_path(chat_id))
    except FileNotFoundError:
        pass


def _load_memory() -> dict:
    if not os.path.exists(MEMORY_PATH):
        return {}
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def _save_memory(memory: dict) -> None:
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def _merge_memory(existing: dict, new_data: dict) -> dict:
    for key, value in new_data.items():
        if key not in existing:
            existing[key] = value
            continue
        if isinstance(existing[key], list) and isinstance(value, list):
            existing[key] = list(dict.fromkeys(existing[key] + value))
        elif isinstance(existing[key], dict) and isinstance(value, dict):
            existing[key].update(value)
        else:
            existing[key] = value
    return existing

# ---- Stage 1: Load token safely ----
try:
    hf_token = st.secrets["HF_TOKEN"]
except (StreamlitSecretNotFoundError, KeyError):
    hf_token = ""

if not hf_token:
    st.error(
        "Missing Hugging Face token. Please add `HF_TOKEN` to Streamlit secrets "
        "(.streamlit/secrets.toml or Streamlit Cloud Secrets)."
    )
    st.stop()

# ---- Sidebar (layout similar to reference) ----
st.sidebar.title("Chats")

def _new_chat():
    chat_id = f"chat_{datetime.utcnow().timestamp()}"
    chat = {
        "id": chat_id,
        "title": "New Chat",
        "created_at": datetime.now().strftime("%b %d, %I:%M %p"),
        "messages": [],
    }
    st.session_state.chats.append(chat)
    _save_chat(chat)
    st.session_state.active_chat_id = chat_id

if "chats" not in st.session_state:
    st.session_state.chats = _load_chats()
if "active_chat_id" not in st.session_state:
    if st.session_state.chats:
        st.session_state.active_chat_id = st.session_state.chats[0]["id"]
    else:
        _new_chat()

if st.sidebar.button("New Chat", use_container_width=True):
    _new_chat()

with st.sidebar.expander("User Memory", expanded=True):
    if "memory" not in st.session_state:
        st.session_state.memory = _load_memory()
    if st.sidebar.button("Clear Memory", use_container_width=True):
        st.session_state.memory = {}
        _save_memory(st.session_state.memory)
        st.rerun()
    if st.session_state.memory:
        st.sidebar.json(st.session_state.memory)
    else:
        st.sidebar.caption("No saved traits yet.")

st.sidebar.markdown("---")
st.sidebar.subheader("Recent Chats")

chat_list = st.sidebar.container(height=360)
with chat_list:
    if not st.session_state.chats:
        st.info("No chats yet. Click New Chat to start.")
    for chat in list(st.session_state.chats):
        cols = st.columns([0.82, 0.18])
        is_active = chat["id"] == st.session_state.active_chat_id
        label = f"{chat['title']}  ·  {chat['created_at']}"
        if cols[0].button(
            label,
            key=f"select_{chat['id']}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_chat_id = chat["id"]
        if cols[1].button("✕", key=f"delete_{chat['id']}"):
            st.session_state.chats = [
                c for c in st.session_state.chats if c["id"] != chat["id"]
            ]
            _delete_chat_file(chat["id"])
            if st.session_state.active_chat_id == chat["id"]:
                if st.session_state.chats:
                    st.session_state.active_chat_id = st.session_state.chats[0]["id"]
                else:
                    _new_chat()
            st.rerun()

# ---- Main area ----
col_left, col_right = st.columns([0.08, 0.92])
with col_left:
    st.write(" ")
with col_right:
    st.markdown("### Conversation")

active_chat = next(
    (c for c in st.session_state.chats if c["id"] == st.session_state.active_chat_id),
    None,
)
if active_chat is None:
    _new_chat()
    active_chat = st.session_state.chats[-1]

chat_container = st.container(height=520)
with chat_container:
    for msg in active_chat["messages"]:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

test_clicked = st.button("Send Test Message", use_container_width=True)
user_input = st.chat_input("Type a message and press Enter")
if test_clicked and not user_input:
    user_input = "Hello!"

if user_input:
    active_chat["messages"].append({"role": "user", "content": user_input})
    if active_chat["title"] == "New Chat":
        active_chat["title"] = user_input[:28] + ("..." if len(user_input) > 28 else "")
    _save_chat(active_chat)

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Personalization memory (JSON): "
                    f"{json.dumps(st.session_state.memory, ensure_ascii=False)}"
                ),
            }
        ]
        + active_chat["messages"],
        "max_tokens": 512,
        "stream": True,
    }
    headers = {"Authorization": f"Bearer {hf_token}"}

    try:
        response = requests.post(
            ENDPOINT, headers=headers, json=payload, timeout=30, stream=True
        )
        if response.status_code == 401:
            st.error("Authentication failed. Check your Hugging Face token.")
        elif response.status_code == 429:
            st.error("Rate limit reached. Please wait and try again.")
        else:
            response.raise_for_status()
            full_text = ""
            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()
                for raw_line in response.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    if not raw_line.startswith("data:"):
                        continue
                    data_str = raw_line.replace("data:", "", 1).strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
                        delta = ""
                    if delta:
                        full_text += delta
                        placeholder.markdown(full_text)
                        time.sleep(0.03)
            if full_text:
                active_chat["messages"].append(
                    {"role": "assistant", "content": full_text}
                )
                _save_chat(active_chat)
                # ---- Memory extraction call (lightweight) ----
                try:
                    mem_payload = {
                        "model": MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Given this user message, extract any personal facts "
                                    "or preferences as a JSON object. If none, return {}."
                                ),
                            },
                            {"role": "user", "content": user_input},
                        ],
                        "max_tokens": 128,
                    }
                    mem_response = requests.post(
                        ENDPOINT, headers=headers, json=mem_payload, timeout=20
                    )
                    mem_response.raise_for_status()
                    mem_data = mem_response.json()
                    mem_text = mem_data["choices"][0]["message"]["content"].strip()
                    extracted = json.loads(mem_text) if mem_text else {}
                    if isinstance(extracted, dict) and extracted:
                        st.session_state.memory = _merge_memory(
                            st.session_state.memory, extracted
                        )
                        _save_memory(st.session_state.memory)
                except (requests.RequestException, KeyError, IndexError, TypeError, json.JSONDecodeError):
                    pass
                st.rerun()
    except requests.RequestException as exc:
        st.error(f"Network or API error: {exc}")
    except (KeyError, IndexError, TypeError):
        st.error("Unexpected response format from Hugging Face Router.")
