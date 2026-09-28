from typing import Optional, Tuple
import streamlit as st
from src.config import DEFAULT_EMBEDDING_MODEL, DEFAULT_KEYSPACE


@st.cache_resource(show_spinner="⚡ Booting Sports Embedding Engine (all-MiniLM-L6-v2)...")
def get_embeddings():
    """Initialize and cache the HuggingFace sports embedding model."""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL)
    except Exception as e:
        st.sidebar.warning(f"Embedding model warning: {e}")
        return None


def get_local_vector_store():
    """Retrieve or initialize the in-memory vector store from session state."""
    if "local_vector_store" not in st.session_state:
        st.session_state.local_vector_store = None

    if st.session_state.local_vector_store is None:
        try:
            from langchain_core.vectorstores import InMemoryVectorStore
            embeddings = get_embeddings()
            if embeddings:
                st.session_state.local_vector_store = InMemoryVectorStore(embeddings)
        except Exception as e:
            st.error(f"Local vector store initialization failed: {e}")
    return st.session_state.local_vector_store


def check_and_wake_astra_db(token: str, db_id: str) -> Optional[str]:
    """Check Astra DB status via DevOps API and trigger wake-up if hibernated."""
    try:
        import json
        import urllib.request

        url = f"https://api.astra.datastax.com/v2/databases/{db_id}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            status = data.get("status", "").upper()
            region = data.get("info", {}).get("region", "us-east-2")

        if status == "HIBERNATED":
            try:
                wake_url = f"https://{db_id}-{region}.apps.astra.datastax.com/api/json/v1"
                wake_data = json.dumps({"findCollections": {}}).encode("utf-8")
                wake_req = urllib.request.Request(
                    wake_url,
                    data=wake_data,
                    headers={"Token": token, "Content-Type": "application/json"},
                )
                urllib.request.urlopen(wake_req, timeout=5)
            except Exception:
                pass
            return (
                "Astra DB was HIBERNATED due to inactivity. We have automatically triggered the wake-up process! "
                "It takes ~1-2 minutes to become ACTIVE. Please retry in a moment, or switch to 'Local In-Memory Store' in the sidebar."
            )
        elif status == "RESUMING":
            return (
                "Astra DB is currently RESUMING from hibernation (in progress). "
                "Please wait 1-2 minutes for pods to spin up, or switch to 'Local In-Memory Store' in the sidebar."
            )
    except Exception:
        pass
    return None


def get_astra_vector_store(
    token: str,
    db_id: str,
    table: str,
    keyspace: str = DEFAULT_KEYSPACE,
) -> Tuple[Optional[object], Optional[str]]:
    """Initialize Astra DB Cassandra vector store with diagnostics.

    Returns:
        (vector_store, error_message)
    """
    if not token or not db_id:
        return None, "Token or Database ID is missing."
    try:
        import cassio
        from langchain_community.vectorstores.cassandra import Cassandra

        cassio.init(token=token, database_id=db_id, keyspace=keyspace if keyspace else None)
        embeddings = get_embeddings()
        if embeddings is None:
            return None, "Failed to load HuggingFace embedding model."

        vector_store = Cassandra(
            embedding=embeddings,
            table_name=table,
            session=None,
            keyspace=keyspace if keyspace else None,
        )
        return vector_store, None
    except Exception as e:
        error_msg = str(e)
        wake_notice = check_and_wake_astra_db(token, db_id)
        if wake_notice:
            return None, wake_notice

        if "401" in error_msg or "Unauthorized" in error_msg:
            return None, (
                "HTTP 401 Unauthorized: Your Astra DB Application Token is invalid or expired. "
                "Please generate a fresh token at https://astra.datastax.com (Role: Database Administrator)."
            )
        elif "Unable to connect" in error_msg or "metadata service" in error_msg:
            return None, (
                f"Connection Failed: Unable to connect to Astra DB ({db_id}). "
                "Check if your database status is 'ACTIVE' in DataStax Astra Console, or switch to 'Local In-Memory Store'."
            )
        return None, f"Astra DB Error: {error_msg}"

