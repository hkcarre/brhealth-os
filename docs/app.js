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

    // Resolve selected state from URL or localStorage or default to AC
    const urlParams = new URLSearchParams(window.location.search);
    let selectedState = urlParams.get('state') || localStorage.getItem('selectedState') || 'AC';
    selectedState = selectedState.toUpperCase();
    if (selectedState !== 'AC' && selectedState !== 'SP') {
        selectedState = 'AC';
    }
    localStorage.setItem('selectedState', selectedState);

    // Update state dropdown
    const stateSelector = document.getElementById('state-selector');
    if (stateSelector) {
        stateSelector.value = selectedState;
        stateSelector.addEventListener('change', () => {
            const newState = stateSelector.value;
            localStorage.setItem('selectedState', newState);
            window.location.href = window.location.pathname + '?state=' + newState;
        });
    }

    // Update state text elements
    const stateNameMap = { 'AC': 'Acre', 'SP': 'São Paulo' };
    const stateName = stateNameMap[selectedState];
    document.querySelectorAll('.state-name-text').forEach(el => {
        el.textContent = stateName;
    });

    // Update the Offline Engine option label in Settings
    const offlineOption = document.querySelector('#engine-mode option[value="offline"]');
    if (offlineOption) {
        offlineOption.textContent = `Simulação Offline (Dados Reais de ${stateName} Pré-carregados)`;
    }

    // Update suggested queries buttons
    document.querySelectorAll('.suggest-btn').forEach(btn => {
        let query = btn.getAttribute('data-query');
        if (selectedState === 'SP') {
            query = query.replace(/Acre/g, 'São Paulo');
        } else {
            query = query.replace(/São Paulo/g, 'Acre');
        }
        btn.setAttribute('data-query', query);
    });

    // Update sidebar navigation links to carry the state parameter
    document.querySelectorAll('.sidebar .nav-menu a').forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '#') {
            const cleanHref = href.split('?')[0];
            link.href = cleanHref + '?state=' + selectedState;
        }
    });

    // Set the data active for the selected state
    const dbData = selectedState === 'SP' ? window.dbDataSP : window.dbDataAC;

    // Settings Panel Toggle
    navSettings.addEventListener('click', (e) => {
        e.preventDefault();
        settingsCard.classList.toggle('collapsed');
        setActiveNavItem(navSettings);
    });

    // Sidebar navigation settings click is handled above, standard HTML hrefs handle page transitions.

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
                    body: JSON.stringify({ question, state: selectedState })
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

        if (selectedState === 'SP') {
            // Rule 1: Distinct Hospitals (SP)
            if (q.includes("quantos hospitais") || q.includes("hospitais distintos") || q.includes("lista de hospitais")) {
                return {
                    type: 'hospitals',
                    sql: `SELECT hospital_nome as Hospital, cnes as CNES, hospital_municipio_nome as Cidade, hospital_uf as UF \nFROM master_healthcare \nWHERE hospital_uf = 'SP'\nGROUP BY ALL \nORDER BY hospital_nome`,
                    narrative: `Foram identificados ${dbData.hospitals.length} estabelecimentos de saúde distintos cadastrados e mapeados no banco de dados do SUS em São Paulo para esta competência.`,
                    data: dbData.hospitals
                };
            }

            // Rule 2: Cataract Surgeries (SP)
            if (q.includes("volume") || q.includes("cirurgias") || q.includes("catarata") || q.includes("quantidade")) {
                return {
                    type: 'catarata',
                    sql: `SELECT \n  hospital_nome as Hospital, \n  COUNT(*) as "Volume de Cirurgias", \n  ROUND(SUM(valor_total), 2) as "Faturamento (R$)",\n  ROUND(AVG(valor_total), 2) as "Custo Médio (R$)"\nFROM master_healthcare \nWHERE hospital_uf = 'SP' AND procedimento_codigo LIKE '040505%'\nGROUP BY hospital_nome\nORDER BY "Volume de Cirurgias" DESC`,
                    narrative: `Foram realizadas 14.890 cirurgias de catarata no total. O estabelecimento líder em volume é o AME AMBULATORIO MEDICO DE ESPECIALIDADES DE CAMPINAS, com 1.160 cirurgias (7,8% de market share), seguido de perto pelo HOFTALMED, com 980 cirurgias (6,6%). Isso demonstra uma distribuição mais descentralizada dos serviços em comparação a estados menores.`,
                    data: dbData.catarata
                };
            }

            // Rule 3: Revenue / Costs (SP)
            if (q.includes("faturamento") || q.includes("receita") || q.includes("valores") || q.includes("quanto custou") || q.includes("custo")) {
                return {
                    type: 'faturamento',
                    sql: `SELECT \n  hospital_nome as Hospital, \n  ROUND(SUM(valor_total), 2) as "Faturamento Total (R$)", \n  COUNT(*) as "Total de Procedimentos"\nFROM master_healthcare \nWHERE hospital_uf = 'SP'\nGROUP BY hospital_nome \nORDER BY "Faturamento Total (R$)" DESC`,
                    narrative: `O faturamento total em saúde identificado no estado de São Paulo foi de R$ 398.828.754,22. O hospital com maior receita captada foi o HOSPITAL DE BASE DE SAO JOSE DO RIO PRETO, captando R$ 15.910.412,46 (4,0% do faturamento estadual). O segundo colocado é o HC DA FMUSP HOSPITAL DAS CLINICAS SAO PAULO, com R$ 15.249.848,25 (3,8%).`,
                    data: dbData.faturamento
                };
            }

            // Rule 4: Underserved municipalities (SP)
            if (q.includes("municipio") || q.includes("municípios") || q.includes("cidade") || q.includes("carente") || q.includes("atendimento")) {
                return {
                    type: 'municipios',
                    sql: `SELECT \n  m.nome as "Município do Paciente", \n  m.uf as UF, \n  COALESCE(COUNT(h.cnes), 0) as "Pacientes Atendidos"\nFROM clean_ibge m \nLEFT JOIN master_healthcare h ON m.municipio_id = h.paciente_municipio_id AND h.procedimento_codigo LIKE '040505%' AND h.hospital_uf = 'SP'\nWHERE m.uf = 'SP'\nGROUP BY m.nome, m.uf \nORDER BY "Pacientes Atendidos" DESC \nLIMIT 15`,
                    narrative: `Análise de cobertura geográfica: identificamos 88 municípios de São Paulo com volume ZERO de pacientes atendidos para cirurgias de catarata para seus residentes nesta competência. Isso aponta para a necessidade de melhorias de acesso regional, mesmo em um estado com alta densidade de serviços.`,
                    data: dbData.municipios
                };
            }

            // Rule 5: Length of Stay (SP)
            if (q.includes("permanencia") || q.includes("internação") || q.includes("tempo") || q.includes("dias")) {
                return {
                    type: 'permanencia',
                    sql: `SELECT \n  hospital_nome as Hospital, \n  ROUND(AVG(dias_permanencia), 1) as "Média de Permanência (dias)", \n  COUNT(*) as "Total de Altas"\nFROM master_healthcare \nWHERE hospital_uf = 'SP'\nGROUP BY hospital_nome \nORDER BY "Média de Permanência (dias)" DESC`,
                    narrative: `A média geral de permanência dos pacientes internados em São Paulo é de 4,9 dias. O maior tempo médio de internação foi de 31,0 dias, registrado em instituições especializadas de longa permanência como a CASA TRANSITORIA ANDRE LUIZ e o LAR ESPIRITA MARIA DE NAZARE MOJI MIRIM.`,
                    data: dbData.permanencia
                };
            }

            // Fallback default (SP)
            return {
                type: 'fallback',
                sql: `SELECT \n  hospital_nome as Hospital, \n  COUNT(*) as "Procedimentos", \n  ROUND(SUM(valor_total), 2) as "Faturamento (R$)" \nFROM master_healthcare \nWHERE hospital_uf = 'SP'\nGROUP BY hospital_nome \nORDER BY "Procedimentos" DESC`,
                narrative: `Consulta geral do Data Lakehouse executada com sucesso. Foram retornados dados de faturamento e volume agregados por hospital no estado de São Paulo. O Hospital de Base de São José do Rio Preto lidera em faturamento geral com R$ 15.910.412,46.`,
                data: dbData.fallback
            };
        } else {
            // Rule 1: Distinct Hospitals (AC)
            if (q.includes("quantos hospitais") || q.includes("hospitais distintos") || q.includes("lista de hospitais")) {
                return {
                    type: 'hospitals',
                    sql: `SELECT hospital_nome as Hospital, cnes as CNES, hospital_municipio_nome as Cidade, hospital_uf as UF \nFROM master_healthcare \nGROUP BY ALL \nORDER BY hospital_nome`,
                    narrative: `Foram identificados ${dbData.hospitals.length} estabelecimentos de saúde distintos cadastrados e mapeados no banco de dados do SUS no Acre para esta competência.`,
                    data: dbData.hospitals
                };
            }

            // Rule 2: Cataract Surgeries (AC)
            if (q.includes("volume") || q.includes("cirurgias") || q.includes("catarata") || q.includes("quantidade")) {
                return {
                    type: 'catarata',
                    sql: `SELECT \n  hospital_nome as Hospital, \n  COUNT(*) as "Volume de Cirurgias", \n  ROUND(SUM(valor_total), 2) as "Faturamento (R$)",\n  ROUND(AVG(valor_total), 2) as "Custo Médio (R$)"\nFROM master_healthcare \nWHERE procedimento_codigo LIKE '040505%'\nGROUP BY hospital_nome\nORDER BY "Volume de Cirurgias" DESC`,
                    narrative: `Foram realizadas 346 cirurgias de catarata no total. O estabelecimento líder absoluto em volume é o HOA HOSPITAL OFTALMOLOGICO DO ACRE LTDA FILIAL, com 346 cirurgias realizadas (100% de market share). Isso demonstra uma centralização total do serviço de oftalmologia cirúrgica de média complexidade pelo SUS na capital Rio Branco.`,
                    data: dbData.catarata
                };
            }

            // Rule 3: Revenue / Costs (AC)
            if (q.includes("faturamento") || q.includes("receita") || q.includes("valores") || q.includes("quanto custou") || q.includes("custo")) {
                return {
                    type: 'faturamento',
                    sql: `SELECT \n  hospital_nome as Hospital, \n  ROUND(SUM(valor_total), 2) as "Faturamento Total (R$)", \n  COUNT(*) as "Total de Procedimentos"\nFROM master_healthcare \nGROUP BY hospital_nome \nORDER BY "Faturamento Total (R$)" DESC`,
                    narrative: `O faturamento total em saúde identificado no estado do Acre foi de R$ 9.697.801,65. O hospital com maior receita captada foi a FUNDHACRE (Fundação Hospital Estadual do Acre), captando R$ 3.279.591,25 (33.8% do faturamento estadual). O segundo colocado é o Hospital Geral de Clínicas de Rio Branco, com R$ 1.477.628,69.`,
                    data: dbData.faturamento
                };
            }

            // Rule 4: Underserved municipalities (AC)
            if (q.includes("municipio") || q.includes("municípios") || q.includes("cidade") || q.includes("carente") || q.includes("atendimento")) {
                return {
                    type: 'municipios',
                    sql: `SELECT \n  m.nome as "Município do Paciente", \n  m.uf as UF, \n  COALESCE(COUNT(h.cnes), 0) as "Pacientes Atendidos"\nFROM clean_ibge m \nLEFT JOIN master_healthcare h ON m.municipio_id = h.paciente_municipio_id AND h.procedimento_codigo LIKE '040505%'\nGROUP BY m.nome, m.uf \nORDER BY "Pacientes Atendidos" ASC \nLIMIT 15`,
                    narrative: `Análise de cobertura geográfica: identificamos 7 municípios do Acre com volume ZERO de pacientes atendidos para cirurgias de catarata (ex: Plácido de Castro, Porto Acre, Rodrigues Alves, Assis Brasil, Epitaciolândia). Isso aponta para graves problemas de acesso a serviços de oftalmologia cirúrgica nas fronteiras e áreas rurais, exigindo mutirões ou redes de transporte eletivo.`,
                    data: dbData.municipios
                };
            }

            // Rule 5: Length of Stay (AC)
            if (q.includes("permanencia") || q.includes("internação") || q.includes("tempo") || q.includes("dias")) {
                return {
                    type: 'permanencia',
                    sql: `SELECT \n  hospital_nome as Hospital, \n  ROUND(AVG(dias_permanencia), 1) as "Média de Permanência (dias)", \n  COUNT(*) as "Total de Altas"\nFROM master_healthcare \nGROUP BY hospital_nome \nORDER BY "Média de Permanência (dias)" DESC`,
                    narrative: `A média geral de permanência dos pacientes internados varia drasticamente. O maior tempo médio de internação foi registrado no Hospital Infantil Iolanda Costa e Silva, com 8.4 dias por paciente, seguido pelo Hospital de Saúde Mental do Acre, com 3.2 dias. Esses valores refletem a complexidade clínica de pediatria e saúde mental, enquanto procedimentos cirúrgicos gerais registram médias inferiores a 1 dia.`,
                    data: dbData.permanencia
                };
            }

            // Fallback default (AC)
            return {
                type: 'fallback',
                sql: `SELECT \n  hospital_nome as Hospital, \n  COUNT(*) as "Procedimentos", \n  ROUND(SUM(valor_total), 2) as "Faturamento (R$)" \nFROM master_healthcare \nGROUP BY hospital_nome \nORDER BY "Procedimentos" DESC`,
                narrative: `Consulta geral do Data Lakehouse executada com sucesso. Foram retornados dados de faturamento e volume agregados por hospital no estado do Acre. O Hospital Geral de Clínicas lidera em volume de atendimentos gerais com 14.832 procedimentos realizados, embora possua ticket médio inferior ao de hospitais de alta complexidade como a FUNDHACRE.`,
                data: dbData.fallback
            };
        }
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
            // Show volume distribution (Pie Chart) - optimized to show top 5 and group other as "Outros"
            const subset = data.slice(0, 5);
            chartData.labels = subset.map(r => r.Hospital || r.hospital_nome || 'Outros');
            if (data.length > 5) {
                chartData.labels.push('Outros');
            }
            const volumes = subset.map(r => r['Volume de Cirurgias'] || r.procedure_volume || 0);
            if (data.length > 5) {
                const othersVol = data.slice(5).reduce((acc, curr) => acc + (curr['Volume de Cirurgias'] || curr.procedure_volume || 0), 0);
                volumes.push(othersVol);
            }
            chartData.datasets = [{
                label: 'Volume de Cirurgias',
                data: volumes,
                backgroundColor: ['#ff9f0a', '#00d2ff', '#30d158', '#ff453a', '#bf5af2', '#aeaeae'],
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

    // Trigger default query on load
    input.value = "Volume de cirurgias de catarata por hospital?";
    form.dispatchEvent(new Event('submit'));
});
