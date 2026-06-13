from pydantic import BaseModel
import pandas as pd
import os

class FeatureState(BaseModel):
    resolved_path: str
    feature_path: str = ""
    status: str = "pending"
    error: str = ""

def feature_node(state: FeatureState) -> FeatureState:
    print(f"Feature Engineering Agent: Generating KPIs from {state.resolved_path}")
    from core.storage import CLEAN_DIR, DuckDBStorage
    
    try:
        df = pd.read_parquet(state.resolved_path)
        
        # In a real scenario, we would join IBGE data (Enrichment Agent).
        # For MVP, we will simulate calculating "Capacity Index" and "Market Share"
        
        # Calculate volume per entity
        df_kpi = df.groupby(['canonical_name', 'entity_id']).size().reset_index(name='procedure_volume')
        
        total_volume = df_kpi['procedure_volume'].sum()
        
        # Feature Engineering
        df_kpi['market_share_pct'] = (df_kpi['procedure_volume'] / total_volume) * 100
        
        # Mocking an Enrichment join (IBGE Population)
        mock_population = 500000 
        df_kpi['procedures_per_10k_capita'] = (df_kpi['procedure_volume'] / mock_population) * 10000
        
        # Save Features
        filename_without_ext = os.path.splitext(os.path.basename(state.resolved_path))[0]
        feature_filename = f"{filename_without_ext}_features.parquet"
        feature_path = os.path.join(CLEAN_DIR, feature_filename)
        
        df_kpi.to_parquet(feature_path, index=False)
        print(f"Feature Engineering Agent: Calculated {len(df_kpi)} KPI records. Saved to {feature_path}")

        # Update in DuckDB
        db = DuckDBStorage()
        table_name = f"features_{filename_without_ext}"
        db.load_parquet(table_name, feature_path)
        db.close()

        state.feature_path = feature_path
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Feature Engineering Agent: Error: {e}")
        
    return state
