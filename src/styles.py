import streamlit as st

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=Orbitron:wght@700;900&display=swap');

/* Global Typography & Background adjustments */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sports Header Styling */
.sports-brand-container {
    background: linear-gradient(135deg, rgba(14, 23, 42, 0.95) 0%, rgba(15, 30, 60, 0.9) 50%, rgba(9, 14, 26, 0.95) 100%);
    border: 1px solid rgba(0, 229, 255, 0.25);
    box-shadow: 0 10px 30px -10px rgba(0, 255, 135, 0.2), inset 0 0 20px rgba(0, 229, 255, 0.05);
    border-radius: 16px;
    padding: 24px 30px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.sports-brand-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00FF87 0%, #60EFFF 50%, #FFB800 100%);
}
.sports-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 255, 135, 0.12);
    color: #00FF87;
    border: 1px solid rgba(0, 255, 135, 0.4);
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.sports-title {
    font-family: 'Orbitron', 'Rajdhani', sans-serif;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #FFFFFF 0%, #60EFFF 45%, #00FF87 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.sports-tagline {
    color: #94A3B8;
    font-size: 1.05rem;
    font-weight: 500;
    margin: 0;
}

/* Live Sports Ticker Bar */
.sports-ticker-bar {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 8px 16px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.88rem;
    color: #CBD5E1;
    overflow: hidden;
}
.ticker-pulse {
    width: 10px;
    height: 10px;
    background-color: #EF4444;
    border-radius: 50%;
    box-shadow: 0 0 10px #EF4444;
    animation: pulseAnimation 1.5s infinite;
    flex-shrink: 0;
}
@keyframes pulseAnimation {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(1.2); }
    100% { opacity: 1; transform: scale(1); }
}
.ticker-highlight {
    color: #00FF87;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    flex-shrink: 0;
}
.ticker-content {
    white-space: nowrap;
    color: #94A3B8;
}

/* HUD Scoreboard Metric Cards */
.hud-card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #60EFFF;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 16px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.hud-card:hover {
    border-color: #00FF87;
    transform: translateY(-2px);
}
.hud-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    font-weight: 700;
    margin-bottom: 4px;
}
.hud-value {
    font-size: 1.05rem;
    font-weight: 700;
    color: #F8FAFC;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Source Badges */
.badge-vector-sports {
    background: linear-gradient(90deg, rgba(0, 255, 135, 0.15), rgba(0, 229, 255, 0.15));
    color: #00FF87;
    border: 1px solid rgba(0, 255, 135, 0.5);
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 12px;
    box-shadow: 0 0 15px rgba(0, 255, 135, 0.15);
}
.badge-wiki-sports {
    background: linear-gradient(90deg, rgba(255, 184, 0, 0.15), rgba(255, 107, 0, 0.15));
    color: #FFB800;
    border: 1px solid rgba(255, 184, 0, 0.5);
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 12px;
    box-shadow: 0 0 15px rgba(255, 184, 0, 0.15);
}

/* Playbook Tactical Chunk */
.playbook-chunk {
    background: rgba(10, 16, 30, 0.85);
    border: 1px solid rgba(96, 239, 255, 0.2);
    border-left: 3px solid #00FF87;
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.88rem;
    line-height: 1.5;
    color: #CBD5E1;
}

/* Category Header Banner */
.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #F1F5F9;
    margin: 18px 0 10px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
"""

def apply_custom_styles():
    """Inject custom Athletic Cyber-Sports CSS theme."""
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
    """Render the HUD scoreboard metric cards."""
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        if groq_api_key:
            model_short = model_name.split("/")[-1].upper()
            st.markdown(
                f"""
                <div class="hud-card" style="border-left-color: #00FF87;">
                    <div class="hud-label">⚡ LLM Engine</div>
                    <div class="hud-value">🟢 Groq ({model_short})</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="hud-card" style="border-left-color: #EF4444;">
                    <div class="hud-label">⚡ LLM Engine</div>
                    <div class="hud-value">🔴 Groq API Key Required</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_stat2:
        if use_astra:
            if active_vector_store:
                st.markdown(
                    f"""
                    <div class="hud-card" style="border-left-color: #60EFFF;">
                        <div class="hud-label">🏟️ Sports Vector Vault</div>
                        <div class="hud-value">🟢 Astra DB Connected (`{table_name}`)</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="hud-card" style="border-left-color: #EF4444;">
                        <div class="hud-label">🏟️ Sports Vector Vault</div>
                        <div class="hud-value">🔴 Astra DB Auth / Token Required</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            chunk_info = f"({indexed_chunk_count} Chunks Indexed)" if indexed_chunk_count > 0 else "(Ready for Ingestion)"
            st.markdown(
                f"""
                <div class="hud-card" style="border-left-color: #00FF87;">
                    <div class="hud-label">⚡ Local Sports Vault</div>
                    <div class="hud-value">🟢 In-Memory Store {chunk_info}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_stat3:
        st.markdown(
            """
            <div class="hud-card" style="border-left-color: #A855F7;">
                <div class="hud-label">🎯 LangGraph Routing</div>
                <div class="hud-value">🟣 Multi-Source Adaptive Graph</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_source_badge(datasource: str):
    """Render the routing badge indicator."""
    if datasource == "vectorstore":
        st.markdown('<span class="badge-vector-sports">🏟️ Routed to: Sports Vector Vault</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-wiki-sports">🌐 Routed to: Global Sports Wiki / Web</span>', unsafe_allow_html=True)


def render_playbook_chunk(documents: str):
    """Render the expandable playbook inspect block."""
    if documents:
        with st.expander("📋 Inspect Retrieved Tactical Playbook"):
            st.markdown(f'<div class="playbook-chunk">{documents}</div>', unsafe_allow_html=True)
