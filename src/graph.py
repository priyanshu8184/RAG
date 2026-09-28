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
    """Route a sports query to the most relevant datasource."""

    datasource: Literal["vectorstore", "wiki_search"] = Field(
        ...,
        description="Given a user question choose to route it to wikipedia or a specialized sports vectorstore.",
    )


class GraphState(TypedDict):
    """Represents the sports intelligence graph state."""

    question: str
    datasource: str
    documents: str
    generation: str


SYSTEM_ROUTER_PROMPT = """You are a world-class sports analytics and knowledge routing assistant.
The vectorstore contains curated, high-fidelity sports archives, player stats, tactical breakdowns, tournament histories (Cricket World Cups, IPL, UEFA Champions League, FIFA World Cup, F1 Grand Prix, NBA Finals, Grand Slams, Olympic records, legends like Virat Kohli, Lionel Messi, Cristiano Ronaldo, MS Dhoni, LeBron James, Lewis Hamilton, Federer, Nadal, Djokovic).
Use the vectorstore for deep sports player stats, tournament records, tactical breakdowns, and indexed sports topics.
For general trivia, current broad queries, or non-indexed topics, route to wiki_search."""


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
            # Fallback sports heuristic
            if any(k in question.lower() for k in SPORTS_KEYWORDS):
                datasource = "vectorstore"
            else:
                datasource = "wiki_search"
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

    def generate_node(state: GraphState):
        question = state["question"]
        documents = state["documents"]

        augmented_prompt = f"""You are SportPulse AI — an elite, high-energy Sports Analyst and Tactical Strategist (comparable to top ESPN / Sky Sports / Cricbuzz lead analysts).

Instructions:
1. Answer the sports question accurately and clearly using ONLY the provided context.
2. Structure your response with compelling highlights, key player records, match statistics, or tactical takeaways whenever present in the context.
3. Be professional, engaging, and enthusiastic yet strictly factual.
4. Do not invent outside facts or speculate beyond the provided context.
5. If the context does not contain enough information, state: "The current sports context does not have sufficient data to answer this conclusively."

### Sports Context / Playbook:
{documents}

### User Question:
{question}

### Tactical Breakdown & Analysis:
"""
        response = llm.invoke(augmented_prompt)
        return {"generation": response.content}

    # Conditional routing decision
    def decide_to_route(state: GraphState):
        return state["datasource"]

    # Build Graph
    workflow = StateGraph(GraphState)
    workflow.add_node("router", route_question_node)
    workflow.add_node("vectorstore", retrieve_vectorstore_node)
    workflow.add_node("wiki_search", wiki_search_node)
    workflow.add_node("generate", generate_node)

    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        decide_to_route,
        {
            "vectorstore": "vectorstore",
            "wiki_search": "wiki_search",
        },
    )
    workflow.add_edge("vectorstore", "generate")
    workflow.add_edge("wiki_search", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
