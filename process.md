# Multi-Agent Research Paper Generator (Groq API) - Process

## 1) Goal
Build a multi-agent AI system that takes a user topic and produces a complete research paper in Markdown using Groq API (OpenAI-compatible), with iterative quality improvement.

## 2) Required Agents
Use 5 agents in this strict sequence:

1. Supervisor Agent
2. Researcher Agent
3. Writer Agent
4. Critic Agent
5. Editor Agent

Final output: polished research paper in Markdown with required sections.

## 3) Tech Stack
- Python 3.10+
- Streamlit
- OpenAI Python SDK (configured for Groq base URL)
- DuckDuckGo search (duckduckgo-search)
- python-dotenv
- Optional: LangChain for prompt templates/chains

## 4) High-Level Workflow

User Topic -> Supervisor -> Researcher -> Writer -> Critic -> Editor -> Final Markdown Paper

## 5) Output Requirements (Writer + Editor)
The final paper must include:
- Abstract
- Introduction
- Literature Review
- Methodology
- Results
- Conclusion
- References

## 6) Project Structure

Use this minimal structure:

```
Multi-Agent/
  app.py
  .env
  requirements.txt
  process.md
  agents/
    supervisor.py
    researcher.py
    writer.py
    critic.py
    editor.py
  prompts/
    researcher_prompt.md
    writer_prompt.md
    critic_prompt.md
    editor_prompt.md
  utils/
    llm.py
    search.py
    schemas.py
```

## 7) Environment and Dependencies

### requirements.txt

```
streamlit>=1.35.0
openai>=1.40.0
duckduckgo-search>=6.2.0
python-dotenv>=1.0.1
pydantic>=2.8.0
```

### .env

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
MAX_SOURCES=8
```

## 8) Groq Client Setup

In `utils/llm.py`:

```python
import os
from openai import OpenAI


def get_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )


def chat_completion(messages, model=None, temperature=0.3, max_tokens=4096):
    client = get_client()
    model_name = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
```

## 9) Data Contracts (Strongly Recommended)

In `utils/schemas.py`:

```python
from pydantic import BaseModel, Field
from typing import List


class SourceItem(BaseModel):
    title: str
    url: str
    snippet: str


class ResearchOutput(BaseModel):
    topic: str
    sources: List[SourceItem] = Field(min_length=5, max_length=10)


class CriticOutput(BaseModel):
    score: int = Field(ge=1, le=10)
    weaknesses: List[str]
    improvements: List[str]


class PipelineState(BaseModel):
    topic: str
    research: ResearchOutput | None = None
    draft_paper: str | None = None
    review: CriticOutput | None = None
    final_paper: str | None = None
```

## 10) Agent Specifications

### A) Supervisor Agent
Responsibilities:
- Accept topic input
- Execute agent pipeline in order
- Validate each stage output
- Return final paper Markdown

Inputs:
- topic (string)

Outputs:
- final_paper (Markdown)

Validation checks:
- Research has 5 to 10 sources
- Draft contains all mandatory sections
- Critic score exists and is 1 to 10
- Final output has references and valid links where possible

### B) Researcher Agent
Responsibilities:
- Query DuckDuckGo for topic
- Gather and deduplicate 5 to 10 relevant sources
- Return source list in structured format

Suggested implementation notes:
- Use 3 to 5 query variants for better coverage
- Deduplicate by normalized URL
- Prefer reputable domains (journals, universities, standards bodies)
- Keep short evidence snippets per source

Pseudo-flow:
1. Build query list from topic
2. Search each query with result cap
3. Merge and deduplicate
4. Rank by relevance keyword overlap
5. Keep top N (5 to 10)

### C) Writer Agent
Responsibilities:
- Generate full research paper from topic + sources
- Follow strict academic structure
- Use in-text citations mapped to references

Prompt constraints:
- Must produce Markdown only
- Must include all required sections
- Must cite only provided sources
- Must include a numbered References section

### D) Critic Agent
Responsibilities:
- Review draft for structure, coherence, evidence use, and clarity
- Return strict feedback

Output format (JSON-like):
- score: 1 to 10
- weaknesses: list of concrete issues
- improvements: actionable edits

Rubric examples:
- Section completeness
- Argument coherence
- Citation quality
- Method clarity
- Language precision

### E) Editor Agent
Responsibilities:
- Improve draft using critic feedback
- Preserve factual integrity and citation mapping
- Return polished final Markdown paper

Rules:
- Do not remove mandatory sections
- Do not invent references absent from source list
- Improve transitions and academic tone

## 11) Prompt Design

Store prompts under `prompts/`.

### researcher_prompt.md (template)
- Role: expert research assistant
- Task: find 5 to 10 reliable sources for {topic}
- Output: structured list with title, url, snippet

### writer_prompt.md (template)
- Role: academic writer
- Inputs: topic + source list
- Task: generate full Markdown paper with required sections
- Constraint: references must match provided URLs

### critic_prompt.md (template)
- Role: strict reviewer
- Input: draft Markdown
- Output: score, weaknesses, improvements

### editor_prompt.md (template)
- Role: senior editor
- Inputs: draft + critic feedback + source list
- Output: improved final Markdown paper

## 12) Supervisor Orchestration Logic

In `agents/supervisor.py`:

```python
from utils.schemas import PipelineState
from agents.researcher import run_researcher
from agents.writer import run_writer
from agents.critic import run_critic
from agents.editor import run_editor


