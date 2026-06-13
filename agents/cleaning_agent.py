from pydantic import BaseModel
import os
import pandas as pd
from dbfread import DBF

class CleaningState(BaseModel):
    dataset_name: str
    target_file: str
    raw_path: str
    clean_path: str = ""
    status: str = "pending"
    error: str = ""

def clean_node(state: CleaningState) -> CleaningState:
    print(f"Cleaning Agent: Processing {state.raw_path}")
    from core.storage import CLEAN_DIR, DuckDBStorage
    
    try:
        # Load raw data
        if state.raw_path.lower().endswith('.dbf'):
            # Convert DBF to DataFrame
            table = DBF(state.raw_path, load=True)
            df = pd.DataFrame(iter(table))
        elif state.raw_path.lower().endswith('.csv'):
            df = pd.read_csv(state.raw_path)
        else:
            raise ValueError(f"Unsupported file format: {state.raw_path}")

        print(f"Cleaning Agent: Loaded {len(df)} rows.")

        # Standardize Columns
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        # Standardize simple dates if they exist (CNES often uses YYYYMM in competentia)
        if 'competencia' in df.columns:
            df['competencia'] = df['competencia'].astype(str)

        # Save to Parquet
        filename_without_ext = os.path.splitext(os.path.basename(state.raw_path))[0]
        parquet_filename = f"{filename_without_ext}.parquet"
        parquet_path = os.path.join(CLEAN_DIR, parquet_filename)
        
        df.to_parquet(parquet_path, index=False)
        print(f"Cleaning Agent: Saved cleaned data to {parquet_path}")

        # Register in DuckDB
        db = DuckDBStorage()
        table_name = f"clean_{state.dataset_name}_{filename_without_ext}"
        db.load_parquet(table_name, parquet_path)
        db.close()

        state.clean_path = parquet_path
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Cleaning Agent: Error: {e}")
        
    return state
