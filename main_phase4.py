import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from agents.feature_engineering_agent import feature_node, FeatureState
from agents.insight_agent import insight_node, InsightState

class Phase4State(TypedDict):
    resolved_path: str
    feature_path: str
    feature_status: str
    insights: str
    insight_status: str
    error: str

def run_features(state: Phase4State) -> Phase4State:
    feat_state = FeatureState(resolved_path=state["resolved_path"])
    result = feature_node(feat_state)
    state["feature_status"] = result.status
    if result.status == "success":
        state["feature_path"] = result.feature_path
    else:
        state["error"] = result.error
    return state

def run_insights(state: Phase4State) -> Phase4State:
    if state["feature_status"] == "failed":
        return state
        
    ins_state = InsightState(feature_path=state["feature_path"])
    result = insight_node(ins_state)
    state["insight_status"] = result.status
    if result.status == "success":
        state["insights"] = result.insights
    else:
        state["error"] = result.error
    return state

def build_phase4_graph():
    workflow = StateGraph(Phase4State)
    
    workflow.add_node("feature_engineering", run_features)
    workflow.add_node("insight_generation", run_insights)
    
    workflow.add_edge(START, "feature_engineering")
    workflow.add_edge("feature_engineering", "insight_generation")
    workflow.add_edge("insight_generation", END)
    
    return workflow.compile()

if __name__ == "__main__":
    from core.storage import CLEAN_DIR
    
    print("--- Starting Phase 4 Advanced Insights (Final) ---")
    app = build_phase4_graph()
    
    target_resolved_file = os.path.join(CLEAN_DIR, "mock_cnes_resolved.parquet")

    initial_state = Phase4State(
        resolved_path=target_resolved_file,
        feature_path="",
        feature_status="pending",
        insights="",
        insight_status="pending",
        error=""
    )
    
    final_state = app.invoke(initial_state)
    
    print("\n--- Phase 4 Execution Summary ---")
    print(f"Feature Engineering Status: {final_state['feature_status']}")
    print(f"Insight Generation Status: {final_state['insight_status']}")
    if final_state.get('error'):
        print(f"Error: {final_state['error']}")
    if final_state.get('insights'):
        print("\n=== BLOOMBERG HEALTHCARE TERMINAL INSIGHT ===")
        print(final_state['insights'])
        print("=============================================")
