import pandas as pd
from rapidfuzz import process, fuzz
from pydantic import BaseModel
import os

class EntityResolutionState(BaseModel):
    clean_path: str
    resolved_path: str = ""
    status: str = "pending"
    error: str = ""

def resolution_node(state: EntityResolutionState) -> EntityResolutionState:
    print(f"Entity Resolution Agent: Processing {state.clean_path}")
    from core.storage import DuckDBStorage, CLEAN_DIR
    
    try:
        # Load the clean dataset
        df = pd.read_parquet(state.clean_path)
        
        if 'nome_fantasia' not in df.columns:
            print("Entity Resolution Agent: 'nome_fantasia' not found. Skipping.")
            state.resolved_path = state.clean_path
            state.status = "success"
            return state

        names = df['nome_fantasia'].unique().tolist()
        canonical_mapping = {}
        
        # Simple clustering using RapidFuzz
        # We iterate over unique names and group them if similarity > 80
        clusters = []
        for name in names:
            added = False
            for cluster in clusters:
                # Compare with the canonical (first) name of the cluster
                score = fuzz.token_sort_ratio(name, cluster[0])
                if score > 60:
                    cluster.append(name)
                    canonical_mapping[name] = cluster[0]
                    added = True
                    break
            if not added:
                clusters.append([name])
                canonical_mapping[name] = name

        print(f"Entity Resolution Agent: Found {len(clusters)} unique entities out of {len(names)} names.")
        for cluster in clusters:
            if len(cluster) > 1:
                print(f"  -> Resolved group: {cluster}")

        # Apply mapping
        df['canonical_name'] = df['nome_fantasia'].map(canonical_mapping)
        
        # Generate stable entity ID
        df['entity_id'] = df['canonical_name'].astype('category').cat.codes.astype(str)
        df['entity_id'] = "HOSP_" + df['entity_id'].str.zfill(5)

        # Save the resolved dataset back
        filename_without_ext = os.path.splitext(os.path.basename(state.clean_path))[0]
        resolved_filename = f"{filename_without_ext}_resolved.parquet"
        resolved_path = os.path.join(CLEAN_DIR, resolved_filename)
        
        df.to_parquet(resolved_path, index=False)
        print(f"Entity Resolution Agent: Saved resolved data to {resolved_path}")

        # Update in DuckDB
        db = DuckDBStorage()
        table_name = f"master_{filename_without_ext}"
        db.load_parquet(table_name, resolved_path)
        db.close()

        state.resolved_path = resolved_path
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Entity Resolution Agent: Error: {e}")
        
    return state
