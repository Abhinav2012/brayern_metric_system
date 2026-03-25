from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from state import AgentState
from agents import commander_node, metrics_agent_node
from logger_agent import export_json_node

# Load environment variables (API Keys, etc.)
load_dotenv()

def router(state: AgentState):
    """Determines if the workflow should continue or finish."""
    if state["investigation_complete"]:
        return "export_json"
    return "metrics_agent"

# Initialize the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("commander", commander_node)
workflow.add_node("metrics_agent", metrics_agent_node)
workflow.add_node("export_json", export_json_node)

# Define Edges
workflow.set_entry_point("commander")
workflow.add_edge("metrics_agent", "commander")
workflow.add_edge("export_json", END)

# Add Conditional Routing
workflow.add_conditional_edges("commander", router)

# Compile
app = workflow.compile()

if __name__ == "__main__":
    initial_input = {
        "alert": "Critical: Payment Gateway Latency Spike", 
        "metrics_report": "",
        "investigation_complete": False,
        "iteration_count": 0
    }
    
    print("--- Starting Incident Investigation ---")
    for output in app.stream(initial_input):
        # Optional: Print the current node's output for visibility
        print(output)