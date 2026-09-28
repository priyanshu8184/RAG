import streamlit as st


@st.cache_resource
def get_wikipedia_tool():
    """Initialize and cache the Wikipedia sports search tool."""
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper

    api_wrapper = WikipediaAPIWrapper(top_k_results=4, doc_content_chars_max=2500)
    return WikipediaQueryRun(api_wrapper=api_wrapper)
