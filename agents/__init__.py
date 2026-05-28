"""Multi-agent fact-checking orchestration layer."""

from agents.claim_agent import create_claim_agent
from agents.extractor_agent import create_extractor_agent
from agents.manager_agent import create_manager_agent, run_fact_check
from agents.research_agent import create_research_agent
from agents.social_manager_agent import create_social_manager_agent, run_social_fact_check

__all__ = [
    "create_claim_agent",
    "create_extractor_agent",
    "create_manager_agent",
    "create_research_agent",
    "run_fact_check",
    "create_social_manager_agent",
    "run_social_fact_check",
]
