"""CodeAgent prompt templates with positional three-argument final_answer."""

from __future__ import annotations

import copy
import importlib.resources

import yaml
from smolagents.agents import PromptTemplates

MANAGED_AGENT_TASK = """You're a helpful agent named '{{name}}'.
You have been submitted this task by your manager.
---
Task:
{{task}}
---
You're helping your manager solve a wider task: so make sure to not provide a one-line answer, but give as much information as possible to give them a clear understanding of the answer.

When finished, call final_answer with exactly three positional raw-string arguments.
Do NOT use keyword arguments (no task_outcome_short=, no outcome_detailed=, etc.).

Required format:
final_answer(
    r"Short version here",
    r"Extremely detailed version here",
    r"Additional context here"
)

Argument mapping:
1. Short version — one or two sentences (task outcome short).
2. Extremely detailed version — full evidence and reasoning.
3. Additional context — caveats or r"" if none.
"""


def get_fact_check_prompt_templates() -> PromptTemplates:
    """Load default smolagents templates and override managed-agent final_answer guidance."""
    raw = yaml.safe_load(
        importlib.resources.files("smolagents.prompts")
        .joinpath("code_agent.yaml")
        .read_text()
    )
    templates = copy.deepcopy(raw)
    templates["managed_agent"]["task"] = MANAGED_AGENT_TASK
    return templates
