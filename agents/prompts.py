"""Shared prompt fragments for all CodeAgents."""

FINAL_ANSWER_INSTRUCTIONS = r"""
When you are done, you MUST call final_answer with exactly three positional string arguments.
Do NOT use keyword arguments (no task_outcome_short=, no outcome_detailed=, no outcome_short=).

Pass only the 3 required strings as positional arguments. Use raw strings (prefix with r).

Required format:
final_answer(
    r"Short version here",
    r"Extremely detailed version here",
    r"Additional context here"
)

Rules:
- Never use named arguments like task_outcome_short= or outcome_detailed=.
- If there is no extra context, pass r"" as the third argument.
- Never call final_answer with one or two arguments only.
"""
