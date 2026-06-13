import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from agents.knowledge_graph_agent import kg_node, KGState
from agents.forecast_agent import forecast_node, ForecastState

class Phase3State(TypedDict):
    resolved_path: str
    kg_status: str
    forecast_status: str
    forecast_json: str
    error: str

def run_kg(state: Phase3State) -> Phase3State:
    kg_state = KGState(resolved_path=state["resolved_path"])
    result = kg_node(kg_state)
    state["kg_status"] = result.status
    if result.status != "success":
        state["error"] = result.error
    return state

def run_forecast(state: Phase3State) -> Phase3State:
    # Run forecast regardless of KG status (parallel capable, but sequential here)
    fc_state = ForecastState(resolved_path=state["resolved_path"])
    result = forecast_node(fc_state)
    state["forecast_status"] = result.status
    if result.status == "success":
        state["forecast_json"] = result.forecast_json
    else:
        state["error"] = result.error
    return state

def build_phase3_graph():
    workflow = StateGraph(Phase3State)
    
    workflow.add_node("knowledge_graph", run_kg)
    workflow.add_node("forecast", run_forecast)
    
    workflow.add_edge(START, "knowledge_graph")
    workflow.add_edge("knowledge_graph", "forecast")
    workflow.add_edge("forecast", END)
    
    return workflow.compile()

if __name__ == "__main__":
    from core.storage import CLEAN_DIR
    
    print("--- Starting Phase 3 Advanced Analytics & Graph ---")
    app = build_phase3_graph()
    
    # We will use the resolved dataset from Phase 2
    target_resolved_file = os.path.join(CLEAN_DIR, "mock_cnes_resolved.parquet")

    initial_state = Phase3State(
        resolved_path=target_resolved_file,
        kg_status="pending",
        forecast_status="pending",
        forecast_json="",
        error=""
    )
    
    final_state = app.invoke(initial_state)
    
    print("\n--- Phase 3 Execution Summary ---")
    print(f"KG Status: {final_state['kg_status']}")
    print(f"Forecast Status: {final_state['forecast_status']}")
    if final_state.get('error'):
        print(f"Error: {final_state['error']}")
    if final_state.get('forecast_json'):
        print("\nForecast Agent JSON Output (Next 3 Months):")
        print(final_state['forecast_json'])
