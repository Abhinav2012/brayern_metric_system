import json
from loguru import logger
from state import AgentState

def export_json_node(state: AgentState):
    """Formats the final state into a JSON report."""
    report_data = {
        "incident_id": "INC-2026-X",
        "original_alert": state["alert"],
        "final_diagnosis": state["final_diagnosis"],
        "total_cycles": state["iteration_count"],
        "last_metrics_captured": state["metrics_report"],
        "status": "COMPLETED" if "DIAGNOSIS" in state["final_diagnosis"] else "TIMEOUT"
    }
    
    file_name = "output/incident_report.json"
    try:
        with open(file_name, "w") as f:
            json.dump(report_data, f, indent=4)
        logger.success(f"Final report saved to {file_name}")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
        
    return state