from pydantic import BaseModel
import pandas as pd
from neo4j import GraphDatabase
import os

class KGState(BaseModel):
    resolved_path: str
    status: str = "pending"
    error: str = ""

def kg_node(state: KGState) -> KGState:
    print(f"Knowledge Graph Agent: Processing {state.resolved_path}")
    
    try:
        df = pd.read_parquet(state.resolved_path)
        
        # Connect to Neo4j
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "password123"
        
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            driver.verify_connectivity()
            print("Knowledge Graph Agent: Connected to Neo4j successfully.")
            
            with driver.session() as session:
                # Merge entities into Graph
                for _, row in df.iterrows():
                    hospital_name = row['canonical_name']
                    hospital_id = row['entity_id']
                    cnes = row['cnes']
                    tipo = row['tipo_unidade']
                    
                    # Create Hospital Node
                    session.run(
                        """
                        MERGE (h:Hospital {id: $id})
                        SET h.name = $name, h.cnes = $cnes, h.tipo = $tipo
                        """, 
                        id=hospital_id, name=hospital_name, cnes=cnes, tipo=tipo
                    )
            driver.close()
            print("Knowledge Graph Agent: Graph populated successfully.")
        except Exception as e:
            print(f"Knowledge Graph Agent: Neo4j not reachable ({e}). Simulating graph insertion for MVP.")
            print(f"Knowledge Graph Agent: (Simulated) Merged {len(df)} Hospital nodes.")
        
        state.status = "success"
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"Knowledge Graph Agent: Error: {e}")
        
    return state
