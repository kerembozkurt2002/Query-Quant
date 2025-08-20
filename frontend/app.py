import streamlit as st
import pandas as pd
import requests
import json
import os
import io
import base64

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PROMPT_ENDPOINT = "/document/v1/api/prompt"

st.set_page_config(page_title="Query-Quant", layout="centered")
st.title("Query-Quant")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm_messages" not in st.session_state:
    st.session_state.llm_messages = []
if "file" not in st.session_state:
    st.session_state.file = None
if "file_bytes" not in st.session_state:
    st.session_state.file_bytes = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "file_mime" not in st.session_state:
    st.session_state.file_mime = None
if "df_preview" not in st.session_state:
    st.session_state.df_preview = None
if "df_shape" not in st.session_state:
    st.session_state.df_shape = None

# ---------- Helpers ----------
def render_message_content(content, target=st):
    """
    Render a message that can be a string or a list of blocks into `target`,
    which must have markdown/image/dataframe/code methods like `st` or a container.
    """
    if isinstance(content, str):
        target.markdown(content, unsafe_allow_html=True)
        return

    if isinstance(content, list):
        for block in content:
            btype = block.get("t")
            val = block.get("value")
            if btype == "md":
                target.markdown(val, unsafe_allow_html=True)
            elif btype == "df":
                try:
                    df = pd.DataFrame(val)
                    target.dataframe(df, use_container_width=True)
                except Exception:
                    target.code(json.dumps(val, ensure_ascii=False, indent=2))
            elif btype == "img":
                try:
                    img_bytes = base64.b64decode(val)
                    target.image(img_bytes, use_container_width=True)
                except Exception:
                    target.markdown(f'<img src="data:image/png;base64,{val}" width="640"/>',
                                    unsafe_allow_html=True)
            else:
                target.code(json.dumps(block, ensure_ascii=False, indent=2))
    else:
        target.code(str(content))

with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload data file (first message only)",
        type=["csv", "xlsx", "xls"],
        help="Supported formats: .csv, .xlsx, .xls"
    )
    if uploaded_file:
        st.session_state.file = uploaded_file
        st.session_state.file_bytes = uploaded_file.getvalue()
        st.session_state.file_name = uploaded_file.name
        st.session_state.file_mime = uploaded_file.type or "application/octet-stream"

        try:
            if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(io.BytesIO(st.session_state.file_bytes))
            else:
                df = pd.read_csv(io.BytesIO(st.session_state.file_bytes))
            st.session_state.df_shape = df.shape
            st.session_state.df_preview = df.head(500)
            rows, cols = st.session_state.df_shape
            st.success(f"File **{uploaded_file.name}** stored. Detected shape: {rows} rows × {cols} columns.")
        except Exception as e:
            st.session_state.df_shape = None
            st.session_state.df_preview = None
            st.error(f"Couldn't preview the file: {e}")

    if st.button("🔄 Clear chat"):
        st.session_state.messages.clear()
        st.session_state.llm_messages.clear()
        st.session_state.file = None
        st.session_state.file_bytes = None
        st.session_state.file_name = None
        st.session_state.file_mime = None
        st.session_state.df_preview = None
        st.session_state.df_shape = None
        st.rerun()

if st.session_state.file:
    st.markdown("### 📄 Uploaded Data")
    if st.session_state.df_shape:
        r, c = st.session_state.df_shape
        st.caption(f"**{st.session_state.file_name}** — {r} rows × {c} columns")
    else:
        st.caption(f"**{st.session_state.file_name}**")

    with st.expander("📊 Click to preview uploaded data", expanded=False):
        if st.session_state.df_preview is not None:
            st.dataframe(st.session_state.df_preview, use_container_width=True)
            st.download_button(
                "⬇️ Download original file",
                data=st.session_state.file_bytes,
                file_name=st.session_state.file_name,
                mime=st.session_state.file_mime,
            )
        else:
            st.info("No preview available.")

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 **Welcome to Query-Quant!**\n\n"
            "Upload a CSV/XLSX/XLS from the sidebar to get started.\n"
            "Once your data is loaded, ask what you want to explore. "
            "I’ll analyze, summarize, and visualize based on the columns I detect."
        )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_message_content(msg["content"])

prompt = st.chat_input("Write a prompt…")
execution_result = None

if prompt:
    if not st.session_state.file:
        st.error("Please upload a file first (see sidebar).")
        st.stop()

    user_blocks = [{"t": "md", "value": prompt}]
    st.session_state.messages.append({"role": "user", "content": user_blocks})
    with st.chat_message("user"):
        render_message_content(user_blocks)

    assistant_ph = st.chat_message("assistant").container()
    thinking_slot = assistant_ph.empty()
    thinking_slot.markdown("⏳ *Thinking…*")

    history_for_llm = []
    for m in st.session_state.llm_messages:
        history_for_llm.append({
            "type": "human" if m["role"] == "user" else "ai",
            "content": m["content"]
        })

    try:
        files = {
            "file": (
                st.session_state.file_name,
                io.BytesIO(st.session_state.file_bytes),
                st.session_state.file_mime
            )
        }
        payload = {"prompt": prompt, "history": json.dumps(history_for_llm)}
        r = requests.post(
            f"{BASE_URL}{PROMPT_ENDPOINT}",
            params=payload,
            files=files,
            timeout=120
        )
        r.raise_for_status()
        result = r.json()
    except Exception as e:
        assistant_blocks = [{"t": "md", "value": f"❌ Error: {e}"}]
        execution_result = None
    else:
        status   = result.get("status", "error")
        message  = result.get("message", "")
        resp_txt = result.get("response_text", "")
        execution_result = result.get("execution_result", "")

        header_text = f"**{message or status.capitalize()}**\n\n{resp_txt}".strip()
        assistant_blocks = [{"t": "md", "value": header_text}]

        chart_img = result.get("chart_image")
        if chart_img:
            assistant_blocks.append({"t": "img", "value": chart_img})

        df_data = result.get("data")
        if df_data:
            assistant_blocks.append({"t": "md", "value": "**Result Table**"})
            assistant_blocks.append({"t": "df", "value": df_data})

    thinking_slot.empty()
    render_message_content(assistant_blocks, target=assistant_ph)

    st.session_state.messages.append({"role": "assistant", "content": assistant_blocks})

    if execution_result is not None:
        st.session_state.llm_messages.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": execution_result}
        ])
