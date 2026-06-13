from pydantic import BaseModel
import pandas as pd
import os

class FeatureState(BaseModel):
    resolved_path: str
    feature_path: str = ""
    status: str = "pending"
    error: str = ""

def feature_node(state: FeatureState) -> FeatureState:
    print("Feature Engineering Agent: Generating KPIs from master_healthcare in DuckDB...")
    from core.storage import CLEAN_DIR, DuckDBStorage
    
    os.makedirs(CLEAN_DIR, exist_ok=True)
    
    try:
        db = DuckDBStorage()
        
        # Calculate KPIs for cataract surgery (code starting with 040505)
        kpi_query = """
        SELECT 
          hospital_nome,
          cnes,
          hospital_uf,
          COUNT(*) AS procedure_volume,
          SUM(valor_total) AS total_revenue,
          ROUND(AVG(valor_total), 2) AS average_cost,
          ROUND(AVG(dias_permanencia), 1) AS average_stay_days
        FROM master_healthcare
        WHERE procedimento_codigo LIKE '040505%'
        GROUP BY hospital_nome, cnes, hospital_uf
        """
        df_kpi = db.execute(kpi_query)
        
        if df_kpi.empty:
            print("Feature Engineering Agent: No cataract surgeries found. Calculating general KPIs.")
            # Fallback to general if no cataract surgeries (e.g. general stats)
            kpi_query_fallback = """
            SELECT 
              hospital_nome,
              cnes,
              hospital_uf,
              COUNT(*) AS procedure_volume,
              SUM(valor_total) AS total_revenue,
              ROUND(AVG(valor_total), 2) AS average_cost,
              ROUND(AVG(dias_permanencia), 1) AS average_stay_days
            FROM master_healthcare
            GROUP BY hospital_nome, cnes, hospital_uf
            """
            df_kpi = db.execute(kpi_query_fallback)
            
        total_volume = df_kpi['procedure_volume'].sum()
        total_rev = df_kpi['total_revenue'].sum()
        
        # Calculate market share
        df_kpi['market_share_vol_pct'] = round((df_kpi['procedure_volume'] / total_volume) * 100, 2) if total_volume > 0 else 0.0
        df_kpi['market_share_rev_pct'] = round((df_kpi['total_revenue'] / total_rev) * 100, 2) if total_rev > 0 else 0.0
        
        # Save features Parquet
        feature_path = os.path.join(CLEAN_DIR, "features_healthcare.parquet")
        df_kpi.to_parquet(feature_path, index=False)
        print(f"Feature Engineering Agent: Saved {len(df_kpi)} records to {feature_path}")
        
        # Load features into DuckDB
        db.load_parquet("features_healthcare", feature_path)
        db.close()
        
        state.feature_path = feature_path
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Feature Engineering Agent: Error: {e}")
        
    return state
