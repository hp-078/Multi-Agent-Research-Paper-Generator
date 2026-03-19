from __future__ import annotations

from typing import Callable, Optional

from agents.critic import run_critic
from agents.editor import run_editor
from agents.researcher import run_researcher
from agents.writer import run_writer
from utils.schemas import PipelineState
from utils.validators import find_missing_sections

StageCallback = Optional[Callable[[str, str], None]]


def _emit(stage_callback: StageCallback, stage: str, message: str) -> None:
    if stage_callback is not None:
        stage_callback(stage, message)


def run_pipeline(topic: str, stage_callback: StageCallback = None) -> PipelineState:
    clean_topic = " ".join(topic.split()).strip()
    if not clean_topic:
        raise ValueError("Topic cannot be empty.")

    state = PipelineState(topic=clean_topic)
    _emit(stage_callback, "Supervisor", "Starting multi-agent workflow.")

    _emit(stage_callback, "Researcher", "Collecting 5 to 10 reliable sources.")
    state.research = run_researcher(clean_topic)
    source_count = len(state.research.sources)
    if not (5 <= source_count <= 10):
        raise ValueError("Researcher must return between 5 and 10 sources.")
    _emit(stage_callback, "Researcher", f"Collected {source_count} sources.")

    _emit(stage_callback, "Writer", "Generating paper draft.")
    state.draft_paper = run_writer(clean_topic, state.research)
    draft_missing = find_missing_sections(state.draft_paper)
    if draft_missing:
        raise ValueError(
            "Draft is missing required sections: " + ", ".join(draft_missing)
        )

    _emit(stage_callback, "Critic", "Reviewing draft quality.")
    state.review = run_critic(clean_topic, state.draft_paper)
    _emit(stage_callback, "Critic", f"Draft scored {state.review.score}/10.")

    _emit(stage_callback, "Editor", "Polishing final paper.")
    state.final_paper = run_editor(
        topic=clean_topic,
        draft=state.draft_paper,
        review=state.review,
        research=state.research,
    )

    final_missing = find_missing_sections(state.final_paper)
    if final_missing:
        raise ValueError(
            "Final paper is missing required sections: " + ", ".join(final_missing)
        )

    _emit(stage_callback, "Supervisor", "Workflow complete.")
    return state
