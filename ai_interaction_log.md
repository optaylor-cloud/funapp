# AI Interaction Log

## 2026-03-18
**User asked:** Create the Week 10 project structure under week_10_assignment.
**Assistant did:** Created app.py, requirements.txt, memory.json, ai_interaction_log.md, chats/, and .streamlit/ with config.toml and secrets.toml.

**User asked:** Set up .venv, install streamlit/requests, run Streamlit, add HF token in secrets.toml, create config.toml, and keep the app running; also ensure Codex interactions are appended to the log.
**Assistant did:** Created .venv, installed dependencies, verified requirements.txt, ran Streamlit, created .streamlit/secrets.toml and .streamlit/config.toml with provided values, restarted Streamlit to apply the theme, and confirmed logging will be appended.

**User asked:** Initialize git, ignore secrets, amend commit, connect GitHub repo, and deploy to Streamlit Cloud; then troubleshoot missing files and push/auth issues.
**Assistant did:** Initialized git, committed, added .gitignore for .streamlit/secrets.toml and amended commit, attempted to set remote and push, noted GitHub auth requirements and missing gh/brew, updated remote URL to funapp, and advised running push from the repo directory.

### Task: Week 10 Setup, Git, and Deployment Prep
**Prompt:** "Set up .venv, install Streamlit/requests, create Streamlit config and secrets, initialize git, ignore secrets, connect GitHub, and deploy to Streamlit Cloud; troubleshoot auth and push issues."
**AI Suggestion:** Created venv, installed deps, added Streamlit config/secrets, updated .gitignore and amended commit to remove secrets, initialized git and remote, guided GitHub auth troubleshooting, switched to SSH and pushed, and provided Streamlit Cloud deployment entries.
**My Modifications & Reflections:** Used SSH auth after token issues; push succeeded. Secrets are ignored in git and will be added in Streamlit Cloud advanced settings.

### Task: Hugging Face Inference Router Integration
**Prompt:** "App must use Hugging Face Inference Router endpoint with OpenAI chat completions format. Use model meta-llama/Llama-3.2-1B-Instruct. Token stored in Streamlit secrets; app must not crash if missing."
**AI Suggestion:** Implemented a Streamlit chat UI that calls the Hugging Face router endpoint with the specified model, reads `HF_TOKEN` from secrets, shows a clear error if missing, and handles request/response errors safely.
**My Modifications & Reflections:** Updated `app.py` with the router call and token handling; ensured secrets are not hardcoded and errors are user-friendly.

### Task: Confirm Secrets Handling and Request Structure
**Prompt:** "Keep secrets out of git; use HF Router request structure with Authorization header and payload including model, messages, and max_tokens."
**AI Suggestion:** Confirmed `.streamlit/secrets.toml` remains ignored and aligned the API request payload with `max_tokens` and Authorization header format.
**My Modifications & Reflections:** Added `max_tokens` to the request payload; secrets file remains untracked and will be supplied in deployment settings.

### Task: Four-Stage Foundational Chat App
**Prompt:** "Build foundational ChatGPT-style app in four stages with st.set_page_config(page_title=\"My AI Chat\", layout=\"wide\"); load HF token from st.secrets[\"HF_TOKEN\"]; show error if missing; send hardcoded test message to Hugging Face router and display response; handle API errors; use similar layout to provided image."
**AI Suggestion:** Implemented a wide-layout Streamlit app with sidebar and main chat area, safely loaded HF token from secrets, sent a hardcoded "Hello!" test message to the Hugging Face router, displayed the response, and handled missing token/API errors without crashing.
**My Modifications & Reflections:** Added stage comments and a test-send button; layout is similar to the reference without copying exactly.

### Task: Handle Missing Secrets Without Crash
**Prompt:** "Success criteria: app must show an error (not crash) when secrets file is missing."
**AI Suggestion:** Catch StreamlitSecretNotFoundError when accessing `st.secrets` and fall back to an empty token so the app can display a friendly error.
**My Modifications & Reflections:** Updated `app.py` to catch the missing-secrets exception; the app should now show the in-app error instead of crashing.

