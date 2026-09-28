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
        if "401" in error_msg or "Unauthorized" in error_msg:
            return None, (
                "HTTP 401 Unauthorized: Your Astra DB Application Token is invalid or expired. "
                "Please generate a fresh token at https://astra.datastax.com (Role: Database Administrator)."
            )
        elif "Unable to connect" in error_msg or "metadata service" in error_msg:
            return None, (
                f"Connection Failed: Unable to connect to Astra DB ({db_id}). "
                "Check if your database status is 'ACTIVE' in DataStax Astra Console."
            )
        return None, f"Astra DB Error: {error_msg}"
