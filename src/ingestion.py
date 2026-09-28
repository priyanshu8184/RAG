from typing import Callable, List, Optional
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.vectorstore import get_astra_vector_store, get_local_vector_store


def load_documents_from_urls(
    urls: List[str],
    log_fn: Optional[Callable[[str], None]] = None,
) -> List[Document]:
    """Fetch documents from a list of web URLs.

    Args:
        urls: List of URLs to load.
        log_fn: Optional logger function (e.g. st.write).

    Returns:
        List of loaded LangChain documents.
    """
    docs: List[Document] = []
    for url in urls:
        try:
            loader = WebBaseLoader(url)
            loaded = loader.load()
            docs.extend(loaded)
            if log_fn:
                log_fn(f"✓ Loaded: {url}")
        except Exception as err:
            if log_fn:
                log_fn(f"⚠️ Failed loading {url}: {err}")
    return docs


def chunk_documents(
    docs: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """Split documents into tactical chunks using tiktoken encoder."""
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return text_splitter.split_documents(docs)


def ingest_sports_vault(
    urls: List[str],
    use_astra: bool = False,
    astra_token: str = "",
    astra_db_id: str = "",
    table_name: str = "sports_intelligence_vault",
    keyspace_name: str = "default_keyspace",
    log_fn: Optional[Callable[[str], None]] = None,
) -> int:
    """Run full ingestion pipeline: load, chunk, and index into vector store.

    Args:
        urls: List of URLs to index.
        use_astra: If True, indexes into Astra DB; otherwise into local in-memory store.
        astra_token: Astra DB application token.
        astra_db_id: Astra DB database UUID.
        table_name: Vector table name.
        keyspace_name: Keyspace name.
        log_fn: Optional logging function to display progress messages.

    Returns:
        Total number of chunks indexed.
    """
    clean_urls = [u.strip() for u in urls if u.strip()]
    if not clean_urls:
        raise ValueError("No valid URLs provided for ingestion.")

    if log_fn:
        log_fn(f"📥 Fetching data from {len(clean_urls)} sports encyclopedias & records...")

    docs = load_documents_from_urls(clean_urls, log_fn=log_fn)
    if not docs:
        raise ValueError("No documents could be loaded from the provided URLs.")

    if log_fn:
        log_fn(f"✂️ Chunking {len(docs)} sports documents into high-resolution segments...")

    doc_splits = chunk_documents(docs)

    if log_fn:
        log_fn(f"Generated {len(doc_splits)} tactical data chunks.")

    if use_astra:
        if log_fn:
            log_fn(f"💾 Connecting to Astra DB table `{table_name}`...")
        vector_store, conn_err = get_astra_vector_store(
            token=astra_token,
            db_id=astra_db_id,
            table=table_name,
            keyspace=keyspace_name,
        )
        if vector_store is None:
            raise ValueError(conn_err or "Failed to connect to Astra DB.")

        batch_size = 100
        total_batches = (len(doc_splits) + batch_size - 1) // batch_size
        for i in range(0, len(doc_splits), batch_size):
            batch = doc_splits[i : i + batch_size]
            vector_store.add_documents(batch)
            if log_fn:
                batch_num = (i // batch_size) + 1
                log_fn(f"Embedded batch {batch_num}/{total_batches} ({len(batch)} chunks)")
    else:
        if log_fn:
            log_fn("💾 Embedding chunks into Local In-Memory Vector Store...")
        local_store = get_local_vector_store()
        if local_store is None:
            raise ValueError("Failed to initialize local vector store.")

        batch_size = 200
        for i in range(0, len(doc_splits), batch_size):
            batch = doc_splits[i : i + batch_size]
            local_store.add_documents(batch)

        if "indexed_chunk_count" in st.session_state:
            st.session_state.indexed_chunk_count += len(doc_splits)

    return len(doc_splits)
