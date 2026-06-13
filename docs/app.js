document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('query-form');
    const input = document.getElementById('question-input');
    const submitBtn = document.getElementById('submit-btn');
    const narrativeOutput = document.getElementById('narrative-output');
    const sqlOutput = document.getElementById('sql-output');
    const tableHead = document.getElementById('table-head');
    const tableBody = document.getElementById('table-body');
    
    // Navigation Items
    const navQa = document.getElementById('nav-qa');
    const navDatalake = document.getElementById('nav-datalake');
    const navForecast = document.getElementById('nav-forecast');
    const navGraph = document.getElementById('nav-graph');
    const navSettings = document.getElementById('nav-settings');
    
    // Settings Elements
    const settingsCard = document.getElementById('settings-card');
    const engineModeSelect = document.getElementById('engine-mode');
    const apiUrlInput = document.getElementById('api-url');
    const statusDot = document.getElementById('status-indicator-dot');
    const statusText = document.getElementById('status-text');
    
    // Chart Elements
    const chartSection = document.getElementById('chart-section');
    const chartCtx = document.getElementById('dashboard-chart').getContext('2d');
    let activeChart = null;

    // PRE-LOADED REAL DUCKDB DATA (Acre, competencia Jan/2024)
    const dbData = {
        hospitals: [
            { "Hospital": "AEROBRAN TAXI AEREO", "CNES": "7619278", "Cidade": "CRUZEIRO DO SUL", "UF": "AC" },
            { "Hospital": "AMBULANCIA USA RIO BRANCO 01", "CNES": "7132921", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "AMBULANCIA USB ACRELANDIA 11", "CNES": "7026641", "Cidade": "ACRELÂNDIA", "UF": "AC" },
            { "Hospital": "AMBULANCIA USB BRASILEIA 19", "CNES": "7030789", "Cidade": "BRASILÉIA", "UF": "AC" },
            { "Hospital": "AMBULANCIA USB DE TARAUACA", "CNES": "7325495", "Cidade": "TARAUACÁ", "UF": "AC" },
            { "Hospital": "AMBULANCIA USB FEIJO", "CNES": "7110561", "Cidade": "FEIJÓ", "UF": "AC" },
            { "Hospital": "AMBULANCIA USB PLACIDO DE CASTRO 12", "CNES": "7241194", "Cidade": "PLÁCIDO DE CASTRO", "UF": "AC" },
            { "Hospital": "AMBULANCIA USB SENA MADUREIRA 21", "CNES": "7241208", "Cidade": "SENA MADUREIRA", "UF": "AC" },
            { "Hospital": "AMBULANCIA USB SENADOR GUIOMARD 15", "CNES": "7241216", "Cidade": "SENADOR GUIOMARD", "UF": "AC" },
            { "Hospital": "AMBULANCIA USB XAPURI 18", "CNES": "7241224", "Cidade": "XAPURI", "UF": "AC" },
            { "Hospital": "CAD IMAGEM", "CNES": "6910335", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "CASA DE ACOLHIDA SOUZA ARAUJO", "CNES": "0773093", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "CEDIMP", "CNES": "6861849", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "FUNDHACRE", "CNES": "2001586", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "HOA HOSPITAL OFTALMOLOGICO DO ACRE LTDA FILIAL", "CNES": "5625645", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "HOSPITAL DA FAMILIA DR MARCIO ROGERIO CAMARGO", "CNES": "5353947", "Cidade": "JORDÃO", "UF": "AC" },
            { "Hospital": "HOSPITAL DA MULHER E DA CRIANCA DO JURUA", "CNES": "2000296", "Cidade": "CRUZEIRO DO SUL", "UF": "AC" },
            { "Hospital": "HOSPITAL DE AMOR RIO BRANCO", "CNES": "9882138", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "HOSPITAL DE SAUDE MENTAL DO ACRE", "CNES": "2000857", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "HOSPITAL DR ABEL PINHEIRO MACIEL FILHO", "CNES": "2000083", "Cidade": "MÂNCIO LIMA", "UF": "AC" },
            { "Hospital": "HOSPITAL DR ARY RODRIGUES", "CNES": "2000725", "Cidade": "SENADOR GUIOMARD", "UF": "AC" },
            { "Hospital": "HOSPITAL DR MANOEL MARINHO MONTE", "CNES": "2000997", "Cidade": "PLÁCIDO DE CASTRO", "UF": "AC" },
            { "Hospital": "HOSPITAL DR SANSAO GOMES", "CNES": "2000121", "Cidade": "TARAUACÁ", "UF": "AC" },
            { "Hospital": "HOSPITAL EPAMINONDAS JACOME", "CNES": "2000393", "Cidade": "XAPURI", "UF": "AC" },
            { "Hospital": "HOSPITAL GERAL DE CLINICAS DE RIO BRANCO", "CNES": "2001578", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "HOSPITAL GERAL DE FEIJO", "CNES": "2000636", "Cidade": "FEIJÓ", "UF": "AC" },
            { "Hospital": "HOSPITAL INFANTIL IOLANDA COSTA E SILVA", "CNES": "2000385", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "HOSPITAL JOAO CANCIO FERNANDES", "CNES": "2000865", "Cidade": "SENA MADUREIRA", "UF": "AC" },
            { "Hospital": "HOSPITAL RAIMUNDO CHAAR", "CNES": "2001500", "Cidade": "BRASILÉIA", "UF": "AC" },
            { "Hospital": "HOSPITAL REGIONAL DO JURUA IRMA NAIR TERESINHA REICHERT", "CNES": "5336171", "Cidade": "CRUZEIRO DO SUL", "UF": "AC" },
            { "Hospital": "HOSPITAL SANTA JULIANA", "CNES": "2002078", "Cidade": "RIO BRANCO", "UF": "AC" },
            { "Hospital": "HOSPITAL UROLOGICO DO ACRE", "CNES": "9246010", "Cidade": "RIO BRANCO", "UF": "AC" }
        ],
        catarata: [
            { "Hospital": "HOA HOSPITAL OFTALMOLOGICO DO ACRE LTDA FILIAL", "Volume de Cirurgias": 346, "Faturamento (R$)": 229087.19, "Custo Médio (R$)": 662.10 }
        ],
        faturamento: [
            { "Hospital": "FUNDHACRE", "Faturamento Total (R$)": 3279591.25, "Total de Procedimentos": 8494 },
            { "Hospital": "HOSPITAL GERAL DE CLINICAS DE RIO BRANCO", "Faturamento Total (R$)": 1477628.69, "Total de Procedimentos": 14832 },
            { "Hospital": "HOSPITAL SANTA JULIANA", "Faturamento Total (R$)": 1311077.74, "Total de Procedimentos": 1116 },
            { "Hospital": "CEDIMP", "Faturamento Total (R$)": 1194940.42, "Total de Procedimentos": 11573 },
            { "Hospital": "HOSPITAL REGIONAL DO JURUA IRMA NAIR TERESINHA REICHERT", "Faturamento Total (R$)": 828256.94, "Total de Procedimentos": 3719 },
            { "Hospital": "CENTRAL ESTADUAL DE REGULACAO AMBULATORIAL", "Faturamento Total (R$)": 612988.20, "Total de Procedimentos": 1078 },
            { "Hospital": "CENTRO DE APOIO DIAGNOSTICO ANALISES CLINICAS CAD", "Faturamento Total (R$)": 553234.77, "Total de Procedimentos": 254 },
            { "Hospital": "HOSPITAL UROLOGICO DO ACRE", "Faturamento Total (R$)": 484371.97, "Total de Procedimentos": 227 },
            { "Hospital": "UPA 24 HORAS DO 2 DISTRITO", "Faturamento Total (R$)": 461662.11, "Total de Procedimentos": 587 },
            { "Hospital": "MATERNIDADE E CLINICAS DE MULHERES BARBARA HELIODORA", "Faturamento Total (R$)": 364971.39, "Total de Procedimentos": 1359 },
            { "Hospital": "UPA DA SOBRAL FRANCO SILVA", "Faturamento Total (R$)": 304663.73, "Total de Procedimentos": 773 },
            { "Hospital": "HOA HOSPITAL OFTALMOLOGICO DO ACRE LTDA FILIAL", "Faturamento Total (R$)": 275686.38, "Total de Procedimentos": 1440 },
            { "Hospital": "HOSPITAL RAIMUNDO CHAAR", "Faturamento Total (R$)": 259647.11, "Total de Procedimentos": 810 },
            { "Hospital": "HOSPITAL DA MULHER E DA CRIANCA DO JURUA", "Faturamento Total (R$)": 241191.74, "Total de Procedimentos": 1321 },
            { "Hospital": "HOSPITAL JOAO CANCIO FERNANDES", "Faturamento Total (R$)": 165198.57, "Total de Procedimentos": 299 }
        ],
        municipios: [
            { "Município do Paciente": "RIO BRANCO", "UF": "AC", "Pacientes Atendidos": 246 },
            { "Município do Paciente": "SENADOR GUIOMARD", "UF": "AC", "Pacientes Atendidos": 14 },
            { "Município do Paciente": "SENA MADUREIRA", "UF": "AC", "Pacientes Atendidos": 11 },
            { "Município do Paciente": "CRUZEIRO DO SUL", "UF": "AC", "Pacientes Atendidos": 8 },
            { "Município do Paciente": "ACRELÂNDIA", "UF": "AC", "Pacientes Atendidos": 7 },
            { "Município do Paciente": "BUJARI", "UF": "AC", "Pacientes Atendidos": 6 },
            { "Município do Paciente": "BRASILÉIA", "UF": "AC", "Pacientes Atendidos": 5 },
            { "Município do Paciente": "CAPIXABA", "UF": "AC", "Pacientes Atendidos": 4 },
            { "Município do Paciente": "PLACIDO DE CASTRO", "UF": "AC", "Pacientes Atendidos": 0 },
            { "Município do Paciente": "PORTO ACRE", "UF": "AC", "Pacientes Atendidos": 0 },
            { "Município do Paciente": "RODRIGUES ALVES", "UF": "AC", "Pacientes Atendidos": 0 },
            { "Município do Paciente": "SANTA ROSA DO PURUS", "UF": "AC", "Pacientes Atendidos": 0 },
            { "Município do Paciente": "ASSIS BRASIL", "UF": "AC", "Pacientes Atendidos": 0 },
            { "Município do Paciente": "EPITACIOLÂNDIA", "UF": "AC", "Pacientes Atendidos": 0 },
            { "Município do Paciente": "JORDÃO", "UF": "AC", "Pacientes Atendidos": 0 }
        ],
        permanencia: [
            { "Hospital": "HOSPITAL INFANTIL IOLANDA COSTA E SILVA", "Média de Permanência (dias)": 8.4, "Total de Altas": 95 },
            { "Hospital": "HOSPITAL DE SAUDE MENTAL DO ACRE", "Média de Permanência (dias)": 3.2, "Total de Altas": 292 },
            { "Hospital": "HOSPITAL SANTA JULIANA", "Média de Permanência (dias)": 1.8, "Total de Altas": 1116 },
            { "Hospital": "HOSPITAL JOAO CANCIO FERNANDES", "Média de Permanência (dias)": 1.3, "Total de Altas": 299 },
            { "Hospital": "MATERNIDADE E CLINICAS DE MULHERES BARBARA HELIODORA", "Média de Permanência (dias)": 1.1, "Total de Altas": 1359 },
            { "Hospital": "HOSPITAL RAIMUNDO CHAAR", "Média de Permanência (dias)": 0.9, "Total de Altas": 810 },
            { "Hospital": "UNIDADE MISTA MARIA DE JESUS ANDER MAZICA", "Média de Permanência (dias)": 0.9, "Total de Altas": 78 },
            { "Hospital": "HOSPITAL DR SANSAO GOMES", "Média de Permanência (dias)": 0.8, "Total de Altas": 449 },
            { "Hospital": "HOSPITAL DA MULHER E DA CRIANCA DO JURUA", "Média de Permanência (dias)": 0.7, "Total de Altas": 1321 },
            { "Hospital": "HOSPITAL REGIONAL DO JURUA IRMA NAIR TERESINHA REICHERT", "Média de Permanência (dias)": 0.7, "Total de Altas": 3719 }
        ],
        fallback: [
            { "Hospital": "HOSPITAL GERAL DE CLINICAS DE RIO BRANCO", "Procedimentos": 14832, "Faturamento (R$)": 1477628.69 },
            { "Hospital": "CEDIMP", "Procedimentos": 11573, "Faturamento (R$)": 1194940.42 },
            { "Hospital": "UPA DO VALE DO JURUA JAQUES PEREIRA BRAGA", "Procedimentos": 9383, "Faturamento (R$)": 73880.06 },
            { "Hospital": "FUNDHACRE", "Procedimentos": 8494, "Faturamento (R$)": 3279591.25 },
            { "Hospital": "HOA HOSPITAL OFTALMOLOGICO DO ACRE LTDA FILIAL", "Procedimentos": 1440, "Faturamento (R$)": 275686.38 }
        ]
    };

    // Settings Panel Toggle
    navSettings.addEventListener('click', (e) => {
        e.preventDefault();
        settingsCard.classList.toggle('collapsed');
        setActiveNavItem(navSettings);
    });

    // Sidebar navigation mock click
    [navQa, navDatalake, navForecast, navGraph].forEach(navItem => {
        navItem.addEventListener('click', (e) => {
            e.preventDefault();
            settingsCard.classList.add('collapsed');
            setActiveNavItem(navItem);

            const title = navItem.textContent.trim();
            if (navItem.id === 'nav-qa') {
                narrativeOutput.textContent = "Selecione ou digite uma pergunta acima para iniciar a análise dos dados integrados do SUS.";
                sqlOutput.textContent = "-- Nenhuma query executada";
                renderTable([]);
                chartSection.classList.add('hidden');
            } else {
                narrativeOutput.innerHTML = `<span style="color: var(--accent-primary)">O módulo '${title}' será ativado em uma futura versão. Atualmente, os dados integrados do SUS do Acre de Jan/2024 estão carregados no Data Lakehouse. Utilize a aba 'Consultar IA' para fazer análises.</span>`;
                sqlOutput.textContent = `-- Módulo ${title} em desenvolvimento`;
                renderTable([]);
                chartSection.classList.add('hidden');
            }
        });
    });

    function setActiveNavItem(item) {
        document.querySelectorAll('.nav-item').forEach(nav => {
            nav.classList.remove('active');
            nav.removeAttribute('aria-current');
        });
        item.classList.add('active');
        item.setAttribute('aria-current', 'page');
    }

    // Suggested Queries click handler
    document.querySelectorAll('.suggest-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            input.value = btn.getAttribute('data-query');
            form.dispatchEvent(new Event('submit'));
        });
    });

    // Status display sync
    engineModeSelect.addEventListener('change', () => {
        const mode = engineModeSelect.value;
        if (mode === 'offline') {
            statusDot.className = 'status-indicator online';
            statusText.textContent = 'Simulação Offline';
        } else {
            statusDot.className = 'status-indicator online amber';
            statusText.textContent = 'Modo API Real';
        }
    });

    // Form Submit (Orchestrator)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = input.value.trim();
        if (!question) return;

        // Visual Loading feedback
        submitBtn.disabled = true;
        submitBtn.querySelector('span').textContent = 'Analisando...';
        submitBtn.querySelector('svg').style.animation = 'spin 1s linear infinite';
        narrativeOutput.innerHTML = '<span style="color: var(--text-muted)">Consultando o Data Lakehouse SUS...</span>';
        sqlOutput.textContent = '-- Compilando query SQL...';
        tableHead.innerHTML = '<th scope="col">Dados</th>';
        tableBody.innerHTML = '<tr><td class="empty-state">Pesquisando registros...</td></tr>';
        chartSection.classList.add('hidden');

        const mode = engineModeSelect.value;
        if (mode === 'online') {
            // Real HTTP API Request
            const apiUrl = apiUrlInput.value.trim() || 'http://127.0.0.1:8001';
            try {
                const response = await fetch(`${apiUrl}/api/ask`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });
                if (!response.ok) throw new Error(`Status ${response.status}`);
                const res = await response.json();
                
                // Render results from API
                narrativeOutput.innerHTML = `<strong>Insight:</strong><br/>${res.narrative}`;
                sqlOutput.textContent = res.sql_executed;
                renderTable(res.data);
                
                // Dynamic Chart if relevant
                renderDynamicChart(question, res.data);
            } catch (error) {
                console.error(error);
                narrativeOutput.innerHTML = `<span style="color: var(--accent-danger)">Erro de conexão: Não foi possível alcançar a API em ${apiUrl}. Verifique se o servidor FastAPI está ativo.</span>`;
                sqlOutput.textContent = `-- Falha na chamada da API\n-- Erro: ${error.message}`;
                tableBody.innerHTML = '<tr><td class="empty-state" style="color: var(--accent-danger)">Erro ao carregar dados remotos</td></tr>';
            } finally {
                resetButtonState();
            }
        } else {
            // Simulated Client-Side Engine (Local pre-calculated data)
            setTimeout(() => {
                const simResult = processSimulatedQuery(question);
                narrativeOutput.innerHTML = `<strong>Insight:</strong><br/>${simResult.narrative}`;
                sqlOutput.textContent = simResult.sql;
                renderTable(simResult.data);
                renderDynamicChart(question, simResult.data, simResult.type);
                resetButtonState();
            }, 600); // Small delay to feel like a real agent processing
        }
    });

    function resetButtonState() {
        submitBtn.disabled = false;
        submitBtn.querySelector('span').textContent = 'Executar';
        submitBtn.querySelector('svg').style.animation = 'none';
    }

    // OFFLINE MOCK QUERY ENGINE
    function processSimulatedQuery(question) {
        const q = question.toLowerCase().trim();

        // Rule 1: Distinct Hospitals
        if (q.includes("quantos hospitais") || q.includes("hospitais distintos") || q.includes("lista de hospitais")) {
            return {
                type: 'hospitals',
                sql: `SELECT hospital_nome as Hospital, cnes as CNES, hospital_municipio_nome as Cidade, hospital_uf as UF \nFROM master_healthcare \nGROUP BY ALL \nORDER BY hospital_nome`,
                narrative: `Foram identificados ${dbData.hospitals.length} estabelecimentos de saúde distintos cadastrados e mapeados no banco de dados do SUS no Acre para esta competência.`,
                data: dbData.hospitals
            };
        }

        // Rule 2: Cataract Surgeries
        if (q.includes("volume") || q.includes("cirurgias") || q.includes("catarata") || q.includes("quantidade")) {
            return {
                type: 'catarata',
                sql: `SELECT \n  hospital_nome as Hospital, \n  COUNT(*) as "Volume de Cirurgias", \n  ROUND(SUM(valor_total), 2) as "Faturamento (R$)",\n  ROUND(AVG(valor_total), 2) as "Custo Médio (R$)"\nFROM master_healthcare \nWHERE procedimento_codigo LIKE '040505%'\nGROUP BY hospital_nome\nORDER BY "Volume de Cirurgias" DESC`,
                narrative: `Foram realizadas 346 cirurgias de catarata no total. O estabelecimento líder absoluto em volume é o HOA HOSPITAL OFTALMOLOGICO DO ACRE LTDA FILIAL, com 346 cirurgias realizadas (100% de market share). Isso demonstra uma centralização total do serviço de oftalmologia cirúrgica de média complexidade pelo SUS na capital Rio Branco.`,
                data: dbData.catarata
            };
        }

        // Rule 3: Revenue / Costs
        if (q.includes("faturamento") || q.includes("receita") || q.includes("valores") || q.includes("quanto custou") || q.includes("custo")) {
            return {
                type: 'faturamento',
                sql: `SELECT \n  hospital_nome as Hospital, \n  ROUND(SUM(valor_total), 2) as "Faturamento Total (R$)", \n  COUNT(*) as "Total de Procedimentos"\nFROM master_healthcare \nGROUP BY hospital_nome \nORDER BY "Faturamento Total (R$)" DESC`,
                narrative: `O faturamento total em saúde identificado no estado do Acre foi de R$ 9.697.801,65. O hospital com maior receita captada foi a FUNDHACRE (Fundação Hospital Estadual do Acre), captando R$ 3.279.591,25 (33.8% do faturamento estadual). O segundo colocado é o Hospital Geral de Clínicas de Rio Branco, com R$ 1.477.628,69.`,
                data: dbData.faturamento
            };
        }

        // Rule 4: Underserved municipalities
        if (q.includes("municipio") || q.includes("municípios") || q.includes("cidade") || q.includes("carente") || q.includes("atendimento")) {
            return {
                type: 'municipios',
                sql: `SELECT \n  m.nome as "Município do Paciente", \n  m.uf as UF, \n  COALESCE(COUNT(h.cnes), 0) as "Pacientes Atendidos"\nFROM clean_ibge m \nLEFT JOIN master_healthcare h ON m.municipio_id = h.paciente_municipio_id AND h.procedimento_codigo LIKE '040505%'\nGROUP BY m.nome, m.uf \nORDER BY "Pacientes Atendidos" ASC \nLIMIT 15`,
                narrative: `Análise de cobertura geográfica: identificamos 7 municípios do Acre com volume ZERO de pacientes atendidos para cirurgias de catarata (ex: Plácido de Castro, Porto Acre, Rodrigues Alves, Assis Brasil, Epitaciolândia). Isso aponta para graves problemas de acesso a serviços de oftalmologia cirúrgica nas fronteiras e áreas rurais, exigindo mutirões ou redes de transporte eletivo.`,
                data: dbData.municipios
            };
        }

        // Rule 5: Length of Stay
        if (q.includes("permanencia") || q.includes("internação") || q.includes("tempo") || q.includes("dias")) {
            return {
                type: 'permanencia',
                sql: `SELECT \n  hospital_nome as Hospital, \n  ROUND(AVG(dias_permanencia), 1) as "Média de Permanência (dias)", \n  COUNT(*) as "Total de Altas"\nFROM master_healthcare \nGROUP BY hospital_nome \nORDER BY "Média de Permanência (dias)" DESC`,
                narrative: `A média geral de permanência dos pacientes internados varia drasticamente. O maior tempo médio de internação foi registrado no Hospital Infantil Iolanda Costa e Silva, com 8.4 dias por paciente, seguido pelo Hospital de Saúde Mental do Acre, com 3.2 dias. Esses valores refletem a complexidade clínica de pediatria e saúde mental, enquanto procedimentos cirúrgicos gerais registram médias inferiores a 1 dia.`,
                data: dbData.permanencia
            };
        }

        // Fallback default
        return {
            type: 'fallback',
            sql: `SELECT \n  hospital_nome as Hospital, \n  COUNT(*) as "Procedimentos", \n  ROUND(SUM(valor_total), 2) as "Faturamento (R$)" \nFROM master_healthcare \nGROUP BY hospital_nome \nORDER BY "Procedimentos" DESC`,
            narrative: `Consulta geral do Data Lakehouse executada com sucesso. Foram retornados dados de faturamento e volume agregados por hospital no estado do Acre. O Hospital Geral de Clínicas lidera em volume de atendimentos gerais com 14.832 procedimentos realizados, embora possua ticket médio inferior ao de hospitais de alta complexidade como a FUNDHACRE.`,
            data: dbData.fallback
        };
    }

    // Dynamic rendering of tables
    function renderTable(dataArray) {
        if (!dataArray || dataArray.length === 0) {
            tableHead.innerHTML = '<th scope="col">Dados</th>';
            tableBody.innerHTML = '<tr><td class="empty-state">Nenhum dado retornado</td></tr>';
            return;
        }

        const headers = Object.keys(dataArray[0]);
        let headHtml = '';
        headers.forEach(h => {
            headHtml += `<th scope="col">${h}</th>`;
        });
        tableHead.innerHTML = headHtml;

        let bodyHtml = '';
        dataArray.forEach(row => {
            bodyHtml += '<tr>';
            headers.forEach(h => {
                let val = row[h];
                if (typeof val === 'number' && h.includes('(R$)')) {
                    val = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
                } else if (typeof val === 'number' && !Number.isInteger(val)) {
                    val = val.toFixed(1);
                }
                bodyHtml += `<td>${val}</td>`;
            });
            bodyHtml += '</tr>';
        });
        tableBody.innerHTML = bodyHtml;
    }

    // Dynamic chart drawer using Chart.js
    function renderDynamicChart(question, data, type) {
        if (activeChart) {
            activeChart.destroy();
            activeChart = null;
        }

        // If no type was passed (e.g. from API mode), try to infer it
        let queryType = type;
        if (!queryType) {
            const q = question.toLowerCase();
            if (q.includes("quantos hospitais") || q.includes("hospitais distintos")) queryType = 'hospitals';
            else if (q.includes("volume") || q.includes("catarata")) queryType = 'catarata';
            else if (q.includes("faturamento") || q.includes("receita")) queryType = 'faturamento';
            else if (q.includes("municipio") || q.includes("municípios")) queryType = 'municipios';
            else if (q.includes("permanencia") || q.includes("internação")) queryType = 'permanencia';
            else queryType = 'fallback';
        }

        if (queryType === 'hospitals') {
            chartSection.classList.add('hidden');
            return;
        }

        chartSection.classList.remove('hidden');

        let chartData = {
            labels: [],
            datasets: []
        };
        let chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#aeaeae', font: { family: 'Inter' } }
                }
            },
            scales: {
                x: { grid: { color: '#1a1d24' }, ticks: { color: '#aeaeae', font: { family: 'Inter' } } },
                y: { grid: { color: '#1a1d24' }, ticks: { color: '#aeaeae', font: { family: 'Inter' } } }
            }
        };

        if (queryType === 'catarata') {
            // Show volume distribution (Pie Chart)
            chartData.labels = data.map(r => r.Hospital || r.hospital_nome || 'Outros');
            chartData.datasets = [{
                label: 'Volume de Cirurgias',
                data: data.map(r => r['Volume de Cirurgias'] || r.procedure_volume || 0),
                backgroundColor: ['#ff9f0a', '#00d2ff', '#30d158', '#ff453a'],
                borderWidth: 0
            }];
            activeChart = new Chart(chartCtx, {
                type: 'pie',
                data: chartData,
                options: {
                    ...chartOptions,
                    plugins: {
                        legend: { position: 'right', labels: { color: '#aeaeae' } }
                    }
                }
            });
        } 
        else if (queryType === 'faturamento') {
            // Show top 7 faturamento
            const subset = data.slice(0, 7);
            chartData.labels = subset.map(r => {
                const name = r.Hospital || r.hospital_nome || '';
                return name.length > 20 ? name.slice(0, 18) + '...' : name;
            });
            chartData.datasets = [{
                label: 'Faturamento Total (R$)',
                data: subset.map(r => r['Faturamento Total (R$)'] || r.total_revenue || 0),
                backgroundColor: 'rgba(255, 159, 10, 0.7)',
                borderColor: '#ff9f0a',
                borderWidth: 1
            }];
            activeChart = new Chart(chartCtx, {
                type: 'bar',
                data: chartData,
                options: {
                    ...chartOptions,
                    indexAxis: 'y'
                }
            });
        }
        else if (queryType === 'municipios') {
            // Patient origins
            chartData.labels = data.map(r => r['Município do Paciente'] || r.paciente_municipio_nome || 'Outro');
            chartData.datasets = [{
                label: 'Pacientes Atendidos',
                data: data.map(r => r['Pacientes Atendidos'] || 0),
                backgroundColor: 'rgba(0, 210, 255, 0.7)',
                borderColor: '#00d2ff',
                borderWidth: 1
            }];
            activeChart = new Chart(chartCtx, {
                type: 'bar',
                data: chartData,
                options: chartOptions
            });
        }
        else if (queryType === 'permanencia') {
            // Stay length
            const subset = data.slice(0, 8);
            chartData.labels = subset.map(r => {
                const name = r.Hospital || r.hospital_nome || '';
                return name.length > 20 ? name.slice(0, 18) + '...' : name;
            });
            chartData.datasets = [{
                label: 'Média de Permanência (dias)',
                data: subset.map(r => r['Média de Permanência (dias)'] || r.average_stay_days || 0),
                backgroundColor: 'rgba(48, 209, 88, 0.7)',
                borderColor: '#30d158',
                borderWidth: 1
            }];
            activeChart = new Chart(chartCtx, {
                type: 'bar',
                data: chartData,
                options: chartOptions
            });
        }
        else {
            // Fallback general bar chart
            const subset = data.slice(0, 6);
            chartData.labels = subset.map(r => {
                const name = r.Hospital || r.hospital_nome || '';
                return name.length > 20 ? name.slice(0, 18) + '...' : name;
            });
            chartData.datasets = [{
                label: 'Faturamento (R$)',
                data: subset.map(r => r['Faturamento (R$)'] || r.total_revenue || 0),
                backgroundColor: 'rgba(255, 159, 10, 0.6)',
                borderColor: '#ff9f0a',
                borderWidth: 1
            }];
            activeChart = new Chart(chartCtx, {
                type: 'bar',
                data: chartData,
                options: chartOptions
            });
        }
    }
});
