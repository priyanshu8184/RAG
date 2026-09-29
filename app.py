import streamlit as st
from src.config import APP_PAGE_ICON, APP_PAGE_TITLE
from src.graph import build_sports_rag_graph, clean_sports_output
from src.ingestion import ingest_sports_vault, is_sports_url
from src.styles import (
    apply_custom_styles,
    render_hero_header,
    render_hud_cards,
    render_playbook_chunk,
    render_source_badge,
    render_ticker_bar,
)
from src.ui import render_preset_buttons, render_sidebar
from src.vectorstore import get_astra_vector_store, get_local_vector_store

# 1. Page Configuration
st.set_page_config(
    page_title=APP_PAGE_TITLE,
    page_icon=APP_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Custom Theme
apply_custom_styles()

# 3. Session State Initialization
if "local_vector_store" not in st.session_state:
    st.session_state.local_vector_store = None
if "indexed_chunk_count" not in st.session_state:
    st.session_state.indexed_chunk_count = 0
if "active_query" not in st.session_state:
    st.session_state.active_query = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Render Sidebar & Gather Config
cfg = render_sidebar()

# Handle Clear Session
if cfg["clear_button"]:
    st.session_state.messages = []
    st.session_state.active_query = None
    st.rerun()

# 5. Resolve Active Vector Store
active_vector_store = None
if cfg["use_astra"]:
    if cfg["astra_token"] and cfg["astra_db_id"]:
        active_vector_store, _ = get_astra_vector_store(
            token=cfg["astra_token"],
            db_id=cfg["astra_db_id"],
            table=cfg["table_name"],
            keyspace=cfg["keyspace_name"],
        )
else:
    active_vector_store = get_local_vector_store()

# 6. Handle Ingestion Trigger
if cfg["index_button"]:
    urls = [u.strip() for u in cfg["custom_urls_input"].splitlines() if u.strip()]
    invalid_urls = []
    for u in urls:
        ok, reason = is_sports_url(u)
        if not ok:
            invalid_urls.append((u, reason))

    if invalid_urls:
        bullets = "\n".join([f"- `{u}` — *{r}*" for u, r in invalid_urls])
        st.error(
            f"⚠️ **Sports Criteria Restriction**: Please enter URLs related to sports only!\n\n"
            f"The following non-sports URL(s) were rejected:\n{bullets}\n\n"
            f"Please provide only sports-related URLs (e.g. cricket, football, basketball, tennis, Formula 1, Olympic records, leagues, or athlete archives)."
        )
    elif cfg["use_astra"] and (not cfg["astra_token"] or not cfg["astra_db_id"]):
        st.error("Please provide your Astra DB Token and Database ID in the sidebar, or switch to 'Local In-Memory Store'.")
    else:
        with st.status("⚡ Indexing Sports Intelligence into Vector Vault...", expanded=True) as status:
            try:
                count = ingest_sports_vault(
                    urls=urls,
                    use_astra=cfg["use_astra"],
                    astra_token=cfg["astra_token"],
                    astra_db_id=cfg["astra_db_id"],
                    table_name=cfg["table_name"],
                    keyspace_name=cfg["keyspace_name"],
                    log_fn=st.write,
                )
                destination = f"Astra DB `{cfg['table_name']}`" if cfg["use_astra"] else "Local In-Memory Vector Store"
                status.update(
                    label=f"🏆 Successfully indexed {count} sports chunks into {destination}!",
                    state="complete",
                )
                st.success(f"Indexed {count} sports intelligence chunks into {destination}! Ready for queries.")
            except Exception as e:
                status.update(label=f"❌ Sports Ingestion failed: {str(e)}", state="error")
                st.error(f"Ingestion error: {str(e)}")

# 7. Main UI Presentation
render_hero_header()
render_ticker_bar()

render_hud_cards(
    groq_api_key=cfg["groq_api_key"],
    model_name=cfg["model_name"],
    use_astra=cfg["use_astra"],
    active_vector_store=active_vector_store,
    table_name=cfg["table_name"],
    indexed_chunk_count=st.session_state.indexed_chunk_count,
)

# 8. Sport Category Selector & Preset Quick Queries
render_preset_buttons()

# 9. Display Previous Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "👤"):
        if "datasource" in msg:
            render_source_badge(msg["datasource"])
        st.markdown(clean_sports_output(msg["content"]))
        if "documents" in msg and msg["documents"]:
            render_playbook_chunk(msg["documents"])

# 10. User Chat Input & Query Execution
user_input = st.chat_input("Ask any sports question (e.g., player stats, tactical records, World Cup milestones)...")

query_to_run = None
if user_input:
    query_to_run = user_input
elif st.session_state.active_query:
    query_to_run = st.session_state.active_query
    st.session_state.active_query = None

if query_to_run:
    if not cfg["groq_api_key"]:
        st.error("Please configure your Groq API Key in the left sidebar to analyze sports queries.")
    else:
        # Display user question
        st.session_state.messages.append({"role": "user", "content": query_to_run})
        with st.chat_message("user", avatar="👤"):
            st.markdown(query_to_run)

        # Run LangGraph pipeline
        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("⚡ Running SportPulse LangGraph Router & Analytics Engine..."):
                try:
                    graph = build_sports_rag_graph(
                        groq_key=cfg["groq_api_key"],
                        model_id=cfg["model_name"],
                        temp=cfg["temperature"],
                        vector_store=active_vector_store,
                    )

                    initial_state = {
                        "question": query_to_run,
                        "datasource": "",
                        "documents": "",
                        "generation": "",
                    }

                    result = graph.invoke(initial_state)
                    datasource = result.get("datasource", "wiki_search")
                    documents = result.get("documents", "")
                    raw_generation = result.get("generation", "No tactical breakdown generated.")
                    generation = clean_sports_output(raw_generation)

                    # Render outputs
                    render_source_badge(datasource)
                    st.markdown(generation)
                    render_playbook_chunk(documents)

                    # Save assistant turn to chat history
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": generation,
                            "datasource": datasource,
                            "documents": documents,
                        }
                    )

                except Exception as e:
                    st.error(f"Error running SportPulse pipeline: {str(e)}")
