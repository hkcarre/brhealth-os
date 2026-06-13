import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional

from agents.entity_resolution_agent import resolution_node, EntityResolutionState
from agents.qa_agent import qa_node, QAState

class Phase2State(TypedDict):
    clean_path: str
    question: str
    resolved_path: str
    json_output: str
    status: str
    error: str

def run_resolution(state: Phase2State) -> Phase2State:
    er_state = EntityResolutionState(clean_path=state["clean_path"])
    result = resolution_node(er_state)
    state["status"] = result.status
    if result.status == "success":
        state["resolved_path"] = result.resolved_path
    else:
        state["error"] = result.error
    return state

def run_qa(state: Phase2State) -> Phase2State:
    if state["status"] == "failed":
        return state
        
    qa_state = QAState(question=state["question"])
    result = qa_node(qa_state)
    state["status"] = result.status
    if result.status == "success":
        state["json_output"] = result.json_output
    else:
        state["error"] = result.error
    return state

def build_phase2_graph():
    workflow = StateGraph(Phase2State)
    
    workflow.add_node("entity_resolution", run_resolution)
    workflow.add_node("qa", run_qa)
    
    workflow.add_edge(START, "entity_resolution")
    workflow.add_edge("entity_resolution", "qa")
    workflow.add_edge("qa", END)
    
    return workflow.compile()

if __name__ == "__main__":
    from core.storage import CLEAN_DIR
    
    print("--- Starting Phase 2 Intelligence & Querying ---")
    app = build_phase2_graph()
    
    # We will use the clean mock dataset from Phase 1
    # We generated it as mock_cnes.parquet
    target_clean_file = os.path.join(CLEAN_DIR, "mock_cnes.parquet")
    
    # Wait, in Phase 1 we updated the mock data but didn't re-run main.py.
    # Let's just run main.py's ingestion and cleaning first manually, 
    # or just assume the file exists and has 4 rows now? 
    # Actually, we should just run it. We'll run it in the terminal.

    initial_state = Phase2State(
        clean_path=target_clean_file,
        question="How many distinct hospitals are there, and what are their names?",
        resolved_path="",
        json_output="",
        status="pending",
        error=""
    )
    
    final_state = app.invoke(initial_state)
    
    print("\n--- Phase 2 Execution Summary ---")
    print(f"Status: {final_state['status']}")
    if final_state.get('error'):
        print(f"Error: {final_state['error']}")
    if final_state.get('json_output'):
        print("\nQA Agent JSON Output:")
        print(final_state['json_output'])
