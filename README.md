# BRHealth OS - Bloomberg Terminal da Saúde

Este é o produto final da nossa plataforma de Inteligência de Dados Públicos (Focada em Saúde / DATASUS). O sistema orquestra agentes de Inteligência Artificial usando LangGraph para extrair, limpar, cruzar e gerar insights sobre o mercado de saúde no Brasil.

---

## 🚀 Como Executar o Projeto Localmente

Siga estes passos para rodar o "Bloomberg Terminal" na sua própria máquina.

### Pré-requisitos
- [Python 3.10+](https://www.python.org/downloads/)
- Git

### 1. Clonar o Repositório
Abra o seu terminal e rode:
```bash
git clone https://github.com/hkcarre/brhealth-os.git
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
pip install dbc-to-dbf
```

### 4. Executar a Ingestão de Dados Públicos Reais
Nosso pipeline de IA faz o download, descompressão e cruzamento relacional de dados reais do DATASUS (SIH/SIA), CNES e IBGE. Para rodar a ingestão de dados reais para o Acre:
```bash
python main.py
```

### 5. Rodar o Backend e a Interface Gráfica
Para iniciar a API do FastAPI e o painel web:
```bash
python -m uvicorn api:app --port 8001
```
**Pronto!** Agora basta abrir o seu navegador (Chrome/Edge/Safari) e acessar: **http://127.0.0.1:8001**

---

## ☁️ Hospedagem Web Grátis (Hugging Face Spaces)

Você pode rodar esta aplicação na nuvem de forma gratuita para compartilhar o link com seus colegas:

1. Acesse o [Hugging Face Spaces](https://huggingface.co/spaces) e crie uma conta gratuita.
2. Clique em **Create new Space**.
3. Defina um nome para o espaço, selecione **Docker** como o SDK e escolha **Blank** como template.
4. Conecte com o seu repositório do GitHub `hkcarre/brhealth-os` ou faça upload dos arquivos (incluindo o `Dockerfile` que está na raiz).
5. O Hugging Face irá ler o `Dockerfile`, compilar a imagem e colocar o painel online de forma 100% gratuita com link HTTPS público!

---

## 🏗 Arquitetura do Sistema

O projeto é modular e possui as seguintes camadas:
- **Data Lakehouse:** DuckDB e Parquet (Processamento de microdados na memória).
- **Agentes (LangGraph):** Módulos Python independentes em `agents/` que cuidam da ingestão, limpeza, resolução de entidades (fuzzy matching) e cálculos estatísticos (ARIMA).
- **Backend:** FastAPI expõe os resultados dos agentes via endpoints HTTP.
- **Frontend:** Vanilla JS/CSS/HTML servidos pelo FastAPI em um design *Premium Dark Mode*.
