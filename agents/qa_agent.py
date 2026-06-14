from pydantic import BaseModel
import os
import json
from typing import Dict, Any

class QAState(BaseModel):
    question: str
    state: str = "AC"
    sql_query: str = ""
    query_result: list = []
    narrative: str = ""
    json_output: str = ""
    status: str = "pending"
    error: str = ""

def qa_node(state: QAState) -> QAState:
    print(f"QA Agent: Answering question: '{state.question}'")
    from core.storage import DuckDBStorage
    import os
    
    try:
        db = DuckDBStorage()
        
        # 1. Check schemas
        has_master = False
        try:
            db.execute("DESCRIBE master_healthcare")
            has_master = True
        except Exception:
            pass
            
        if not has_master:
            raise Exception("Tabela 'master_healthcare' nao encontrada no DuckDB. Execute o pipeline primeiro.")
            
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if api_key and api_key != "dummy-key" and api_key.strip():
            # LLM Dynamic text-to-SQL
            print("QA Agent: Generating SQL using LLM...")
            from core.llm import get_llm
            llm = get_llm()
            
            prompt = f"""
            Você é o assistente do Bloomberg Terminal de Saúde do Brasil.
            Temos as seguintes tabelas no DuckDB:
            
            1. `master_healthcare` (internações e cadastros consolidados):
               - cnes (código CNES do hospital)
               - hospital_nome (nome do estabelecimento)
               - hospital_municipio_nome (cidade do hospital)
               - hospital_uf (estado do hospital)
               - procedimento_codigo (código do procedimento, ex: '0405050372' para catarata)
               - valor_total (valor pago em R$)
               - data_internacao (YYYYMMDD)
               - data_saida (YYYYMMDD)
               - dias_permanencia (quantidade de dias)
               - paciente_idade (idade do paciente)
               - paciente_sexo (1=masculino, 2=feminino, 3=ignorado)
               - paciente_municipio_nome (cidade de residência)
               - paciente_uf (estado do paciente)
               
            2. `features_healthcare` (KPIs calculados):
               - hospital_nome, cnes, hospital_uf
               - procedure_volume, total_revenue, average_cost, average_stay_days
               - market_share_vol_pct, market_share_rev_pct
               
            Pergunta do usuário: "{state.question}"
            Estado ativo selecionado no painel: "{state.state}"
            
            Gere uma query SQL válida para DuckDB para responder à pergunta. 
            Filtre a query para o estado selecionado "{state.state}" (usando "hospital_uf = '{state.state}'" ou "paciente_uf = '{state.state}'" conforme apropriado) para retornar apenas os dados relativos a esse estado, a menos que a pergunta peça explicitamente outro local.
            Retorne APENAS um JSON no seguinte formato:
            {{
                "sql_executed": "SUA QUERY SQL AQUI",
                "narrative": "Uma explicação em português sucinta e profissional sobre os resultados obtidos (descreva o faturamento, volumes, etc. para o estado {state.state})"
            }}
            Não inclua blocos de código ```json ou textos explicativos antes ou depois.
            """
            response = llm.invoke(prompt)
            output_text = response.content.strip()
            # Parse response
            # Cleanup markdown block markers if LLM generates them despite instructions
            if output_text.startswith("```"):
                output_text = "\n".join(output_text.split("\n")[1:-1])
            output_dict = json.loads(output_text)
            sql = output_dict["sql_executed"]
            state.sql_query = sql
            
            # Execute SQL
            df = db.execute(sql)
            state.query_result = df.to_dict(orient="records")
            state.narrative = output_dict["narrative"]
            
        else:
            # Offline Fallback Compiler (Rule-based)
            print(f"QA Agent: Google API Key not configured. Using Offline Fallback Compiler for state {state.state}...")
            q = state.question.lower().strip()
            
            state_name_map = {"AC": "Acre", "SP": "São Paulo"}
            state_name = state_name_map.get(state.state, state.state)
            
            # Rule 1: Distict hospitals
            if "quantos hospitais" in q or "hospitais distintos" in q or "lista de hospitais" in q:
                sql = f"SELECT hospital_nome as Hospital, cnes as CNES, hospital_municipio_nome as Cidade, hospital_uf as UF FROM master_healthcare WHERE hospital_uf = '{state.state}' GROUP BY ALL ORDER BY hospital_nome"
                narrative_builder = lambda df: f"Foram identificados {len(df)} estabelecimentos de saúde distintos no banco de dados de {state_name}."
                
            # Rule 2: Cataract volume by hospital
            elif "volume" in q or "cirurgias" in q or "catarata" in q or "quantidade" in q:
                sql = f"""
                SELECT 
                  hospital_nome as Hospital, 
                  COUNT(*) as "Volume de Cirurgias", 
                  ROUND(SUM(valor_total), 2) as "Faturamento (R$)",
                  ROUND(AVG(valor_total), 2) as "Custo Médio (R$)"
                FROM master_healthcare 
                WHERE hospital_uf = '{state.state}' AND procedimento_codigo LIKE '040505%' 
                GROUP BY hospital_nome 
                ORDER BY "Volume de Cirurgias" DESC
                """
                def narrative_builder(df):
                    if df.empty:
                        return f"Nenhuma cirurgia de catarata registrada no estado de {state_name} no período de competência analisado."
                    top_h = df.iloc[0]['Hospital']
                    top_v = df.iloc[0]['Volume de Cirurgias']
                    tot_v = df['Volume de Cirurgias'].sum()
                    return f"Foram realizadas {tot_v} cirurgias de catarata no total em {state_name}. O estabelecimento líder em volume é {top_h}, com {top_v} cirurgias realizadas."
            
            # Rule 3: Revenue / financial totals
            elif "faturamento" in q or "receita" in q or "valores" in q or "quanto custou" in q or "custo" in q:
                sql = f"""
                SELECT 
                  hospital_nome as Hospital, 
                  ROUND(SUM(valor_total), 2) as "Faturamento Total (R$)", 
                  COUNT(*) as "Total de Procedimentos"
                FROM master_healthcare 
                WHERE hospital_uf = '{state.state}'
                GROUP BY hospital_nome 
                ORDER BY "Faturamento Total (R$)" DESC
                """
                def narrative_builder(df):
                    if df.empty:
                        return f"Sem dados de faturamento para o estado de {state_name}."
                    total_pago = df['Faturamento Total (R$)'].sum()
                    top_h = df.iloc[0]['Hospital']
                    top_f = df.iloc[0]['Faturamento Total (R$)']
                    return f"O faturamento total em saúde identificado em {state_name} foi de R$ {total_pago:,.2f}. O hospital com maior receita captada foi o {top_h}, com R$ {top_f:,.2f}."
            
            # Rule 4: Underserved municipalities
            elif "municipio" in q or "municípios" in q or "cidade" in q or "carente" in q or "atendimento" in q:
                sql = f"""
                SELECT 
                  m.nome as "Município do Paciente", 
                  m.uf as UF, 
                  COALESCE(COUNT(h.cnes), 0) as "Pacientes Atendidos"
                FROM clean_ibge m 
                LEFT JOIN master_healthcare h ON m.municipio_id = h.paciente_municipio_id AND h.procedimento_codigo LIKE '040505%' AND h.hospital_uf = '{state.state}'
                WHERE m.uf = '{state.state}'
                GROUP BY m.nome, m.uf 
                ORDER BY "Pacientes Atendidos" ASC 
                LIMIT 15
                """
                def narrative_builder(df):
                    zero_count = len(df[df['Pacientes Atendidos'] == 0])
                    return f"Análise de cobertura: identificamos {zero_count} municípios em {state_name} sem registros de atendimento/cirurgias de catarata para seus residentes no mês (volume zero), indicando possíveis gargalos de acesso."
            
            # Rule 5: Hospital stay / average days
            elif "permanencia" in q or "internação" in q or "tempo" in q or "dias" in q:
                sql = f"""
                SELECT 
                  hospital_nome as Hospital, 
                  ROUND(AVG(dias_permanencia), 1) as "Média de Permanência (dias)", 
                  COUNT(*) as "Total de Altas"
                FROM master_healthcare 
                WHERE hospital_uf = '{state.state}'
                GROUP BY hospital_nome 
                ORDER BY "Média de Permanência (dias)" DESC
                """
                def narrative_builder(df):
                    if df.empty:
                        return f"Sem dados de internação para o estado de {state_name}."
                    top_h = df.iloc[0]['Hospital']
                    top_d = df.iloc[0]['Média de Permanência (dias)']
                    return f"A média geral de permanência dos pacientes internados em {state_name} varia por hospital. O maior tempo médio de internação foi registrado no {top_h}, com {top_d} dias por paciente."
            
            # Default fallback query
            else:
                sql = f"""
                SELECT 
                  hospital_nome as Hospital, 
                  COUNT(*) as "Procedimentos", 
                  ROUND(SUM(valor_total), 2) as "Faturamento (R$)" 
                FROM master_healthcare 
                WHERE hospital_uf = '{state.state}'
                GROUP BY hospital_nome 
                ORDER BY "Procedimentos" DESC
                """
                narrative_builder = lambda df: f"Consulta geral executada com sucesso. Encontrados registros de {len(df)} hospitais operando no período no estado de {state_name}."

            # Execute SQL
            df = db.execute(sql)
            state.sql_query = sql
            state.query_result = df.to_dict(orient="records")
            state.narrative = narrative_builder(df)
            
        # Format JSON Output
        output_dict = {
            "question": state.question,
            "sql_executed": state.sql_query,
            "narrative": state.narrative,
            "data": state.query_result
        }
        state.json_output = json.dumps(output_dict, indent=2, ensure_ascii=False)
        state.status = "success"
        
        db.close()
        
    except Exception as e:
        state.status = "failed"
        state.error = str(e)
        print(f"QA Agent: Error: {e}")
        
    return state
