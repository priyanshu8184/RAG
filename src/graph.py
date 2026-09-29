from typing import Literal, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from src.tools import get_wikipedia_tool

# Fallback sports keywords heuristic
SPORTS_KEYWORDS = [
    "cricket", "football", "soccer", "messi", "ronaldo", "kohli", "dhoni",
    "f1", "formula 1", "hamilton", "verstappen", "nba", "lebron", "jordan",
    "tennis", "federer", "nadal", "djokovic", "world cup", "champions league",
    "ipl", "olympics", "stats", "goals", "runs", "wickets", "grand slam",
]


class RouteQuery(BaseModel):
    """Route a query to vectorstore, wiki_search for sports topics, or non_sports if unrelated."""

    datasource: Literal["vectorstore", "wiki_search", "non_sports"] = Field(
        ...,
        description="Choose 'vectorstore' for indexed sports stats/records, 'wiki_search' for other sports/athletes/competitions, or 'non_sports' if the query is NOT related to sports, games, athletics, or sporting tournaments/athletes.",
    )


class GraphState(TypedDict):
    """Represents the sports intelligence graph state."""

    question: str
    datasource: str
    documents: str
    generation: str


import re

SYSTEM_ROUTER_PROMPT = """You are a strict sports classifier and tactical knowledge router.
Your job is to determine whether the user question is related to SPORTS, athletic games, tournaments, athletes, leagues, rules, scores, or tactics.

CRITICAL CLASSIFICATION RULES:
1. STRICT NON-SPORTS FILTER: If the question is NOT related to sports (e.g., programming, code, cooking, recipes, politics, general history, geography, science, math, movies, music, personal life unrelated to sports, or general banter), you MUST select 'non_sports'.
2. SPORTS QUERIES: If the question IS related to sports:
   - Select 'vectorstore' if it asks about deeply indexed sports legends (Kohli, Rohit, Messi, Ronaldo, Dhoni, Sachin, Hamilton, Verstappen, LeBron, Jordan, Federer, Nadal, Djokovic) or major tournaments (Cricket World Cups, IPL, UEFA Champions League, FIFA World Cup, F1 Grand Prix, NBA Finals, Grand Slams, Olympic records).
   - Select 'wiki_search' for any other sports topic, unindexed athlete, tournament, sports rules, or sports trivia."""


def clean_sports_output(text: str) -> str:
    """Clean and reformat output to eliminate <br> tags, unpack cramped tables, and guarantee crisp bullet points."""
    if not text:
        return ""

    # If the text contains a markdown table with <br> tags, unpack it into crisp bullet points
    lines = text.strip().splitlines()
    is_table_with_br = any("|" in line for line in lines) and any("<br" in line.lower() for line in lines)
    if is_table_with_br:
        cleaned_lines = []
        for line in lines:
            trimmed = line.strip()
            # Skip divider lines like |---|---|
            if not trimmed or re.match(r"^[\|\s\-:]+$", trimmed):
                continue
            cells = [c.strip() for c in trimmed.split("|") if c.strip()]
            if len(cells) >= 2 and not cells[0].lower().startswith("category"):
                header = cells[0].strip()
                val = " | ".join(cells[1:])
                cleaned_lines.append(f"\n### {header}")
                items = re.split(r"<br\s*/?>", val, flags=re.IGNORECASE)
                for it in items:
                    it_clean = re.sub(r"^[•\-\*\s]+", "", it).strip()
                    if it_clean:
                        if ";" in it_clean and not any(k in it_clean.lower() for k in ["&amp;", "&lt;", "&gt;"]):
                            sub_items = it_clean.split(";")
                            for sit in sub_items:
                                if sit.strip():
                                    cleaned_lines.append(f"- {sit.strip()}")
                        else:
                            cleaned_lines.append(f"- {it_clean}")
            elif not ("|" in line and any(k in line.lower() for k in ["highlights", "category", "details"])):
                cleaned_lines.append(line)
        text = "\n".join(cleaned_lines)

    # Convert any lingering <br> followed by bullet into clean newline bullet
    text = re.sub(r"<br\s*/?>\s*[•\-\*]\s*", "\n- ", text, flags=re.IGNORECASE)
    # Convert remaining <br> tags into clean newlines
    text = re.sub(r"<br\s*/?>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</br>", "", text, flags=re.IGNORECASE)
    # Normalize unicode bullet • into markdown bullet -
    text = re.sub(r"^[ \t]*[•]\s*", "- ", text, flags=re.MULTILINE)

    return text.strip()


