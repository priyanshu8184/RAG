import streamlit as st

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F1F5F9;
}

::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.6);
}
::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.25);
    border-radius: 9999px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(56, 189, 248, 0.5);
}


.sports-brand-container {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(17, 24, 39, 0.98) 50%, rgba(11, 15, 25, 0.95) 100%);
    border: 1px solid rgba(56, 189, 248, 0.2);
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), 0 0 30px -8px rgba(56, 189, 248, 0.12);
    backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 28px 34px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}
.sports-brand-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2.5px;
    background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #2DD4BF 100%);
}
.sports-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(56, 189, 248, 0.08);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.28);
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(56, 189, 248, 0.1);
}
.sports-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 30%, #93C5FD 70%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 14px;
}
.sports-tagline {
    color: #94A3B8;
    font-size: 1.02rem;
    font-weight: 400;
    line-height: 1.6;
    margin: 0;
    max-width: 900px;
}


.sports-ticker-bar {
    background: rgba(17, 24, 39, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 12px;
    padding: 10px 18px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 0.88rem;
    color: #CBD5E1;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    overflow: hidden;
}
.ticker-pulse {
    width: 9px;
    height: 9px;
    background-color: #38BDF8;
    border-radius: 50%;
    box-shadow: 0 0 12px #38BDF8, 0 0 4px #818CF8;
    animation: coolPulse 2s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes coolPulse {
    0% { opacity: 1; transform: scale(1); box-shadow: 0 0 6px #38BDF8; }
    50% { opacity: 0.45; transform: scale(1.3); box-shadow: 0 0 16px #38BDF8; }
    100% { opacity: 1; transform: scale(1); box-shadow: 0 0 6px #38BDF8; }
}
.ticker-highlight {
    color: #38BDF8;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'Outfit', sans-serif;
    font-size: 0.86rem;
    flex-shrink: 0;
}
.ticker-content {
    white-space: nowrap;
    color: #94A3B8;
    font-size: 0.85rem;
    letter-spacing: 0.02em;
}

/* Glassmorphic Metric Cards */
.hud-card {
    background: rgba(17, 24, 39, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-left: 3.5px solid #38BDF8;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 16px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.35);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.hud-card:hover {
    border-color: rgba(56, 189, 248, 0.35);
    transform: translateY(-2px);
    box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.45), 0 0 20px -5px rgba(56, 189, 248, 0.15);
}
.hud-label {
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #64748B;
    font-weight: 700;
    margin-bottom: 6px;
}
.hud-value {
    font-size: 1.02rem;
    font-weight: 600;
    color: #F8FAFC;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.01em;
}

/* Sophisticated Cool Source Badges */
.badge-vector-sports {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(99, 102, 241, 0.12));
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(56, 189, 248, 0.12);
}
.badge-wiki-sports {
    background: linear-gradient(135deg, rgba(129, 140, 248, 0.12), rgba(168, 85, 247, 0.12));
    color: #A5B4FC;
    border: 1px solid rgba(129, 140, 248, 0.35);
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(129, 140, 248, 0.12);
}
.badge-reject-sports {
    background: linear-gradient(135deg, rgba(244, 63, 94, 0.12), rgba(239, 68, 68, 0.15));
    color: #FB7185;
    border: 1px solid rgba(244, 63, 94, 0.35);
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(244, 63, 94, 0.12);
}

/* Tactical Playbook Inspector */
.playbook-chunk {
    background: rgba(11, 15, 25, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.18);
    border-left: 3px solid #38BDF8;
    padding: 14px 18px;
    margin: 8px 0;
    border-radius: 0 10px 10px 0;
    font-size: 0.87rem;
    line-height: 1.6;
    color: #CBD5E1;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Category Section Header */
.section-header {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: #F8FAFC;
    margin: 22px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Streamlit Button & Tab Enhancements */
div[data-testid="stButton"] > button {
    background: rgba(17, 24, 39, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.16);
    color: #E2E8F0;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.86rem;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
div[data-testid="stButton"] > button:hover {
    background: rgba(56, 189, 248, 0.12);
    border-color: rgba(56, 189, 248, 0.45);
    color: #38BDF8;
    box-shadow: 0 4px 14px -2px rgba(56, 189, 248, 0.2);
    transform: translateY(-1px);
}

/* Streamlit Tabs Styling */
div[data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}
div[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 8px 16px !important;
    transition: color 0.2s ease !important;
}
div[data-baseweb="tab"]:hover {
    color: #38BDF8 !important;
}
div[data-baseweb="tab"][aria-selected="true"] {
    color: #38BDF8 !important;
    border-bottom: 2px solid #38BDF8 !important;
}

/* Chat Message Styling */
div[data-testid="stChatMessage"] {
    background: rgba(17, 24, 39, 0.5);
    border: 1px solid rgba(148, 163, 184, 0.08);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 14px;
    backdrop-filter: blur(8px);
}

/* Expander Styling */
div[data-testid="stExpander"] {
    background: rgba(17, 24, 39, 0.4);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 12px;
    margin-bottom: 12px;
}
"""


def apply_custom_styles():
    """Inject custom Classy Cool Sports Intelligence CSS theme."""
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


def render_hero_header():
    """Render the main hero header banner."""
    st.markdown(
        """
        <div class="sports-brand-container">
            <div class="sports-badge-pill">⚡ Adaptive LangGraph RAG • Cassandra Vector DB • Groq Ultra-Fast</div>
            <div class="sports-title">
                SPORTPULSE AI
            </div>
            <p class="sports-tagline">
                Next-Gen Multi-Source Sports Intelligence Hub • Deep Player Analytics, Match Archives & Real-Time Tactical Breakdown
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ticker_bar():
    """Render the live sports intelligence radar ticker."""
    st.markdown(
        """
        <div class="sports-ticker-bar">
            <div class="ticker-pulse"></div>
            <div class="ticker-highlight">INTELLIGENCE RADAR</div>
            <div class="ticker-content">
                🏏 ICC CRICKET WORLD CUP & IPL &nbsp;•&nbsp; ⚽ UEFA CHAMPIONS LEAGUE & PREMIER LEAGUE &nbsp;•&nbsp; 🏎️ FORMULA 1 GRAND PRIX &nbsp;•&nbsp; 🏀 NBA PLAYOFFS &nbsp;•&nbsp; 🎾 GRAND SLAM TENNIS
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hud_cards(groq_api_key: str, model_name: str, use_astra: bool, active_vector_store, table_name: str, indexed_chunk_count: int):
    """Render the HUD scoreboard metric cards with classy cool colors."""
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        if groq_api_key:
            model_short = model_name.split("/")[-1].upper()
            st.markdown(
                f"""
                <div class="hud-card" style="border-left-color: #38BDF8;">
                    <div class="hud-label">⚡ LLM Engine</div>
                    <div class="hud-value"><span style="color: #38BDF8;">●</span> Groq ({model_short})</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="hud-card" style="border-left-color: #F43F5E;">
                    <div class="hud-label">⚡ LLM Engine</div>
                    <div class="hud-value"><span style="color: #F43F5E;">●</span> Groq API Key Required</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_stat2:
        if use_astra:
            if active_vector_store:
                st.markdown(
                    f"""
                    <div class="hud-card" style="border-left-color: #2DD4BF;">
                        <div class="hud-label">🏟️ Sports Vector Vault</div>
                        <div class="hud-value"><span style="color: #2DD4BF;">●</span> Astra DB Connected (`{table_name}`)</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="hud-card" style="border-left-color: #F43F5E;">
                        <div class="hud-label">🏟️ Sports Vector Vault</div>
                        <div class="hud-value"><span style="color: #F43F5E;">●</span> Astra DB Auth / Token Required</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            chunk_info = f"({indexed_chunk_count} Chunks Indexed)" if indexed_chunk_count > 0 else "(Ready for Ingestion)"
            st.markdown(
                f"""
                <div class="hud-card" style="border-left-color: #38BDF8;">
                    <div class="hud-label">⚡ Local Sports Vault</div>
                    <div class="hud-value"><span style="color: #38BDF8;">●</span> In-Memory Store {chunk_info}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_stat3:
        st.markdown(
            """
            <div class="hud-card" style="border-left-color: #818CF8;">
                <div class="hud-label">🎯 LangGraph Routing</div>
                <div class="hud-value"><span style="color: #818CF8;">●</span> Multi-Source Adaptive Graph</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_source_badge(datasource: str):
    """Render the routing badge indicator."""
    if datasource == "vectorstore":
        st.markdown('<span class="badge-vector-sports">🏟️ Routed to: Sports Vector Vault</span>', unsafe_allow_html=True)
    elif datasource == "non_sports":
        st.markdown('<span class="badge-reject-sports">🛑 Policy Check: Non-Sports Query Filtered</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-wiki-sports">🌐 Routed to: Global Sports Wiki / Web</span>', unsafe_allow_html=True)


def render_playbook_chunk(documents: str):
    """Render the expandable playbook inspect block."""
    if documents:
        with st.expander("📋 Inspect Retrieved Tactical Playbook"):
            st.markdown(f'<div class="playbook-chunk">{documents}</div>', unsafe_allow_html=True)