### Task: Part B Chat UI and History
**Prompt:** "Extend Part A with Streamlit chat UI, use st.chat_message and st.chat_input, keep input fixed, store full history in session state, send history to API, and render scrolling chat above input."
**AI Suggestion:** Replaced the hardcoded test message with `st.chat_input`, rendered messages via `st.chat_message` in a fixed-height container, stored full history in `st.session_state.messages`, and sent the entire history with each request for context.
**My Modifications & Reflections:** Updated `app.py` to the native chat UI and ensured the input bar stays visible while the message history scrolls.

### Task: Dark Green Theme Styling
**Prompt:** "Make the background dark green and use light colors for text (light blue, light green)."
**AI Suggestion:** Added lightweight CSS to set a dark green app background, light blue text, and light green inputs while keeping native Streamlit chat UI.
**My Modifications & Reflections:** Updated `app.py` with theme CSS; no changes to chat logic.

### Task: Part C Multi-Chat Sidebar
**Prompt:** "Add New Chat button; sidebar list of chats with title + timestamp; highlight active chat; switch without overwriting; delete with ✕; handle active deletion and empty state."
**AI Suggestion:** Implemented multi-chat state with per-chat message history, a scrollable sidebar list with select and delete controls, active chat highlighting via button style, and safe fallback when deleting the active chat.
**My Modifications & Reflections:** Updated `app.py` to manage multiple chats independently; active chat stays distinct and the input still posts to the selected chat.

### Task: Custom Chat Avatars
**Prompt:** "Use the first image as the user icon and the second image as the AI icon."
**AI Suggestion:** Copied `user.png` and `assistant.png` from Downloads into `assets/` and set them as avatars in `st.chat_message`.
**My Modifications & Reflections:** Updated `app.py` to use `assets/user.png` and `assets/ai.png` for chat avatars.

### Task: Part D Chat Persistence
**Prompt:** "Persist each chat as a JSON file in chats/, load on startup, allow delete to remove file, and continue chats across restarts."
**AI Suggestion:** Added JSON save/load helpers, load existing chats on startup, save on new chat and each message, and delete the corresponding file when a chat is removed.
**My Modifications & Reflections:** Updated `app.py` to read/write per-chat JSON files in `chats/`; active chat selection survives restarts.

### Task: Streaming Responses
**Prompt:** "Stream model replies token-by-token using SSE and stream=True, render incrementally, and save full response to history."
**AI Suggestion:** Added streaming request handling with SSE parsing, incremental UI updates via a placeholder, a short delay to show streaming, and final persistence of the full response.
**My Modifications & Reflections:** Implemented streaming in `app.py` with `stream=True` and a tiny delay; responses are now displayed incrementally and saved.

### Task: Persistent User Memory
**Prompt:** "Extract user traits after each assistant response, store in memory.json, display in sidebar, allow reset, and inject memory into system prompt for personalization."
**AI Suggestion:** Added memory load/save/merge helpers, sidebar display with clear control, a second API call to extract traits from the latest user message, and injected JSON memory into the system prompt for future requests.
**My Modifications & Reflections:** Implemented persistent memory in `memory.json`; chat now personalizes responses using stored traits and shows them in the sidebar.

### Task: Requirements Audit and Part A Test Message
**Prompt:** "Ensure st.secrets[\"HF_TOKEN\"] usage, keep Part A test message support, and confirm all rubric requirements."
**AI Suggestion:** Adjusted token loading to use st.secrets["HF_TOKEN"] with safe exception handling and added a Send Test Message button that sends "Hello!" while keeping the chat UI.
**My Modifications & Reflections:** Updated `app.py` to satisfy the explicit Part A requirement while preserving multi-turn chat behavior.

