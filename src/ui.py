import os
from typing import Any, Dict
import streamlit as st
from src.config import (
    DEFAULT_KEYSPACE,
    DEFAULT_SPORTS_URLS,
    DEFAULT_TABLE_NAME,
    SPORT_PRESETS,
    SUPPORTED_GROQ_MODELS,
    get_available_groq_models,
)
from src.vectorstore import get_astra_vector_store


def render_sidebar() -> Dict[str, Any]:
    """Render the sidebar controls and return engine configuration."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0 20px 0;">
                <div style="font-family: 'Orbitron', sans-serif; font-size: 1.5rem; font-weight: 900; background: linear-gradient(90deg, #00FF87, #60EFFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    ⚡ SPORTPULSE
                </div>
                <div style="color: #64748B; font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700;">
                    Tactical Intelligence v2.0
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### ⚙️ Engine Config")

        with st.expander("🔑 API & DB Credentials", expanded=True):
            groq_api_key = st.text_input(
                "Groq API Key",
                type="password",
                value=os.getenv("GROQ_API_KEY", ""),
                help="Required for LangGraph sports routing and response generation.",
            )

            vector_backend = st.radio(
                "Vector Store Backend",
                ["⚡ Local In-Memory Store (Instant / No DB Required)", "🏟️ DataStax Astra DB (Cloud Vector DB)"],
                index=0,
                help="Choose between instant local in-memory embeddings or cloud DataStax Astra DB.",
            )

            use_astra = "Astra DB" in vector_backend

            if use_astra:
                astra_token = st.text_input(
                    "Astra DB Token",
                    type="password",
                    value=os.getenv("ASTRA_DB_APPLICATION_TOKEN", ""),
                    help="AstraCS:... application token from DataStax Astra",
                )
                astra_db_id = st.text_input(
                    "Astra DB Database ID",
                    value=os.getenv("ASTRA_DB_ID", ""),
                    help="Astra DB database UUID",
                )
                table_name = st.text_input(
                    "Sports Vector Table",
                    value=DEFAULT_TABLE_NAME,
                    help="Cassandra vector table in Astra DB",
                )
                keyspace_name = st.text_input(
                    "Keyspace Name",
                    value=os.getenv("ASTRA_DB_KEYSPACE", DEFAULT_KEYSPACE),
                    help="Astra DB keyspace",
                )

                if st.button("🔌 Test Astra DB Connection", use_container_width=True):
                    with st.spinner("Connecting to Astra DB..."):
                        test_store, test_err = get_astra_vector_store(
                            astra_token, astra_db_id, table_name, keyspace_name
                        )
                        if test_store:
                            st.success("✅ Successfully connected to Astra DB Vector Store!")
                        else:
                            st.error(f"❌ {test_err}")
            else:
                astra_token = ""
                astra_db_id = ""
                table_name = "sports_in_memory_vault"
                keyspace_name = DEFAULT_KEYSPACE
                st.info("💡 Local In-Memory Store is active. Ingestion and similarity search run 100% locally in your session.")

        with st.expander("🤖 Sports Model Settings", expanded=False):
            available_models = get_available_groq_models(groq_api_key)
            model_name = st.selectbox(
                "Groq Model",
                available_models,
                index=0,
                help="High-throughput LLMs for low-latency sports queries",
            )
            temperature = st.slider("Tactical Creativity (Temp)", 0.0, 1.0, 0.15, 0.05)

        with st.expander("📥 Sports Knowledge Ingestion", expanded=True):
            st.markdown("**Curated Sports Ingestion Knowledge Base:**")
            custom_urls_input = st.text_area(
                "Sports URLs to index (one per line)",
                value="\n".join(DEFAULT_SPORTS_URLS),
                height=140,
            )

            index_button = st.button("⚡ Ingest Sports Vault into Vector DB", use_container_width=True)

        clear_button = st.button("🧹 Clear Match Session", use_container_width=True)

    return {
        "groq_api_key": groq_api_key,
        "vector_backend": vector_backend,
        "use_astra": use_astra,
        "astra_token": astra_token,
        "astra_db_id": astra_db_id,
        "table_name": table_name,
        "keyspace_name": keyspace_name,
        "model_name": model_name,
        "temperature": temperature,
        "custom_urls_input": custom_urls_input,
        "index_button": index_button,
        "clear_button": clear_button,
    }


def render_preset_buttons():
    """Render category tabs and quick tactical query buttons."""
    st.markdown('<div class="section-header">🏆 Select a Sport & Quick Tactical Query:</div>', unsafe_allow_html=True)
    tabs = st.tabs(list(SPORT_PRESETS.keys()))

    for tab, (category, presets) in zip(tabs, SPORT_PRESETS.items()):
        with tab:
            cols = st.columns(len(presets))
            for col, (label, query) in zip(cols, presets):
                if col.button(label, use_container_width=True):
                    st.session_state.active_query = query
                    st.rerun()
