import os
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class DiscoveryState(BaseModel):
    query: str
    datasets_found: list = []
    status: str = "pending"

def get_llm():
    """Returns an instance of Gemini Pro."""
    # Note: Requires GOOGLE_API_KEY environment variable to be set.
    api_key = os.getenv("GOOGLE_API_KEY", "dummy-key-for-local-test")
    return ChatGoogleGenerativeAI(model="gemini-3.1-pro", google_api_key=api_key)

def discovery_node(state: DiscoveryState) -> DiscoveryState:
    print(f"Discovery Agent: Searching for datasets matching '{state.query}'")
    
    # In a full implementation, this agent would crawl DATASUS/gov.br portals.
    # For MVP, we simulate discovering the CNES ST file on FTP.
    print("Discovery Agent: Found matching dataset on DATASUS FTP.")
    
    state.datasets_found = [
        {
            "name": "CNES_Subtipos",
            "url": "ftp.datasus.gov.br",
            "path": "/dissemin/publicos/CNES/200508_/Dados/ST.dbf", # Simulated DBF
            "filename": "ST2401.dbf" # Fictional filename for 2024 month 01
        }
    ]
    state.status = "success"
    return state
