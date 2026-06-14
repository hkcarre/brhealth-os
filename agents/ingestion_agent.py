import ftplib
import os
from pydantic import BaseModel, Field

class IngestionState(BaseModel):
    dataset_name: str
    target_file: str
    status: str = "pending"
    raw_path: str = ""
    error: str = ""

import urllib.request
import zipfile
import requests
import json

def ingest_node(state: IngestionState) -> IngestionState:
    print(f"Ingestion Agent: Starting ingestion for dataset: {state.dataset_name} ({state.target_file})")
    from core.storage import RAW_DIR
    
    os.makedirs(RAW_DIR, exist_ok=True)
    local_filepath = os.path.join(RAW_DIR, state.target_file)
    
    try:
        if state.dataset_name == "sih":
            url = f"https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIHSUS/200801_/Dados/{state.target_file}"
            print(f"Ingestion Agent: Downloading SIH file from mirror: {url}")
            urllib.request.urlretrieve(url, local_filepath)
            state.raw_path = local_filepath
            state.status = "success"
            print(f"Ingestion Agent: Successfully downloaded SIH file to {local_filepath}")
            
        elif state.dataset_name.startswith("sia"):
            url = f"https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIASUS/200801_/Dados/{state.target_file}"
            print(f"Ingestion Agent: Downloading SIA file from mirror: {url}")
            urllib.request.urlretrieve(url, local_filepath)
            state.raw_path = local_filepath
            state.status = "success"
            print(f"Ingestion Agent: Successfully downloaded SIA file to {local_filepath}")
            
        elif state.dataset_name == "cnes":
            # Extract the state code from target_file (e.g. TAB_CNES_SP.zip -> SP)
            state_code = state.target_file.replace("TAB_CNES_", "").replace(".zip", "")
            print(f"Ingestion Agent: Mapped state code for CNES: {state_code}")
            
            zip_url = "https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/CNES/200508_/Auxiliar/TAB_CNES.zip"
            zip_filepath = os.path.join(RAW_DIR, "TAB_CNES.zip") # We keep the general name so we reuse the 35MB download!
            
            if not os.path.exists(zip_filepath):
                print(f"Ingestion Agent: Downloading CNES Aux zip: {zip_url}")
                urllib.request.urlretrieve(zip_url, zip_filepath)
            else:
                print("Ingestion Agent: TAB_CNES.zip already exists locally.")
                
            # Extract CADGER{state_code}.dbf to RAW_DIR
            target_dbf = f"DBF/CADGER{state_code}.dbf"
            extracted_path = os.path.join(RAW_DIR, f"CADGER{state_code}.dbf")
            print(f"Ingestion Agent: Extracting {target_dbf} from ZIP to {extracted_path}...")
            
            with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                zip_ref.extract(target_dbf, RAW_DIR)
                # Move from RAW_DIR/DBF/CADGER{state_code}.dbf to RAW_DIR/CADGER{state_code}.dbf
                os.replace(os.path.join(RAW_DIR, target_dbf), extracted_path)
                # Clean up empty DBF folder if needed
                try:
                    os.rmdir(os.path.join(RAW_DIR, "DBF"))
                except Exception:
                    pass
                    
            state.raw_path = extracted_path
            state.status = "success"
            print(f"Ingestion Agent: Successfully extracted CADGER DBF to {extracted_path}")
            
        elif state.dataset_name == "ibge":
            url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
            print(f"Ingestion Agent: Fetching IBGE municipalities: {url}")
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            with open(local_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            state.raw_path = local_filepath
            state.status = "success"
            print(f"Ingestion Agent: Successfully downloaded IBGE data to {local_filepath}")
            
        else:
            raise ValueError(f"Unknown dataset name: {state.dataset_name}")
            
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Ingestion Agent: Ingestion failed with error: {e}")
        
    return state
