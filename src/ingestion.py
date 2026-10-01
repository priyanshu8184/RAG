import json
import re
import urllib.parse
import urllib.request
from typing import Callable, List, Optional, Tuple
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import DEFAULT_SPORTS_URLS
from src.vectorstore import get_astra_vector_store, get_local_vector_store

SPORTS_DOMAINS = {
    "espn.com", "espncricinfo.com", "cricbuzz.com", "fifa.com", "uefa.com",
    "nba.com", "nfl.com", "formula1.com", "f1.com", "skysports.com",
    "olympics.com", "atptour.com", "wtatennis.com", "pgatour.com",
    "mlb.com", "nhl.com", "icc-cricket.com", "premierleague.com",
    "bundesliga.com", "laliga.com", "motorsport.com", "bcci.tv",
    "eurosport.com", "cbssports.com", "si.com", "theathletic.com",
}

SPORTS_KEYWORDS = {
    "sport", "sports", "cricket", "cricketer", "football", "footballer", "soccer",
    "basketball", "tennis", "formula", "f1", "grand_prix", "racing", "motorsport",
    "baseball", "hockey", "rugby", "golf", "golfer", "volleyball", "badminton",
    "athletics", "athlete", "sportsperson", "olympic", "olympics", "paralympic", "swimming", "swimmer",
    "boxing", "boxer", "wrestling", "wrestler", "nba", "nfl", "fifa", "uefa", "icc",
    "ipl", "atp", "wta", "pga", "mlb", "nhl", "kohli", "messi", "ronaldo", "dhoni",
    "sachin", "tendulkar", "hamilton", "verstappen", "lebron", "jordan", "federer",
    "nadal", "djokovic", "rohit", "rohit_sharma", "maradona", "pele", "bolt", "phelps",
    "world_cup", "champions_league", "super_bowl", "wimbledon", "tournament",
    "championship", "stadium", "striker", "batsman", "bowler", "wicket", "touchdown",
    "quarterback", "grand_slam", "ballon_d_or", "driver", "pitcher", "goalkeeper",
    "bumrah", "hardik", "jadeja", "sehwag", "ganguly", "dravid", "alcaraz", "sinner",
    "serena", "curry", "kobe", "shaq", "sindhu", "neeraj", "chopra"
}

SPORTS_CONTENT_ANCHORS = {
    "sport", "sports", "athlete", "athletic", "sportsperson", "tournament", "championship",
    "league", "match", "game", "player", "coach", "manager", "stadium",
    "arena", "referee", "umpire", "score", "goal", "wicket", "touchdown",
    "basket", "trophy", "medal", "olympic", "fifa", "uefa", "nba", "nfl",
    "ipl", "icc", "cricket", "football", "soccer", "basketball", "tennis",
    "golf", "baseball", "hockey", "f1", "racing", "grand slam", "world cup",
    "batsman", "bowler", "innings", "century", "striker", "midfielder", "racer"
}


