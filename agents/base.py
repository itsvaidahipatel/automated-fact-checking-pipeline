"""Shared CodeAgent construction helpers."""

from __future__ import annotations

from typing import Any

from smolagents import CodeAgent, Tool

from agents.final_answer_tool import get_final_answer_tool
from agents.model_factory import create_vllm_model
from agents.prompt_templates import get_fact_check_prompt_templates
from config import Settings


def build_code_agent(
    *,
    settings: Settings,
    tools: list[Tool] | None = None,
    instructions: str,
    **agent_kwargs: Any,
) -> CodeAgent:
    """Create a CodeAgent with the three-argument final_answer tool registered."""
    agent_tools = list(tools or [])
    agent_tools.append(get_final_answer_tool())

    prompt_templates = agent_kwargs.pop("prompt_templates", None) or get_fact_check_prompt_templates()

    agent = CodeAgent(
        tools=agent_tools,
        model=create_vllm_model(settings),
        instructions=instructions,
        prompt_templates=prompt_templates,
        **agent_kwargs,
    )
    # Force override — smolagents setdefault would keep FinalAnswerTool (1-arg) otherwise
    agent.tools["final_answer"] = get_final_answer_tool()
    return agent
