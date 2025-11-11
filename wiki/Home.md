# Home

Welcome to the VUTS (Value Understanding Through Sentiment) Wiki!

## 📖 Navigation

- [Home](Home) - Project overview and navigation
- [Getting Started](Getting-Started) - Quick start guide for new users
- [Fetching Module](Fetching-Module) - Financial news collection
- [LLM Module](LLM-Module) - Sentiment analysis with Large Language Models
- [Market Module](Market-Module) - Historical market data fetching
- [Utilities Module](Utilities-Module) - Shared helper functions
- [Architecture](Architecture) - System design and data flow
- [API Reference](API-Reference) - Detailed API documentation

## 🎯 What is VUTS?

VUTS is an AI-powered platform for analyzing financial news sentiment. It:
- Fetches news from multiple sources (Google News, Bing News, Finnhub)
- Analyzes sentiment using Large Language Models (OpenAI GPT)
- Enriches analysis with historical market data
- Provides actionable insights with scores from -10.00 to +10.00

## 🚀 Quick Links

- **[Quick Start Guide](../docs/Quick_Start_Guide.md)** - Get running in 5 minutes
- **[Complete Workflow](../docs/Workflow_Guide.md)** - Detailed usage examples
- **[Development Outline](../docs/Development_Outline.md)** - Project roadmap

## 📊 Key Features

✅ Multi-source news aggregation  
✅ LLM-powered sentiment analysis  
✅ Market context integration  
✅ Web UI for viewing reports and trends  
✅ Centralized CLI with `vuts` command  
✅ Cost-efficient processing (~$0.0006 per article)  
✅ Smart caching and deduplication  
✅ Comprehensive test suite  

## 🏗️ Project Structure

```
vuts/
├── docs/              # Main documentation
├── scratch/           # Application code
│   ├── vuts           # Centralized CLI entrypoint
│   ├── src/
│   │   ├── fetching/  # News collection
│   │   ├── llm/       # Sentiment analysis
│   │   ├── market/    # Market data
│   │   ├── ui/        # Web interface
│   │   ├── tests/     # Test suite
│   │   └── utils/     # Shared utilities
│   └── demo_workflow.py
└── wiki/              # Wiki pages (this directory)
```

## 📝 Contributing

See the main repository README for contribution guidelines.

## ⚠️ Disclaimer

This tool is for research and educational purposes only. Sentiment scores should **not** be considered financial advice.
