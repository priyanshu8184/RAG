from typing import Literal, TypedDict
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from src.tools import get_wikipedia_tool

# Fallback sports keywords heuristic (expanded to include sports persons, positions, terms)
SPORTS_KEYWORDS = [
    "cricket", "cricketer", "football", "footballer", "soccer", "messi", "ronaldo", "kohli", "dhoni",
    "sachin", "tendulkar", "rohit", "sharma", "bumrah", "hardik", "jadeja", "sehwag", "ganguly", "dravid",
    "f1", "formula 1", "hamilton", "verstappen", "senna", "schumacher", "leclerc", "norris", "alonso",
    "nba", "lebron", "jordan", "kobe", "curry", "shaq", "giannis", "durant", "basketball",
    "tennis", "federer", "nadal", "djokovic", "alcaraz", "sinner", "serena", "williams", "sharapova",
    "world cup", "champions league", "premier league", "la liga", "ipl", "olympics", "olympic",
    "stats", "goals", "runs", "wickets", "grand slam", "ballon d'or", "century", "batting", "bowling",
    "striker", "midfielder", "defender", "goalkeeper", "quarterback", "touchdown", "athlete", "sportsperson",
    "player", "coach", "tournament", "championship", "badminton", "sindhu", "saina", "neeraj", "chopra"
]


class RouteQuery(BaseModel):
    """Route a query to vectorstore, wiki_search for sports/sportspeople topics, or non_sports if unrelated."""

    datasource: Literal["vectorstore", "wiki_search", "non_sports"] = Field(
        ...,
        description=(
            "Choose 'vectorstore' for indexed sports vault queries, "
            "'wiki_search' for any sports person / athlete (e.g. Kohli, Messi, Ronaldo, LeBron, Federer, etc.), "
            "competitions, sports trivia, match records, or sports rules, "
            "or 'non_sports' ONLY if the query is completely unrelated to sports, athletes, games, or tournaments."
        ),
    )


class GraphState(TypedDict):
    """Represents the sports intelligence graph state."""

    question: str
    datasource: str
    documents: str
    generation: str


