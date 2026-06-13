# BRHealth OS - Bloomberg Terminal da Saúde

Este é o Produto Mínimo Viável (MVP) da nossa plataforma de Inteligência de Dados Públicos (Focada em Saúde / DATASUS). O sistema orquestra agentes de Inteligência Artificial usando LangGraph para extrair, limpar, cruzar e gerar insights sobre o mercado de saúde no Brasil.

## 🚀 Como Executar o Projeto Localmente

Siga estes passos para rodar o "Bloomberg Terminal" na sua própria máquina.

### Pré-requisitos
- [Python 3.10+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Opcional, para rodar o MinIO e Neo4j localmente)
- Git

### 1. Clonar o Repositório
Abra o seu terminal e rode:
```bash
git clone https://github.com/seu-usuario/brhealth-os.git
cd brhealth-os
```

### 2. Configurar o Ambiente Virtual
Crie e ative um ambiente virtual para instalar as dependências sem sujar o seu computador:
```bash
# No Windows:
python -m venv venv
.\venv\Scripts\activate

# No Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
Com o ambiente ativado, instale os pacotes:
```bash
pip install -r requirements.txt
```

*(Nota: Como acabamos de inicializar o repositório, certifique-se de exportar as dependências com `pip freeze > requirements.txt`)*

### 4. Rodar o Backend e a Interface Gráfica
Nossa arquitetura roda usando FastAPI. Para ligar o servidor da API e a Interface Gráfica:
```bash
uvicorn api:app --port 8000
```
**Pronto!** Agora basta abrir o seu navegador (Chrome/Edge/Safari) e acessar: **http://127.0.0.1:8000**

---

## 🏗 Arquitetura do Sistema

O projeto é modular e possui as seguintes camadas:
- **Data Lakehouse:** DuckDB e Parquet (Processamento ultrarrápido na memória)
- **Agentes (LangGraph):** Módulos Python independentes em `agents/` que cuidam da ingestão, limpeza, resolução de entidades (fuzzy matching) e cálculos estatísticos (ARIMA).
- **Backend:** FastAPI expõe os resultados dos agentes via endpoints HTTP.
- **Frontend:** Vanilla JS/CSS/HTML servidos pelo FastAPI em um design *Premium Dark Mode*.

## 🛠 Para desenvolvedores

Caso queira executar testes isolados nas *pipelines* de agentes, você pode rodar os scripts individuais de fase:
```bash
python main.py        # Fase 1: Ingestão e Limpeza
python main_phase2.py # Fase 2: Resolução de Entidades e Query QA
python main_phase3.py # Fase 3: Previsões e Grafo de Conhecimento
python main_phase4.py # Fase 4: Engenharia de Atributos e Geração de Insights
```
