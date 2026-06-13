from typing import TypedDict, List, Dict, Optional
import os
from langgraph.graph import StateGraph, START, END

from agents.discovery_agent import discovery_node, DiscoveryState
from agents.ingestion_agent import ingest_node, IngestionState
from agents.cleaning_agent import clean_node, CleaningState
from agents.entity_resolution_agent import resolution_node, EntityResolutionState
from agents.feature_engineering_agent import feature_node, FeatureState

# Define the overall state for the LangGraph workflow
class PipelineState(TypedDict):
    query: str
    target_datasets: List[dict]
    raw_paths: Dict[str, str]
    clean_paths: Dict[str, str]
    resolved_path: str
    feature_path: str
    status: str
    error: str

def run_discovery(state: PipelineState) -> PipelineState:
    print("\n[Node 1: Discovery] Finding datasets...")
    ds_state = DiscoveryState(query=state["query"])
    result = discovery_node(ds_state)
    state["status"] = result.status
    if result.status == "success":
        state["target_datasets"] = result.datasets_found
    else:
        state["error"] = "Discovery failed"
    return state

def run_ingestion(state: PipelineState) -> PipelineState:
    print("\n[Node 2: Ingestion] Downloading files...")
    if not state.get("target_datasets"):
        state["status"] = "failed"
        state["error"] = "No datasets discovered"
        return state
        
    for ds in state["target_datasets"]:
        in_state = IngestionState(
            dataset_name=ds["name"],
            target_file=ds["filename"]
        )
        result = ingest_node(in_state)
        if result.status == "success":
            state["raw_paths"][ds["name"]] = result.raw_path
        else:
            state["status"] = "failed"
            state["error"] = f"Ingestion failed for {ds['name']}: {result.error}"
            return state
            
    state["status"] = "success"
    return state

def run_cleaning(state: PipelineState) -> PipelineState:
    print("\n[Node 3: Cleaning] Cleaning and converting files...")
    if not state.get("raw_paths"):
        state["status"] = "failed"
        state["error"] = "No raw files to clean"
        return state
        
    for ds_name, raw_path in state["raw_paths"].items():
        cl_state = CleaningState(
            dataset_name=ds_name,
            target_file=os.path.basename(raw_path),
            raw_path=raw_path
        )
        result = clean_node(cl_state)
        if result.status == "success":
            state["clean_paths"][ds_name] = result.clean_path
        else:
            state["status"] = "failed"
            state["error"] = f"Cleaning failed for {ds_name}: {result.error}"
            return state
            
    state["status"] = "success"
    return state

def run_resolution(state: PipelineState) -> PipelineState:
    print("\n[Node 4: Entity Resolution] Clustering hospital names and merging tables...")
    # Clean paths must contain cnes, sih, and ibge
    cnes_clean = state["clean_paths"].get("cnes")
    if not cnes_clean:
        state["status"] = "failed"
        state["error"] = "Missing clean CNES path"
        return state
        
    er_state = EntityResolutionState(
        clean_path=cnes_clean
    )
    result = resolution_node(er_state)
    state["status"] = result.status
    if result.status == "success":
        state["resolved_path"] = result.resolved_path
    else:
        state["error"] = f"Resolution failed: {result.error}"
    return state

def run_features(state: PipelineState) -> PipelineState:
    print("\n[Node 5: Feature Engineering] Calculating KPIs...")
    feat_state = FeatureState(
        resolved_path=state["resolved_path"]
    )
    result = feature_node(feat_state)
    state["status"] = result.status
    if result.status == "success":
        state["feature_path"] = result.feature_path
    else:
        state["error"] = f"Feature Engineering failed: {result.error}"
    return state

def build_graph():
    workflow = StateGraph(PipelineState)
    
    workflow.add_node("discovery", run_discovery)
    workflow.add_node("ingestion", run_ingestion)
    workflow.add_node("cleaning", run_cleaning)
    workflow.add_node("resolution", run_resolution)
    workflow.add_node("features", run_features)
    
    workflow.add_edge(START, "discovery")
    workflow.add_edge("discovery", "ingestion")
    workflow.add_edge("ingestion", "cleaning")
    workflow.add_edge("cleaning", "resolution")
    workflow.add_edge("resolution", "features")
    workflow.add_edge("features", END)
    
    return workflow.compile()

if __name__ == "__main__":
    print("--- Starting Brazilian Healthcare Intelligence OS Pipeline ---")
    app = build_graph()
    
    initial_state = PipelineState(
        query="Catarata e faturamento SUS no Acre",
        target_datasets=[],
        raw_paths={},
        clean_paths={},
        resolved_path="",
        feature_path="",
        status="pending",
        error=""
    )
    
    final_state = app.invoke(initial_state)
    
    print("\n--- Pipeline Execution Summary ---")
    print(f"Status: {final_state['status']}")
    if final_state['error']:
        print(f"Error: {final_state['error']}")
    else:
        print("\nDownloaded Raw Files:")
        for k, v in final_state['raw_paths'].items():
            print(f"  {k}: {v}")
        print("\nCleaned Parquet Files:")
        for k, v in final_state['clean_paths'].items():
            print(f"  {k}: {v}")
        print(f"\nResolved CNES: {final_state['resolved_path']}")
        print(f"Calculated KPIs: {final_state['feature_path']}")
        print("\nSuccess! Real public health data has been successfully integrated into DuckDB.")
