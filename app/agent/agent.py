"""Core LangGraph agent runtime for Orion."""

from __future__ import annotations

import uuid
from typing import Any

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import tools
from app.config.llm import get_llm
from app.config.settings import settings


def run_agent(question: str, session_id: str) -> dict[str, Any]:
    """Run the Orion agent for a user question and return answer metadata."""

    _ = (question, session_id, uuid, SYSTEM_PROMPT, tools, get_llm, settings)
    # TODO(Phase 3): build the LangGraph agent runtime.
    # Suggested checklist:
    # - initialize the LLM once at module level with get_llm()
    # - create the LangGraph checkpointer
    # - create the agent with create_react_agent(...)
    # - invoke it with the user's question
    # - generate a session_id when one is not provided
    # - return: answer, session_id, steps, model_used
    raise NotImplementedError("TODO: implement run_agent() in app/agent/agent.py")