def build_sports_rag_graph(groq_key: str, model_id: str, temp: float, vector_store):
    """Construct and compile the adaptive sports RAG LangGraph workflow.

    Args:
        groq_key: Groq API key for LLM inference.
        model_id: Groq model name string.
        temp: LLM temperature.
        vector_store: Active vector store instance (Astra or in-memory).

    Returns:
        Compiled LangGraph application.
    """
    # 1. Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key=groq_key,
        model_name=model_id,
        temperature=temp,
    )

    # 2. Structured Sports Router
    structured_llm_router = llm.with_structured_output(RouteQuery)
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_ROUTER_PROMPT),
            ("human", "{question}"),
        ]
    )
    question_router = route_prompt | structured_llm_router

    # Nodes
    def route_question_node(state: GraphState):
        question = state["question"]
        try:
            route_result = question_router.invoke({"question": question})
            if hasattr(route_result, "datasource"):
                datasource = route_result.datasource
            elif isinstance(route_result, dict):
                datasource = route_result.get("datasource", "vectorstore")
            else:
                datasource = str(route_result)
        except Exception:
            # Fallback sports heuristic with strict non-sports rejection
            q_lower = question.lower()
            if any(k in q_lower for k in SPORTS_KEYWORDS):
                datasource = "vectorstore"
            elif any(sk in q_lower for sk in ["who won", "score", "match", "championship", "tournament", "player", "athlete", "cup", "league", "stadium", "medal"]):
                datasource = "wiki_search"
            else:
                datasource = "non_sports"
        return {"datasource": datasource}

    def retrieve_vectorstore_node(state: GraphState):
        question = state["question"]
        if vector_store is not None:
            try:
                retriever = vector_store.as_retriever(search_kwargs={"k": 4})
                retrieved_docs = retriever.invoke(question)
                docs_text = "\n\n".join([d.page_content for d in retrieved_docs])
            except Exception as e:
                docs_text = f"Sports vectorstore retrieval error: {str(e)}"
        else:
            docs_text = "Vector store is not currently populated. Ingest documents in sidebar or use Wikipedia fallback."
        return {"documents": docs_text}

    def wiki_search_node(state: GraphState):
        question = state["question"]
        wiki = get_wikipedia_tool()
        try:
            wiki_result = wiki.invoke(question)
        except Exception as e:
            wiki_result = f"Wikipedia sports search error: {str(e)}"
        return {"documents": str(wiki_result)}

    def reject_non_sports_node(state: GraphState):
        """Strictly reject queries unrelated to sports."""
        rejection_msg = (
            "⚡ **SportPulse AI Policy Notice**\n\n"
            "I am designed and specialized to answer questions **strictly related to sports only**.\n\n"
            "Please ask questions related to sports, athletic competitions, tournaments, or athletes "
            "(such as cricket, football, tennis, Formula 1, basketball, tournament records, player statistics, "
            "match tactics, or sporting history)."
        )
        return {
            "generation": rejection_msg,
            "documents": "",
            "datasource": "non_sports",
        }

    def generate_node(state: GraphState):
        question = state["question"]
        documents = state["documents"]

        augmented_prompt = f"""You are SportPulse AI — an elite Sports Analyst and Tactical Strategist.

CRITICAL POLICY & STYLE MANDATES:
1. SPORTS-ONLY CRITERIA: You are strictly forbidden from answering questions unrelated to sports. If the question or context is not about sports, athletes, tournaments, or games, decline to answer and state: "I am programmed to answer questions related to sports only. Please ask a sports-related question."
2. Present your breakdown in CRISP, CLEAN BULLET POINTS (`- `) grouped under topical section headers (e.g., `### 🏏 Debut & Career Overview`, `### 🏆 Major Trophies & Titles`, `### 📊 Statistical Milestones`, `### 🎯 Tactical Analysis`).
3. MANDATORY: NEVER use `<br>` tags or HTML tags anywhere.
4. DO NOT output dense markdown tables where cells have multiple items. Instead, use clear, readable bullet lists.
5. Keep each bullet point punchy, concise, and highlight key records, numbers, and dates in **bold**.
6. Answer strictly using ONLY the provided sports context. Do not invent outside facts.
7. If the context does not contain enough data, state: "The current sports context does not have sufficient data to answer this conclusively."

### Sports Context / Playbook:
{documents}

### User Question:
{question}

### Tactical Breakdown & Analysis:
"""
        response = llm.invoke(augmented_prompt)
        cleaned_response = clean_sports_output(response.content)
        return {"generation": cleaned_response}

    # Conditional routing decision
    def decide_to_route(state: GraphState):
        return state["datasource"]

    # Build Graph
    workflow = StateGraph(GraphState)
    workflow.add_node("router", route_question_node)
    workflow.add_node("vectorstore", retrieve_vectorstore_node)
    workflow.add_node("wiki_search", wiki_search_node)
    workflow.add_node("reject_non_sports", reject_non_sports_node)
    workflow.add_node("generate", generate_node)

    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        decide_to_route,
        {
            "vectorstore": "vectorstore",
            "wiki_search": "wiki_search",
            "non_sports": "reject_non_sports",
        },
    )
    workflow.add_edge("vectorstore", "generate")
    workflow.add_edge("wiki_search", "generate")
    workflow.add_edge("reject_non_sports", END)
    workflow.add_edge("generate", END)

    return workflow.compile()
