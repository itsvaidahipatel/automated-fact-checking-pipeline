"""Three-argument final_answer tool compatible with smolagents CodeAgent."""

from __future__ import annotations

from smolagents import Tool


class FactCheckFinalAnswerTool(Tool):
    """
    Replaces the default single-argument FinalAnswerTool.

    Managed agents must call with exactly three positional string arguments.
    """

    name = "final_answer"
    description = (
        "Returns the final answer and ends the agent run. "
        "Call with three positional string arguments only (no keyword arguments): "
        "outcome_short, outcome_detailed, additional_context."
    )
    inputs = {
        "outcome_short": {
            "type": "string",
            "description": "Brief task outcome (one or two sentences).",
        },
        "outcome_detailed": {
            "type": "string",
            "description": "Full detailed outcome for the manager.",
        },
        "additional_context": {
            "type": "string",
            "description": "Extra context, caveats, or empty string if none.",
        },
    }
    output_type = "string"

    def forward(
        self,
        outcome_short: str,
        outcome_detailed: str,
        additional_context: str,
    ) -> str:
        return (
            f"### 1. Task outcome (short version):\n{outcome_short}\n\n"
            f"### 2. Task outcome (extremely detailed version):\n{outcome_detailed}\n\n"
            f"### 3. Additional context (if relevant):\n{additional_context}"
        )


def get_final_answer_tool() -> FactCheckFinalAnswerTool:
    """Factory for the shared final_answer tool instance."""
    return FactCheckFinalAnswerTool()