SYSTEM_ROUTER_PROMPT = """You are a strict sports classifier and tactical knowledge router for SportPulse AI.
Your primary role is to identify queries related to SPORTS, ATHLETES, SPORTSPERSONS, LEAGUES, TOURNAMENTS, MATCHES, RULES, and STATS.

CRITICAL CLASSIFICATION RULES:
1. STRICT SPORTS & SPORTSPERSON INCLUSION:
   Any question about:
   - Any athlete, player, sportsperson, cricketer, footballer, racer, tennis player, basketballer, Olympic champion, coach, manager, or sporting icon (e.g., Virat Kohli, Rohit Sharma, MS Dhoni, Sachin Tendulkar, Lionel Messi, Cristiano Ronaldo, Lewis Hamilton, Max Verstappen, LeBron James, Michael Jordan, Roger Federer, Rafael Nadal, Novak Djokovic, Neeraj Chopra, etc.)
   - Any sport (Cricket, Football, Basketball, Tennis, Formula 1, Athletics, Badminton, Hockey, Golf, Boxing, Swimming, etc.)
   - Any sporting tournament, league, World Cup, IPL, Champions League, Grand Prix, Grand Slam, Olympic Games, match, score, record, rule, or tactic
   IS A 100% VALID SPORTS QUERY.

2. STRICT NON-SPORTS FILTER:
   Only select 'non_sports' if the question is TOTALLY UNRELATED to sports or sports personalities (e.g., programming/software code, cooking recipes, general politics, stock market/finance, non-sports geography, movies/entertainment with no sports link, general school math).

3. ROUTING DESTINATION:
   - Select 'wiki_search' for questions about sports personalities, athlete biographies, general sports trivia, tournament overviews, and live sports questions.
   - Select 'vectorstore' if specifically inquiring about indexed playbook archives or deep statistical documents."""


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
                datasource = route_result.get("datasource", "wiki_search")
            else:
                datasource = str(route_result)
        except Exception:
            # Fallback sports heuristic with strict non-sports rejection
            q_lower = question.lower()
            if any(k in q_lower for k in SPORTS_KEYWORDS) or any(
                sk in q_lower for sk in [
                    "who is", "who won", "score", "match", "championship", "tournament",
                    "player", "athlete", "sportsperson", "cricketer", "footballer",
                    "cup", "league", "stadium", "medal", "batsman", "bowler", "captain"
                ]
            ):
                datasource = "wiki_search"
            else:
                datasource = "non_sports"
        return {"datasource": datasource}

    def retrieve_vectorstore_node(state: GraphState):
        question = state["question"]
        docs_text = ""
        retrieval_success = False

        if vector_store is not None:
            try:
                retriever = vector_store.as_retriever(search_kwargs={"k": 4})
                retrieved_docs = retriever.invoke(question)
                if retrieved_docs:
                    valid_chunks = [d.page_content for d in retrieved_docs if d.page_content and len(d.page_content.strip()) > 30]
                    if valid_chunks:
                        docs_text = "\n\n".join(valid_chunks)
                        retrieval_success = True
            except Exception as e:
                docs_text = f"Sports vectorstore retrieval notice: {str(e)}"

        # Seamless Fallback: If vector store is empty, unpopulated, or yielded no matches, fetch from Wikipedia
        datasource = state.get("datasource", "vectorstore")
        if not retrieval_success or not docs_text or len(docs_text.strip()) < 50:
            try:
                wiki = get_wikipedia_tool()
                wiki_result = wiki.invoke(question)
                if wiki_result and len(str(wiki_result).strip()) > 30:
                    docs_text = str(wiki_result)
                    datasource = "wiki_search"
                else:
                    docs_text = docs_text or "General Sports Intelligence Engine Context"
            except Exception:
                docs_text = docs_text or "General Sports Intelligence Engine Context"

        return {"documents": docs_text, "datasource": datasource}

    def wiki_search_node(state: GraphState):
        question = state["question"]
        wiki = get_wikipedia_tool()
        try:
            wiki_result = wiki.invoke(question)
            docs_text = str(wiki_result)
        except Exception as e:
            docs_text = f"Wikipedia sports search error: {str(e)}"
        return {"documents": docs_text, "datasource": "wiki_search"}

    def reject_non_sports_node(state: GraphState):
        """Strictly reject queries unrelated to sports."""
        rejection_msg = (
            "⚡ **SportPulse AI Policy Notice**\n\n"
            "I am designed and specialized to answer questions **strictly related to sports, athletics, and sports personalities only**.\n\n"
            "Please ask questions related to:\n"
            "- **Sports Personalities & Athletes** (e.g. Virat Kohli, MS Dhoni, Lionel Messi, Cristiano Ronaldo, LeBron James, Lewis Hamilton, Roger Federer, etc.)\n"
            "- **Sports & Competitions** (Cricket, Football, Tennis, Formula 1, Basketball, Olympics, etc.)\n"
            "- **Matches, Tournaments & Leagues** (World Cups, IPL, Champions League, Grand Slams, etc.)\n"
            "- **Records, Player Statistics, Match Tactics, & Rules**."
        )
        return {
            "generation": rejection_msg,
            "documents": "",
            "datasource": "non_sports",
        }

    def generate_node(state: GraphState):
        question = state["question"]
        documents = state["documents"]

        augmented_prompt = f"""You are SportPulse AI — an elite Sports Analyst and Tactical Strategist specializing in all sports, tournaments, matches, and sports personalities / athletes (cricketers, footballers, tennis players, racers, basketball players, Olympic champions, etc.).

CRITICAL POLICY & STYLE MANDATES:
1. SPORTS & SPORTSPERSON SCOPE:
   - You answer questions related to sports, athletic games, tournaments, and any sports personality or athlete (e.g., Virat Kohli, Rohit Sharma, MS Dhoni, Messi, Ronaldo, LeBron, Hamilton, Federer, etc.).
   - Provide a comprehensive, authoritative, high-energy breakdown detailing their sport, role, career milestones, iconic records, championships, and tactical legacy.
2. SYNTHESIS & FACTUAL ACCURACY:
   - Use the retrieved sports context below along with your authoritative sports intelligence to give a full, detailed answer.
   - Do NOT give empty refusals or say "insufficient data" when asked about famous athletes, players, or sports events. Always provide the complete tactical and career breakdown.
3. STRICT NON-SPORTS REFUSAL:
   - If the user question is strictly unrelated to sports or sports personalities (e.g. writing python code, cooking recipes, general non-sports politics), decline politely by stating: "I am programmed to answer questions related to sports and sports personalities only. Please ask a sports-related question."
4. STRUCTURE & FORMATTING:
   - Group information under topical markdown headers (e.g., `### 🏏 Career Overview & Identity`, `### 🏆 Major Trophies & Milestones`, `### 📊 Key Statistics & Records`, `### 🎯 Playing Style & Tactical Mastery`).
   - Format information in CRISP, CLEAN BULLET POINTS (`- `).
   - Highlight key statistics, dates, and names in **bold**.
   - NEVER use `<br>` tags or HTML tags anywhere.
   - DO NOT output messy markdown tables.

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

