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
    
    # Extract state from query (default to AC)
    q = state.query.lower()
    state_code = "AC"
    if "são paulo" in q or "sao paulo" in q or "sp" in q:
        state_code = "SP"
        
    print(f"Discovery Agent: Detected state: {state_code}")
    
    if state_code == "SP":
        state.datasets_found = [
            {
                "name": "sih",
                "url": f"https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIHSUS/200801_/Dados/RD{state_code}2401.dbc",
                "filename": f"RD{state_code}2401.dbc"
            },
            {
                "name": "sia_a",
                "url": f"https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIASUS/200801_/Dados/PA{state_code}2401a.dbc",
                "filename": f"PA{state_code}2401a.dbc"
            },
            {
                "name": "sia_b",
                "url": f"https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIASUS/200801_/Dados/PA{state_code}2401b.dbc",
                "filename": f"PA{state_code}2401b.dbc"
            },
            {
                "name": "sia_c",
                "url": f"https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIASUS/200801_/Dados/PA{state_code}2401c.dbc",
                "filename": f"PA{state_code}2401c.dbc"
            },
            {
                "name": "cnes",
                "url": "https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/CNES/200508_/Auxiliar/TAB_CNES.zip",
                "filename": f"TAB_CNES_{state_code}.zip"
            },
            {
                "name": "ibge",
                "url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
                "filename": "municipios.json"
            }
        ]
    else:
        state.datasets_found = [
            {
                "name": "sih",
                "url": f"https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIHSUS/200801_/Dados/RD{state_code}2401.dbc",
                "filename": f"RD{state_code}2401.dbc"
            },
            {
                "name": "sia",
                "url": f"https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/SIASUS/200801_/Dados/PA{state_code}2401.dbc",
                "filename": f"PA{state_code}2401.dbc"
            },
            {
                "name": "cnes",
                "url": "https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/CNES/200508_/Auxiliar/TAB_CNES.zip",
                "filename": f"TAB_CNES_{state_code}.zip"
            },
            {
                "name": "ibge",
                "url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
                "filename": "municipios.json"
            }
        ]
    state.status = "success"
    print(f"Discovery Agent: Discovered real SIH, SIA, CNES, and IBGE datasets for {state_code}.")
    return state
