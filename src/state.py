from typing import TypedDict

class AgentState(TypedDict):
    alert: str
    metrics_report: str
    investigation_complete: bool
    final_diagnosis: str
    iteration_count: int