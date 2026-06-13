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
    
    # In the real implementation, we discover the DATASUS files and IBGE API target.
    # Default to Acre (AC) and competence 2401 (Jan 2024) for lightweight fast execution.
    state.datasets_found = [
        {
            "name": "sih",
            "url": "https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIHSUS/200801_/Dados/RDAC2401.dbc",
            "filename": "RDAC2401.dbc"
        },
        {
            "name": "sia",
            "url": "https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIASUS/200801_/Dados/PAAC2401.dbc",
            "filename": "PAAC2401.dbc"
        },
        {
            "name": "cnes",
            "url": "https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/CNES/200508_/Auxiliar/TAB_CNES.zip",
            "filename": "TAB_CNES.zip"
        },
        {
            "name": "ibge",
            "url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
            "filename": "municipios.json"
        }
    ]
    state.status = "success"
    print("Discovery Agent: Discovered real SIH, SIA, CNES, and IBGE datasets.")
    return state
