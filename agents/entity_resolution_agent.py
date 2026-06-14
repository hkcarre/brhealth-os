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
    print(f"Entity Resolution Agent: Starting resolution for clean CNES data")
    from core.storage import DuckDBStorage, CLEAN_DIR
    
    try:
        # 1. Load clean CNES Parquet
        cnes_path = os.path.join(CLEAN_DIR, "clean_cnes.parquet")
        if not os.path.exists(cnes_path):
            raise FileNotFoundError(f"Clean CNES parquet not found at {cnes_path}")
            
        df = pd.read_parquet(cnes_path)
        
        # Optimize: Filter CNES records to only those present in clean_sih or clean_sia
        print("Entity Resolution Agent: Filtering CNES to active facilities in clinical data...")
        db = DuckDBStorage()
        try:
            active_cnes = db.execute("""
                SELECT cnes FROM clean_sih
                UNION
                SELECT cnes FROM clean_sia
            """)['cnes'].dropna().unique().tolist()
            df = df[df['cnes'].isin(active_cnes)].copy()
            print(f"Entity Resolution Agent: Filtered CNES records from {len(active_cnes)} active facilities.")
        except Exception as ex:
            print(f"Entity Resolution Agent: Warning - could not filter active CNES: {ex}")
        db.close()
        
        if 'fantasia' not in df.columns:
            raise KeyError("Column 'fantasia' not found in CNES data.")
            
        # Get unique facility names (non-empty)
        names = df['fantasia'].dropna().unique().tolist()
        names = [n for n in names if n.strip()]
        canonical_mapping = {}
        
        # 2. Fuzzy clustering using RapidFuzz (Token Sort Ratio)
        clusters = []
        for name in names:
            added = False
            for cluster in clusters:
                score = fuzz.token_sort_ratio(name, cluster[0])
                if score > 80: # Highly similar names (e.g. HOSP SAO JOSE vs HOSP SAO JOSE LTDA)
                    cluster.append(name)
                    canonical_mapping[name] = cluster[0]
                    added = True
                    break
            if not added:
                clusters.append([name])
                canonical_mapping[name] = name
                
        print(f"Entity Resolution Agent: Grouped {len(names)} unique names into {len(clusters)} canonical entities.")
        
        # Apply mapping
        df['canonical_name'] = df['fantasia'].map(canonical_mapping).fillna(df['fantasia'])
        
        # Generate stable entity ID
        df['entity_id'] = df['canonical_name'].astype('category').cat.codes.astype(str)
        df['entity_id'] = "HOSP_" + df['entity_id'].str.zfill(5)
        
        # Save resolved CNES Parquet
        resolved_path = os.path.join(CLEAN_DIR, "clean_cnes_resolved.parquet")
        df.to_parquet(resolved_path, index=False)
        print(f"Entity Resolution Agent: Saved resolved CNES to {resolved_path}")
        
        # Load into DuckDB
        db = DuckDBStorage()
        db.load_parquet("clean_cnes_resolved", resolved_path)
        
        # 3. Create the master unified table master_healthcare in DuckDB
        print("Entity Resolution Agent: Creating master_healthcare table in DuckDB...")
        
        # Check which clean tables exist in DuckDB
        tables = db.execute("PRAGMA show_tables")['name'].tolist()
        sia_selects = []
        if 'clean_sia' in tables:
            sia_selects.append("SELECT cnes, proc_rea, val_tot, munic_res, dias_perm, idade, sexo, dt_inter, dt_saida, competen FROM clean_sia")
        for char in ['a', 'b', 'c', 'd']:
            tbl = f"clean_sia_{char}"
            if tbl in tables:
                sia_selects.append(f"SELECT cnes, proc_rea, val_tot, munic_res, dias_perm, idade, sexo, dt_inter, dt_saida, competen FROM {tbl}")
                
        sia_union_query = " UNION ALL ".join(sia_selects)
        print(f"Entity Resolution Agent: Mapped {len(sia_selects)} clean SIA tables for union.")
        
        join_query = f"""
        CREATE OR REPLACE TABLE master_healthcare AS
        WITH clinical_union AS (
            SELECT cnes, proc_rea, val_tot, munic_res, dias_perm, idade, sexo, dt_inter, dt_saida, competen FROM clean_sih
            UNION ALL
            {sia_union_query}
        )
        SELECT 
          s.cnes,
          c.canonical_name AS hospital_nome,
          c.entity_id AS hospital_id,
          c.codufmun AS hospital_municipio_id,
          m_h.nome AS hospital_municipio_nome,
          m_h.uf AS hospital_uf,
          s.proc_rea AS procedimento_codigo,
          s.val_tot AS valor_total,
          s.dt_inter AS data_internacao,
          s.dt_saida AS data_saida,
          s.dias_perm AS dias_permanencia,
          s.idade AS paciente_idade,
          s.sexo AS paciente_sexo,
          s.munic_res AS paciente_municipio_id,
          m_p.nome AS paciente_municipio_nome,
          m_p.uf AS paciente_uf,
          s.competen AS competencia
        FROM clinical_union s
        LEFT JOIN clean_cnes_resolved c ON s.cnes = c.cnes
        LEFT JOIN clean_ibge m_h ON LEFT(c.codufmun, 6) = m_h.municipio_id
        LEFT JOIN clean_ibge m_p ON s.munic_res = m_p.municipio_id
        """
        db.execute(join_query)
        
        # Verify join count
        count_df = db.execute("SELECT COUNT(*) as cnt FROM master_healthcare")
        total_rows = count_df.iloc[0]['cnt']
        print(f"Entity Resolution Agent: master_healthcare created successfully with {total_rows} rows.")
        
        db.close()
        
        state.resolved_path = resolved_path
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Entity Resolution Agent: Error: {e}")
        
    return state
