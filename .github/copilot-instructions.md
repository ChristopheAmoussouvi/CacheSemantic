<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI Data Interaction Agent - Development Instructions

## Project Overview
This is a Streamlit-based AI agent application for natural language interaction with data (CSV/Excel files). The project uses:
- **Frontend**: Streamlit for the user interface
- **AI Agent**: LangChain for natural language processing
- **Vector Database**: ChromaDB with persistent storage
- **Semantic Caching**: FAISS for intelligent caching
- **Visualization**: Seaborn/Matplotlib with export capabilities

## ✅ Project Status - COMPLETED
- [x] Project structure created and organized
- [x] All core components implemented (SemanticCache, DataManager, AIAgent)
- [x] Dependencies installed and validated
- [x] Streamlit interface developed with modern UI
- [x] Configuration files created (.env, .streamlit/config.toml)
- [x] Documentation completed (README.md, QUICKSTART.md)
- [x] Test suite implemented and validated
- [x] Sample data provided for testing
- [x] Startup scripts created (start.bat, start.ps1)

## 🎯 Key Features Implemented
### 🧠 AI Intelligence
- **LangChain Integration**: Natural language processing with OpenAI GPT models
- **Semantic Caching**: FAISS-based intelligent caching system (85% similarity threshold)
- **Vector Database**: ChromaDB for persistent data storage and semantic search

### 📊 Data Processing
- **Multi-format Support**: CSV, XLSX, XLS file handling
- **Automatic Indexing**: Data is automatically vectorized and indexed
- **Smart Chunking**: Large files are processed in manageable chunks

### 📈 Visualization Engine
- **Automatic Chart Generation**: AI determines appropriate chart types
- **Multiple Chart Types**: Histograms, scatter plots, line charts, bar charts, heatmaps, boxplots
- **High-Quality Export**: PNG export at 300 DPI resolution
- **Interactive Interface**: Charts displayed directly in chat with download buttons

### 💬 Chat Interface
- **Natural Language Queries**: Ask questions in French about your data
- **Conversation Memory**: Maintains context throughout the session
- **Smart Response Routing**: Cache → Pandas Agent → LLM with context
- **Source Attribution**: Shows where each response originated

## 🛠 Technical Architecture
```
ChatPOC2/
├── app.py                     # Main Streamlit application
├── src/components/
│   ├── semantic_cache.py      # FAISS-based semantic caching
│   ├── data_manager.py        # ChromaDB vector database management
│   └── ai_agent.py           # LangChain AI agent with visualization
├── data/                      # Sample data files
├── cache/                     # FAISS cache storage
├── chroma_db/                 # ChromaDB persistent storage
└── exports/                   # Generated visualizations
```

## 🚀 Usage Instructions
1. **Setup**: Copy `.env.example` to `.env` and add OpenAI API key
2. **Start**: Run `start.bat` or `streamlit run app.py`
3. **Access**: Open browser to http://localhost:8501
4. **Load Data**: Upload CSV/Excel files via sidebar
5. **Interact**: Ask questions in natural French language

## 💡 Example Queries
- "Montre-moi un résumé des données"
- "Crée un graphique des ventes par région"
- "Quelle est la tendance des prix dans le temps?"
- "Trouve les corrélations entre les variables"

## 🔧 Configuration
- **Cache Threshold**: Adjust `SEMANTIC_CACHE_THRESHOLD` in .env
- **Model Selection**: Change `LLM_MODEL` for different OpenAI models
- **UI Customization**: Modify `.streamlit/config.toml` for theme changes

## ✅ Validation Results
All components tested and validated:
- ✅ Dependencies installed correctly
- ✅ Configuration files present
- ✅ Unit tests passing (7/7)
- ✅ Integration tests successful
- ✅ Streamlit application starts correctly

## 📚 Documentation
- **Complete Guide**: README.md
- **Quick Start**: QUICKSTART.md
- **Validation**: Run `python validate.py`

The AI Data Interaction Agent is now fully functional and ready for production use!
