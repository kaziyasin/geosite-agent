from dataclasses import dataclass


@dataclass(frozen=True)
class AgentWorkflowResult:
    summary: str
    tool_trace: list[str]
    requires_human_review: bool


def run_demo_workflow(query: str) -> AgentWorkflowResult:
    return AgentWorkflowResult(
        summary=f"Demo workflow accepted query: {query}",
        tool_trace=[
            "classify_intent",
            "retrieve_visual_evidence",
            "retrieve_business_context",
            "score_sites",
            "generate_report",
        ],
        requires_human_review=True,
    )
