from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from agents.discovery_agent import discovery_node, DiscoveryState
from agents.ingestion_agent import ingest_node, IngestionState
from agents.cleaning_agent import clean_node, CleaningState

# Define the overall state for the LangGraph workflow
class PipelineState(TypedDict):
    query: str
    target_dataset: Optional[dict]
    raw_path: str
    clean_path: str
    status: str
    error: str

# Node functions adapted for the pipeline state
def run_discovery(state: PipelineState) -> PipelineState:
    ds_state = DiscoveryState(query=state["query"])
    result = discovery_node(ds_state)
    state["status"] = result.status
    if result.status == "success" and result.datasets_found:
        state["target_dataset"] = result.datasets_found[0]
    return state

def run_ingestion(state: PipelineState) -> PipelineState:
    if not state.get("target_dataset"):
        state["status"] = "failed"
        state["error"] = "No dataset found"
        return state
        
    ds = state["target_dataset"]
    # We pass the filename we want to download
    in_state = IngestionState(
        dataset_name=ds["name"],
        target_file=ds["filename"]
    )
    result = ingest_node(in_state)
    state["status"] = result.status
    if result.status == "success":
        state["raw_path"] = result.raw_path
    else:
        state["error"] = result.error
    return state

def run_cleaning(state: PipelineState) -> PipelineState:
    if not state.get("raw_path"):
        state["status"] = "failed"
        state["error"] = "No raw path to clean"
        return state

    cl_state = CleaningState(
        dataset_name=state["target_dataset"]["name"],
        target_file=state["target_dataset"]["filename"],
        raw_path=state["raw_path"]
    )
    result = clean_node(cl_state)
    state["status"] = result.status
    if result.status == "success":
        state["clean_path"] = result.clean_path
    else:
        state["error"] = result.error
    return state

def build_graph():
    workflow = StateGraph(PipelineState)
    
    workflow.add_node("discovery", run_discovery)
    workflow.add_node("ingestion", run_ingestion)
    workflow.add_node("cleaning", run_cleaning)
    
    workflow.add_edge(START, "discovery")
    workflow.add_edge("discovery", "ingestion")
    workflow.add_edge("ingestion", "cleaning")
    workflow.add_edge("cleaning", END)
    
    return workflow.compile()

if __name__ == "__main__":
    print("--- Starting Brazilian Healthcare Intelligence OS Pipeline MVP ---")
    app = build_graph()
    
    initial_state = PipelineState(
        query="Latest CNES establishment types",
        target_dataset=None,
        raw_path="",
        clean_path="",
        status="pending",
        error=""
    )
    
    final_state = app.invoke(initial_state)
    
    print("\n--- Pipeline Execution Summary ---")
    print(f"Status: {final_state['status']}")
    if final_state['error']:
        print(f"Error: {final_state['error']}")
    if final_state.get('raw_path'):
        print(f"Raw File: {final_state['raw_path']}")
    if final_state.get('clean_path'):
        print(f"Cleaned Parquet: {final_state['clean_path']}")
