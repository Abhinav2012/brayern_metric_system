import os
from langchain_groq import ChatGroq
from loguru import logger
from state import AgentState
from dotenv import load_dotenv


load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def commander_node(state: AgentState):
    """Analyzes alerts and metrics to decide next steps."""
    current_count = state.get("iteration_count", 0) + 1
    logger.info(f"Cycle {current_count}/30: Commander analyzing...")
    
    prompt = [
        ("system", "You are the AI Incident Commander. "
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

def metrics_agent_node(state: AgentState):
    """Simulates gathering system metrics."""
    service = os.getenv("SERVICE_NAME", "payment-gateway")
    mock_metrics = f"Service: {service} | CPU: 94% | Mem: 88% | Latency: 1200ms"
    logger.warning(f"Metrics Agent gathered: {mock_metrics}")
    return {"metrics_report": mock_metrics}