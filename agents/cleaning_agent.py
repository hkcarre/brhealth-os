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
    print(f"Cleaning Agent: Processing {state.raw_path} for dataset {state.dataset_name}")
    from core.storage import CLEAN_DIR, DuckDBStorage
    from dbctodbf import DBCDecompress
    import json
    
    os.makedirs(CLEAN_DIR, exist_ok=True)
    
    try:
        if state.dataset_name == "sih":
            # 1. Decompress DBC to DBF
            dbf_path = state.raw_path.replace(".dbc", ".dbf")
            if not os.path.exists(dbf_path):
                print(f"Cleaning Agent: Decompressing {state.raw_path} -> {dbf_path}")
                decompressor = DBCDecompress()
                decompressor.decompressFile(state.raw_path, dbf_path)
            else:
                print(f"Cleaning Agent: DBF already exists: {dbf_path}")
                
            # 2. Read DBF
            print(f"Cleaning Agent: Reading DBF {dbf_path}")
            table = DBF(dbf_path, encoding="iso-8859-1")
            df = pd.DataFrame(iter(table))
            
            # 3. Standardize column names to lowercase
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # 4. Filter and select critical columns
            keep_cols = ['cnes', 'proc_rea', 'val_tot', 'munic_res', 'dias_perm', 'idade', 'sexo', 'dt_inter', 'dt_saida', 'competen']
            # Fallback if some column is missing (e.g. competen can be ANO_CMPT/MES_CMPT, let's check)
            for col in keep_cols:
                if col not in df.columns:
                    if col == 'competen' and 'ano_cmpt' in df.columns:
                        df['competen'] = df['ano_cmpt'].astype(str) + df['mes_cmpt'].astype(str).str.zfill(2)
                    else:
                        df[col] = None
                        
            df = df[keep_cols]
            
            # Clean types
            df['val_tot'] = pd.to_numeric(df['val_tot'], errors='coerce').fillna(0.0)
            df['dias_perm'] = pd.to_numeric(df['dias_perm'], errors='coerce').fillna(0).astype(int)
            df['idade'] = pd.to_numeric(df['idade'], errors='coerce').fillna(0).astype(int)
            df['cnes'] = df['cnes'].astype(str).str.strip().str.zfill(7)
            df['proc_rea'] = df['proc_rea'].astype(str).str.strip().str.zfill(10)
            df['munic_res'] = df['munic_res'].astype(str).str.strip().str.zfill(6)
            
        elif state.dataset_name == "sia":
            # 1. Decompress DBC to DBF
            dbf_path = state.raw_path.replace(".dbc", ".dbf")
            if not os.path.exists(dbf_path):
                print(f"Cleaning Agent: Decompressing {state.raw_path} -> {dbf_path}")
                decompressor = DBCDecompress()
                decompressor.decompressFile(state.raw_path, dbf_path)
            else:
                print(f"Cleaning Agent: DBF already exists: {dbf_path}")
                
            # 2. Read DBF
            print(f"Cleaning Agent: Reading DBF {dbf_path}")
            table = DBF(dbf_path, encoding="iso-8859-1")
            df = pd.DataFrame(iter(table))
            
            # 3. Standardize column names to lowercase
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # 4. Map columns Pa_coduni -> cnes, pa_proc_id -> proc_rea, etc.
            df = df.rename(columns={
                'pa_coduni': 'cnes',
                'pa_proc_id': 'proc_rea',
                'pa_valapr': 'val_tot',
                'pa_munpcn': 'munic_res',
                'pa_idade': 'idade',
                'pa_sexo': 'sexo',
                'pa_cmp': 'competen'
            })
            
            # Fill missing required columns
            df['dias_perm'] = 0
            df['dt_inter'] = df['competen'].astype(str) + "01"
            df['dt_saida'] = df['competen'].astype(str) + "01"
            
            # Select final standardized columns
            keep_cols = ['cnes', 'proc_rea', 'val_tot', 'munic_res', 'dias_perm', 'idade', 'sexo', 'dt_inter', 'dt_saida', 'competen']
            for col in keep_cols:
                if col not in df.columns:
                    df[col] = None
            df = df[keep_cols]
            
            # Standardize types
            df['val_tot'] = pd.to_numeric(df['val_tot'], errors='coerce').fillna(0.0)
            df['dias_perm'] = 0
            df['idade'] = pd.to_numeric(df['idade'], errors='coerce').fillna(0).astype(int)
            df['cnes'] = df['cnes'].astype(str).str.strip().str.zfill(7)
            df['proc_rea'] = df['proc_rea'].astype(str).str.strip().str.zfill(10)
            df['munic_res'] = df['munic_res'].astype(str).str.strip().str.zfill(6)

        elif state.dataset_name == "cnes":
            # Read the extracted CADGER DBF file
            print(f"Cleaning Agent: Reading CNES DBF {state.raw_path}")
            table = DBF(state.raw_path, encoding="iso-8859-1")
            df = pd.DataFrame(iter(table))
            
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Select columns
            keep_cols = ['cnes', 'fantasia', 'raz_soci', 'codufmun']
            for col in keep_cols:
                if col not in df.columns:
                    df[col] = ""
            df = df[keep_cols]
            
            # Standardize CNES code and name
            df['cnes'] = df['cnes'].astype(str).str.strip().str.zfill(7)
            df['fantasia'] = df['fantasia'].astype(str).str.strip().str.upper()
            df['raz_soci'] = df['raz_soci'].astype(str).str.strip().str.upper()
            df['codufmun'] = df['codufmun'].astype(str).str.strip().str.zfill(6)
            
        elif state.dataset_name == "ibge":
            # Read JSON file
            print(f"Cleaning Agent: Reading IBGE JSON {state.raw_path}")
            with open(state.raw_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            UF_MAP = {
                '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
                '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL',
                '28': 'SE', '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP', '41': 'PR',
                '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
            }
                
            records = []
            for item in data:
                municipio_id = str(item['id'])[:6] # Truncate 7-digit to 6-digit for DATASUS
                nome = item['nome'].strip().upper()
                
                # Safe navigation
                uf = None
                micro = item.get('microrregiao')
                if micro:
                    meso = micro.get('mesorregiao')
                    if meso:
                        uf_obj = meso.get('UF')
                        if uf_obj:
                            uf = uf_obj.get('sigla')
                            
                if not uf:
                    state_code = str(item['id'])[:2]
                    uf = UF_MAP.get(state_code, "UNKNOWN")
                    
                records.append({
                    'municipio_id': municipio_id,
                    'nome': nome,
                    'uf': uf.strip().upper()
                })
                
            df = pd.DataFrame(records)
            
        else:
            raise ValueError(f"Unknown dataset name: {state.dataset_name}")
            
        # Save to Parquet
        parquet_filename = f"clean_{state.dataset_name}.parquet"
        parquet_path = os.path.join(CLEAN_DIR, parquet_filename)
        df.to_parquet(parquet_path, index=False)
        print(f"Cleaning Agent: Saved cleaned data to {parquet_path}")
        
        # Load to DuckDB
        db = DuckDBStorage()
        table_name = f"clean_{state.dataset_name}"
        db.load_parquet(table_name, parquet_path)
        db.close()
        
        state.clean_path = parquet_path
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Cleaning Agent: Error during clean: {e}")
        
    return state
