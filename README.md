⚡ SportPulse AI — Next-Gen Multi-Source Sports Intelligence Hub

SportPulse AI is a sports analytics, match intelligence, and retrieval-augmented generation (RAG) platform powered by Streamlit, LangGraph, DataStax Astra DB (Cassandra Vector Store), Groq Ultra-Fast LLMs, and Wikipedia / Web Sports Knowledge.

-------------------------------------------------------------------------------------------

🏆 Key Features

⚡Adaptive Sports Query Routing: Uses LangGraph and structured LLM routing to automatically classify sports queries and route them to either the Astra DB Sports Vector Vault (for specialized sports records, player bios, tactical archives) or Wikipedia (for broad sports trivia, recent competitions, and cross-sport knowledge).

🏟️ Curated Sports Knowledge Vault : Built-in sports ingestion pipeline covering Cricket (IPL, World Cups, Virat Kohli, MS Dhoni, Sachin Tendulkar), Football (UEFA Champions League, FIFA World Cup, Messi, Ronaldo), Formula 1 (Hamilton, Verstappen), Basketball (NBA, LeBron James, Jordan), and Tennis (Federer, Nadal, Djokovic).

🎨 High-Octane Cyber-Sports UI: Dynamic stadium dark theme with glowing neon accents, live intelligence radar ticker, real-time scoreboard HUD, and sport category tabs (🏏 Cricket, ⚽ Football, 🏎️ Formula 1, 🏀 Basketball, 🎾 Tennis).

📋 Tactical Playbook Inspection : Inspect retrieved context chunks directly within the interface to audit sources and citations.

⚡ Ultra-Low Latency Inference: Powered by Groq's LPUs running cutting-edge models (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`).

------------------------------------------------------------------------------------------

🛠️ Setup Instructions

1. Create and Activate Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```

3. Configure Credentials (Optional `.env` file)

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Set the values:
- `GROQ_API_KEY`: Your Groq API key from [Groq Console](https://console.groq.com/)
- `ASTRA_DB_APPLICATION_TOKEN`: Your Astra DB Application Token (`AstraCS:...`) from [DataStax Astra](https://astra.datastax.com/)
- `ASTRA_DB_ID`: Your Astra DB Database ID (UUID)

(Alternatively, you can enter these keys directly in the SportPulse AI sidebar).

----------------------------------------------------------------------------------------------------------

🚀 Running the Application

Launch the Streamlit app:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

📂 Project Structure

```
d:/RAG/
├── app.py                      # Main SportPulse AI Streamlit Application Entrypoint
├── src/                        # Modular Application Package
│   ├── __init__.py             # Package marker
│   ├── config.py               # Constants, default sports URLs, supported models & presets
│   ├── styles.py               # Custom Cyber-Sports CSS theme & HTML UI components
│   ├── vectorstore.py          # HuggingFace embeddings, in-memory & Astra DB vector stores
│   ├── tools.py                # External query tools (Wikipedia search wrapper)
│   ├── ingestion.py            # Web scraping, tiktoken chunking & batch vector indexing
│   ├── graph.py                # LangGraph adaptive router & RAG pipeline
│   └── ui.py                   # Streamlit sidebar controls & sport category preset buttons
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment Variable Template
└── README.md                   # Documentation & Setup Guide
```

---

🎯 Sample Sports Prompts

🏏Cricket: "What are Virat Kohli's major batting records in international cricket and run chases?"
⚽ Football: "What are Cristiano Ronaldo's all-time records in the UEFA Champions League?"
🏎️Formula 1: "What are Lewis Hamilton's career achievements and race win records in Formula One?"
🏀Basketball: "What are LeBron James' major NBA career achievements and championships?"
🎾Tennis: "What are the Grand Slam singles title records of Roger Federer, Rafael Nadal, and Novak Djokovic?"
