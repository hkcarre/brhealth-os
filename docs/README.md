# Terminal de Inteligência de Saúde BR - GitHub Pages

Esta pasta contém o frontend estático e auto-suficiente do dashboard **BRHealth OS**, projetado no estilo clássico do Terminal Bloomberg.

## Características
1. **100% Client-Side:** Funciona totalmente no navegador sem necessidade de banco de dados ativo ou backend Python rodando.
2. **Dados Pré-carregados:** Inclui as respostas reais computadas para o estado do **Acre (competência Janeiro de 2024)** usando dados integrados do DATASUS SIH, CNES e IBGE.
3. **Agente QA Inteligente Integrado:** O motor JavaScript simula o Agente QA executando queries SQL no navegador e apresentando narratives e gráficos interativos usando a biblioteca **Chart.js**.
4. **Modo Online (Conectado):** Nas configurações do painel, você pode habilitar a conexão HTTP dinâmica com a sua API FastAPI local (`http://127.0.0.1:8001`) ou qualquer endpoint de produção para consultar qualquer estado do Brasil em tempo real.

## Como habilitar o GitHub Pages

Para colocar este dashboard no ar para seus colegas acessarem de qualquer lugar gratuitamente:

1. Acesse a página do seu repositório no GitHub.
2. Vá em **Settings** (Configurações) no menu superior.
3. No painel esquerdo, clique em **Pages**.
4. Sob **Build and deployment -> Source**, certifique-se de que está selecionado **Deploy from a branch**.
5. Sob **Branch**, selecione a branch `master` (ou `main`) e no seletor de pasta ao lado selecione **`/docs`**.
6. Clique em **Save**.
7. Aguarde de 1 a 2 minutos. O link público será gerado e exibido no topo da página (ex: `https://seu-usuario.github.io/brhealth-os/`).
