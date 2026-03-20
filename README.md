# Multi-Agent Research Paper Generator (Groq API + LangGraph)

This project generates a complete research paper from a topic using a 5-agent pipeline:

1. Supervisor
2. Researcher
3. Writer
4. Critic
5. Editor

The supervisor orchestration is implemented with LangGraph.

## Features

- Topic input from Streamlit UI
- Web research using DuckDuckGo
- Draft generation with Groq LLM via OpenAI-compatible SDK
- LangGraph state graph orchestration for reliable stage execution
- Strict critical review with score and feedback
- Final polished markdown paper
- Download final paper as `.md`

## Project Structure

- `app.py`
- `agents/`
- `utils/`
- `prompts/`
- `.env`
- `requirements.txt`

Key dependency additions:

- `langgraph` for graph-based agent orchestration

## Setup

1. Install dependencies:

   `pip install -r requirements.txt`

2. Update environment values in `.env`:

   - `GROQ_API_KEY`
   - `GROQ_MODEL`
   - `MAX_SOURCES`

3. Run Streamlit:

   `streamlit run app.py`

## Required Output Sections

The generated paper includes:

- Abstract
- Introduction
- Literature Review
- Methodology
- Results
- Conclusion
- References

## Notes

- Sources are collected from DuckDuckGo and deduplicated by normalized URL.
- The system validates that 5 to 10 sources are present.
- The writer and editor are checked for mandatory section completeness.
