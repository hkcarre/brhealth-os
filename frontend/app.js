document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('query-form');
    const input = document.getElementById('question-input');
    const submitBtn = document.getElementById('submit-btn');
    const narrativeOutput = document.getElementById('narrative-output');
    const sqlOutput = document.getElementById('sql-output');
    const tableHead = document.getElementById('table-head');
    const tableBody = document.getElementById('table-body');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const question = input.value.trim();
        if (!question) return;

        // Set Loading State
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span>';
        narrativeOutput.innerHTML = '<span style="color: var(--text-muted)">Analisando dados do Data Lakehouse...</span>';
        sqlOutput.innerHTML = '-- Gerando SQL dialect...';
        
        tableHead.innerHTML = '<th>Dados</th>';
        tableBody.innerHTML = '<tr><td class="empty-state">Buscando resultados...</td></tr>';

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question })
            });

            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status}`);
            }

            const result = await response.json();
            
            // Render Narrative
            narrativeOutput.innerHTML = `<strong>Insight:</strong><br/>${result.narrative}`;
            
            // Render SQL
            sqlOutput.innerHTML = result.sql_executed;

            // Render Table Data
            renderTable(result.data);

        } catch (error) {
            console.error('API Error:', error);
            narrativeOutput.innerHTML = `<span style="color: #ef4444">Falha ao processar a requisição. O agente está offline?</span>`;
            sqlOutput.innerHTML = '-- Erro de conexão';
            tableBody.innerHTML = '<tr><td class="empty-state" style="color: #ef4444">Erro ao carregar dados</td></tr>';
        } finally {
            // Reset Button State
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                Executar
                <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            `;
        }
    });

    // Sidebar navigation logic
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all
            navItems.forEach(nav => nav.classList.remove('active'));
            // Add to clicked
            item.classList.add('active');
            
            // If it's not the first item (Consultar IA), show a message
            if (item.textContent.trim() !== 'Consultar IA') {
                narrativeOutput.innerHTML = `<span style="color: var(--accent-primary)">Módulo '${item.textContent.trim()}' será ativado nas próximas atualizações do MVP.</span>`;
                sqlOutput.innerHTML = '-- Navegação indisponível';
                tableBody.innerHTML = '<tr><td class="empty-state">Módulo em desenvolvimento</td></tr>';
            } else {
                narrativeOutput.innerHTML = 'Aguardando consulta...';
                sqlOutput.innerHTML = '-- Nenhuma query executada';
                tableBody.innerHTML = '<tr><td class="empty-state">Execute uma pergunta para ver os dados</td></tr>';
            }
        });
    });

    function renderTable(dataArray) {
        if (!dataArray || dataArray.length === 0) {
            tableHead.innerHTML = '<th>Dados</th>';
            tableBody.innerHTML = '<tr><td class="empty-state">Nenhum dado retornado</td></tr>';
            return;
        }

        // Get headers from first object keys
        const headers = Object.keys(dataArray[0]);
        
        // Build Header Row
        let headerHtml = '';
        headers.forEach(h => {
            // Format column names (e.g., canonical_name -> Canonical Name)
            const formattedHeader = h.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
            headerHtml += `<th>${formattedHeader}</th>`;
        });
        tableHead.innerHTML = headerHtml;

        // Build Body Rows
        let bodyHtml = '';
        dataArray.forEach(row => {
            bodyHtml += '<tr>';
            headers.forEach(h => {
                bodyHtml += `<td>${row[h]}</td>`;
            });
            bodyHtml += '</tr>';
        });
        tableBody.innerHTML = bodyHtml;
    }
});
