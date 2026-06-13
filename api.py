from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os

from agents.qa_agent import qa_node, QAState

app = FastAPI(title="Brazilian Healthcare Intelligence OS API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql_executed: str
    narrative: str
    data: list

@app.get("/api")
def read_root():
    return {"status": "Healthcare Intelligence OS is running."}

@app.post("/api/ask", response_model=QueryResponse)
def ask_question(req: QueryRequest):
    state = QAState(question=req.question)
    result = qa_node(state)
    
    if result.status == "failed":
        raise HTTPException(status_code=500, detail=result.error)
        
    try:
        json_data = json.loads(result.json_output)
        return QueryResponse(
            sql_executed=json_data.get("sql_executed", ""),
            narrative=json_data.get("narrative", ""),
            data=json_data.get("data", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to parse agent response")

# Serve the frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
os.makedirs(frontend_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

# To run: uvicorn api:app --reload
