import os
from typing import Any

import httpx
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def api_get(path: str) -> Any:
    response = httpx.get(f"{API_BASE_URL}{path}", timeout=60)
    response.raise_for_status()
    return response.json()


def api_post(path: str, json: dict | None = None, files: dict | None = None) -> Any:
    response = httpx.post(f"{API_BASE_URL}{path}", json=json, files=files, timeout=180)
    response.raise_for_status()
    return response.json()


def api_delete(path: str) -> int:
    response = httpx.delete(f"{API_BASE_URL}{path}", timeout=60)
    response.raise_for_status()
    return response.status_code


st.set_page_config(
    page_title="RAG Support Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("📚 RAG Support Assistant")
st.caption("Upload support documents, ask questions, and get grounded answers with sources.")

with st.sidebar:
    st.header("Backend")

    health_clicked = st.button("Check API Health")
    if health_clicked:
        try:
            health = api_get("/health")
            st.success(f"API is running: {health}")
        except Exception as exc:
            st.error(f"API health check failed: {exc}")

    st.divider()

    st.header("Documents")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["txt", "pdf"],
    )

    if uploaded_file is not None:
        if st.button("Upload Document"):
            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                }
                result = api_post("/documents", files=files)
                st.success(
                    f"Uploaded/indexed: {result['filename']} "
                    f"({result['chunk_count']} chunks)"
                )
            except Exception as exc:
                st.error(f"Upload failed: {exc}")

    try:
        documents = api_get("/documents")
    except Exception:
        documents = []

    if documents:
        st.subheader("Indexed Documents")

        for doc in documents:
            col_doc, col_delete = st.columns([3, 1])

            with col_doc:
                st.write(
                    f"**{doc['filename']}**  \n"
                    f"ID: `{doc['id']}` · Chunks: `{doc['chunk_count']}`"
                )

            with col_delete:
                if st.button("Delete", key=f"delete-doc-{doc['id']}"):
                    try:
                        api_delete(f"/documents/{doc['id']}")
                        st.success("Deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Delete failed: {exc}")
    else:
        st.info("No documents indexed yet.")


left_col, right_col = st.columns([1, 2])

with left_col:
    st.header("Conversation")

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    conversation_title = st.text_input(
        "New conversation title",
        value="Support policy test",
    )

    if st.button("Create Conversation"):
        try:
            conversation = api_post(
                "/conversations",
                json={"title": conversation_title},
            )
            st.session_state.conversation_id = conversation["id"]
            st.success(f"Created conversation ID: {conversation['id']}")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to create conversation: {exc}")

    try:
        conversations = api_get("/conversations")
    except Exception:
        conversations = []

    if conversations:
        conversation_options = {
            f"{conversation['id']} - {conversation['title']}": conversation["id"]
            for conversation in conversations
        }

        selected_label = st.selectbox(
            "Select conversation",
            options=list(conversation_options.keys()),
        )

        if st.button("Use Selected Conversation"):
            st.session_state.conversation_id = conversation_options[selected_label]
            st.rerun()

    st.write("Current conversation ID:")
    st.code(st.session_state.conversation_id)


with right_col:
    st.header("Ask Question")

    question = st.text_area(
        "Question",
        value="When should support escalate a ticket to engineering?",
        height=100,
    )

    top_k = st.slider("Number of retrieved chunks", min_value=1, max_value=10, value=3)

    if st.button("Ask"):
        try:
            if st.session_state.conversation_id is None:
                conversation = api_post(
                    "/conversations",
                    json={"title": question[:80]},
                )
                st.session_state.conversation_id = conversation["id"]

            result = api_post(
                f"/conversations/{st.session_state.conversation_id}/ask",
                json={
                    "question": question,
                    "top_k": top_k,
                },
            )

            st.subheader("Answer")
            st.write(result["answer"])

            st.subheader("Sources")
            for index, source in enumerate(result["sources"], start=1):
                with st.expander(
                    f"Source {index}: {source['filename']} "
                    f"(chunk {source['chunk_index']}, similarity {source['similarity']:.4f})"
                ):
                    st.write(source["content_preview"])

        except Exception as exc:
            st.error(f"Ask failed: {exc}")

    st.divider()

    st.header("Conversation History")

    if st.session_state.conversation_id is not None:
        try:
            messages = api_get(
                f"/conversations/{st.session_state.conversation_id}/messages"
            )

            if messages:
                for message in messages:
                    if message["role"] == "user":
                        with st.chat_message("user"):
                            st.write(message["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(message["content"])
            else:
                st.info("No messages yet.")
        except Exception as exc:
            st.error(f"Failed to load messages: {exc}")
    else:
        st.info("Create or select a conversation first.")