def is_sports_url(url: str) -> Tuple[bool, str]:
    """Validate whether a URL belongs to a sports domain, entity, or topic.

    Returns:
        (is_sports, explanation)
    """
    if not url or not url.strip():
        return False, "Empty or invalid URL"

    clean_url = url.strip()

    # Pre-approved default sports URLs
    if clean_url in DEFAULT_SPORTS_URLS:
        return True, "Pre-approved official sports archive"

    parsed = urllib.parse.urlparse(clean_url)
    domain = parsed.netloc.lower()

    # 1. Check known sports domains
    if any(sd in domain for sd in SPORTS_DOMAINS):
        return True, "Verified sports platform/domain"

    # 2. Check tokens in URL path/slug
    unquoted = urllib.parse.unquote(clean_url).lower()
    tokens = set(re.findall(r"[a-z0-9_]+", unquoted))
    matched_slug = tokens.intersection(SPORTS_KEYWORDS)
    if matched_slug:
        return True, f"Sports terminology identified in URL ({', '.join(list(matched_slug)[:3])})"

    # 3. For Wikipedia URLs, inspect entry metadata/summary for sports classification
    if "wikipedia.org/wiki/" in clean_url:
        slug = clean_url.split("/wiki/")[-1].split("#")[0].split("?")[0]
        try:
            req_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
            req = urllib.request.Request(req_url, headers={"User-Agent": "SportPulseAI/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                desc = (data.get("description") or "").lower()
                extract = (data.get("extract") or "").lower()
                combined = f"{desc} {extract}"
                combined_tokens = set(re.findall(r"[a-z0-9_]+", combined))
                matched_wiki = combined_tokens.intersection(SPORTS_KEYWORDS)
                if matched_wiki:
                    return True, f"Wikipedia sports entity verified ({', '.join(list(matched_wiki)[:3])})"
                else:
                    entry_title = data.get("title", slug)
                    return False, f"Wikipedia article '{entry_title}' is not sports-related"
        except Exception:
            pass

    return False, "Not recognized as a sports resource"


def is_sports_content(text: str, title: str = "") -> Tuple[bool, str]:
    """Verify that loaded page content is genuinely related to sports."""
    if not text:
        return False, "Page has no readable text"

    sample = text[:15000].lower()
    hits = 0
    for kw in SPORTS_CONTENT_ANCHORS:
        hits += sample.count(kw)

    # Core check: sports articles have abundant occurrences of sports anchors
    if hits >= 4 or any(sk in title.lower() for sk in ["sport", "cricket", "football", "soccer", "tennis", "f1", "olympic"]):
        return True, f"Sports content confirmed ({hits} sports anchor mentions)"
    return False, f"Document content does not match sports criteria (only {hits} sports markers found)"


def load_documents_from_urls(
    urls: List[str],
    log_fn: Optional[Callable[[str], None]] = None,
) -> List[Document]:
    """Fetch documents from a list of web URLs with strict sports verification.

    Args:
        urls: List of URLs to load.
        log_fn: Optional logger function (e.g. st.write).

    Returns:
        List of loaded LangChain documents.
    """
    docs: List[Document] = []
    for url in urls:
        clean_url = url.strip()
        if not clean_url:
            continue

        # Validate URL level
        is_sport, reason = is_sports_url(clean_url)
        if not is_sport:
            msg = f"⚠️ Please enter URLs related to sports only! Rejected: '{clean_url}' ({reason})"
            if log_fn:
                log_fn(msg)
            continue

        try:
            loader = WebBaseLoader(clean_url)
            loaded = loader.load()
            if not loaded:
                if log_fn:
                    log_fn(f"⚠️ Empty page loaded from: {clean_url}")
                continue

            # Verify content level
            content_ok, content_reason = is_sports_content(
                loaded[0].page_content,
                loaded[0].metadata.get("title", "")
            )
            if not content_ok:
                msg = f"⚠️ Please enter URLs related to sports only! Content from '{clean_url}' failed sports criteria ({content_reason})"
                if log_fn:
                    log_fn(msg)
                continue

            docs.extend(loaded)
            if log_fn:
                log_fn(f"✓ Verified Sports Resource: {clean_url}")
        except Exception as err:
            if log_fn:
                log_fn(f"⚠️ Failed loading {clean_url}: {err}")
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
    """Run full ingestion pipeline: validate sports URLs, load, chunk, and index.

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

    # Strict Criteria Validation: Pre-check all URLs for non-sports links
    non_sports_urls = []
    for u in clean_urls:
        ok, reason = is_sports_url(u)
        if not ok:
            non_sports_urls.append((u, reason))

    if non_sports_urls:
        rejected_list = "\n".join([f"- {url} ({reason})" for url, reason in non_sports_urls])
        raise ValueError(
            f"Please enter URLs related to sports only!\n\nThe following URL(s) do not match sports criteria:\n{rejected_list}"
        )

    if log_fn:
        log_fn(f"📥 Verified {len(clean_urls)} sports encyclopedias. Loading data...")

    docs = load_documents_from_urls(clean_urls, log_fn=log_fn)
    if not docs:
        raise ValueError(
            "Please enter URLs related to sports only! None of the provided URLs yielded valid sports content."
        )

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