def run_pipeline(topic: str) -> PipelineState:
    state = PipelineState(topic=topic)

    state.research = run_researcher(topic)
    if not (5 <= len(state.research.sources) <= 10):
        raise ValueError("Researcher must return 5 to 10 sources")

    state.draft_paper = run_writer(topic, state.research)

    required_sections = [
        "## Abstract",
        "## Introduction",
        "## Literature Review",
        "## Methodology",
        "## Results",
        "## Conclusion",
        "## References",
    ]
    missing = [s for s in required_sections if s not in state.draft_paper]
    if missing:
        raise ValueError(f"Draft missing sections: {missing}")

    state.review = run_critic(state.draft_paper)

    state.final_paper = run_editor(
        topic=topic,
        draft=state.draft_paper,
        review=state.review,
        research=state.research,
    )
    return state
```

## 13) Streamlit UI Flow

In `app.py`:

1. Input field for topic
2. Generate button
3. Progress indicators for each agent stage
4. Display:
   - source table
   - draft (optional expander)
   - critic feedback
   - final paper
5. Download button for Markdown file

Pseudo-UI steps:

```python
import streamlit as st
from dotenv import load_dotenv
from agents.supervisor import run_pipeline

load_dotenv()
st.set_page_config(page_title="Research Paper Generator", layout="wide")

st.title("Multi-Agent Research Paper Generator")
topic = st.text_input("Enter research topic")

if st.button("Generate Paper") and topic.strip():
    with st.status("Running multi-agent pipeline...", expanded=True) as status:
        state = run_pipeline(topic)
        status.update(label="Done", state="complete")

    st.subheader("Final Paper")
    st.markdown(state.final_paper)

    st.download_button(
        "Download Markdown",
        data=state.final_paper,
        file_name="research_paper.md",
        mime="text/markdown",
    )
```

## 14) Researcher Implementation Notes (DuckDuckGo)

In `utils/search.py`, use `duckduckgo-search`:

```python
from duckduckgo_search import DDGS


def ddg_search(query: str, max_results: int = 10):
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))
```

Recommended safeguards:
- Timeout and retry for transient network errors
- URL deduplication
- Basic domain quality filtering

## 15) Quality and Safety Constraints

- No fabricated citations
- Use only gathered sources in references
- Keep claims aligned with source snippets
- If insufficient sources found, return graceful error and ask to broaden topic

## 16) Validation Checklist

Before showing final output, verify:
- 5 to 10 sources gathered
- All mandatory sections present
- Critic output includes score, weaknesses, improvements
- Final paper includes references with links
- Markdown renders correctly in Streamlit

## 17) Run Instructions

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Set environment variables in `.env`
3. Run app:
   - `streamlit run app.py`
4. Enter topic and generate paper

## 18) Optional Enhancements

- Add iterative loop: if critic score < 8, re-edit once more
- Add citation style selection (APA/IEEE)
- Add PDF export from Markdown
- Cache search results for repeated topics
- Add plagiarism and redundancy checks

## 19) Definition of Done

The feature is complete when:
- User can input a topic in Streamlit
- Pipeline runs all 5 agents in order
- Final Markdown paper includes all required sections
- Critic feedback is visible
- User can download final paper
