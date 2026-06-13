from pydantic import BaseModel
import os
import json
from typing import Dict, Any

class QAState(BaseModel):
    question: str
    sql_query: str = ""
    query_result: list = []
    narrative: str = ""
    json_output: str = ""
    status: str = "pending"
    error: str = ""

def qa_node(state: QAState) -> QAState:
    print(f"QA Agent: Answering question: '{state.question}'")
    from core.storage import DuckDBStorage
    from core.llm import get_llm
    
    try:
        db = DuckDBStorage()
        
        # 1. Inspect Schema
        # In MVP we only have the master table, let's get its schema
        schema_df = db.execute("DESCRIBE master_mock_cnes")
        schema_str = schema_df.to_string()
        
        # 2. Generate SQL using LLM (Mocked for local MVP without API key)
        print("QA Agent: Sending schema to LLM (Mocked)")
        sql = "SELECT canonical_name, COUNT(*) as count FROM master_mock_cnes GROUP BY canonical_name"
        state.sql_query = sql
        print(f"QA Agent: Generated SQL -> {sql}")
        
        # 3. Execute SQL
        result_df = db.execute(sql)
        state.query_result = result_df.to_dict(orient="records")
        print(f"QA Agent: Query executed, found {len(result_df)} rows.")
        
        # 4. Generate Narrative and JSON using LLM (Mocked)
        state.narrative = f"Existem {len(result_df)} hospitais distintos identificados no banco de dados. São eles: " + ", ".join(result_df['canonical_name'].tolist())
        
        # Create JSON output
        output_dict = {
            "question": state.question,
            "sql_executed": state.sql_query,
            "narrative": state.narrative,
            "data": state.query_result
        }
        state.json_output = json.dumps(output_dict, indent=2)
        state.status = "success"
        
        db.close()
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"QA Agent: Error: {e}")
        
    return state
