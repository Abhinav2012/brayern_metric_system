import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from loguru import logger

# Load variables from .env
load_dotenv()

# 1. Updated State: Added 'count' to track iterations
class AgentState(TypedDict):
    alert: str
    metrics_report: str
    investigation_complete: bool
    final_diagnosis: str
    iteration_count: int  # Tracking cycles

# 2. Initialize Groq
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# --- NODE: COMMANDER AGENT ---
def commander_node(state: AgentState):
    current_count = state.get("iteration_count", 0) + 1
    logger.info(f"Cycle {current_count}/30: Commander analyzing...")
    
    prompt = [
        ("system", "You are the Bayer AI Incident Commander. "
                   "If metrics indicate failure (>80%), provide a DIAGNOSIS. "
                   "Output ONLY 'ACTION: GET_METRICS' or 'DIAGNOSIS: [reason]'."),
        ("user", f"Alert: {state['alert']}\nMetrics: {state['metrics_report']}")
    ]
    
    response = llm.invoke(prompt)
    content = response.content.strip()
    
    # Logic: Finish if diagnosed OR if we hit the 30-cycle limit
    is_done = "DIAGNOSIS" in content or current_count >= 30
    
    return {
        "final_diagnosis": content, 
        "investigation_complete": is_done,
        "iteration_count": current_count
    }

# --- NODE: METRICS AGENT ---
def metrics_agent_node(state: AgentState):
    service = os.getenv("SERVICE_NAME", "payment-gateway")
    # Simulate data
    mock_metrics = f"Service: {service} | CPU: 94% | Mem: 88% | Latency: 1200ms"
    logger.warning(f"Metrics Agent gathered: {mock_metrics}")
    return {"metrics_report": mock_metrics}

# --- NODE: EXPORTER (New End Node) ---
def export_json_node(state: AgentState):
    """Final node to format the output as a JSON file."""
    report_data = {
        "incident_id": "INC-2026-X",
        "original_alert": state["alert"],
        "final_diagnosis": state["final_diagnosis"],
        "total_cycles": state["iteration_count"],
        "last_metrics_captured": state["metrics_report"],
        "status": "COMPLETED" if "DIAGNOSIS" in state["final_diagnosis"] else "TIMEOUT"
    }
    
    file_name = "incident_report.json"
    with open(file_name, "w") as f:
        json.dump(report_data, f, indent=4)
    
    logger.success(f"Final report saved to {file_name}")
    return state

# 3. Updated Graph Construction
def router(state: AgentState):
    # If investigation is done, go to the Exporter, else back to Metrics
    if state["investigation_complete"]:
        return "export_json"
    return "metrics_agent"

workflow = StateGraph(AgentState)

workflow.add_node("commander", commander_node)
workflow.add_node("metrics_agent", metrics_agent_node)
workflow.add_node("export_json", export_json_node) # Final processing node

workflow.set_entry_point("commander")
workflow.add_edge("metrics_agent", "commander")
workflow.add_edge("export_json", END) # Points to terminal END

workflow.add_conditional_edges("commander", router)

app = workflow.compile()

# --- RUN THE AGENT ---
if __name__ == "__main__":
    initial_input = {
        "alert": "Critical: Payment Gateway Latency Spike", 
        "metrics_report": "",
        "investigation_complete": False,
        "iteration_count": 0
    }
    
    for output in app.stream(initial_input):
        print(output)