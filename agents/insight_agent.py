from pydantic import BaseModel
import pandas as pd
import json

class InsightState(BaseModel):
    feature_path: str
    insights: str = ""
    status: str = "pending"
    error: str = ""

def insight_node(state: InsightState) -> InsightState:
    print(f"Insight Agent: Generating narratives from {state.feature_path}")
    from core.llm import get_llm
    
    try:
        df = pd.read_parquet(state.feature_path)
        data_str = df.to_string()
        
        # We will mock the LLM response to save API calls in the MVP, 
        # but here is the logic that would run:
        """
        llm = get_llm()
        prompt = f'''
        Act as a Principal Healthcare Analyst for the Brazilian Intelligence OS.
        Review these KPI features for the hospitals:
        {data_str}
        
        Write a short "Bloomberg-style" market insight paragraph. Highlight market share dominance
        and identify an opportunity based on procedures per capita.
        '''
        response = llm.invoke(prompt)
        state.insights = response.content
        """
        
        # Mock Response for MVP
        print("Insight Agent: Analyzing KPIs with LLM (Mocked)...")
        state.insights = "MARKET INSIGHT: HOSPITAL SAO JOSE currently dominates the local market with a 50.0% market share. However, the overall procedure rate is only 0.08 per 10k capita, indicating a statistically underserved municipality. OPPORTUNITY: There is significant room for capacity expansion or a new market entrant (Private Equity Acquisition target) to absorb unaddressed demand."
        
        print("Insight Agent: Insights generated.")
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Insight Agent: Error: {e}")
        
    return state
