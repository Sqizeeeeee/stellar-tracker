// Получаем лимит из шаблона
const CSV_CLIENT_PARSE_LIMIT = parseInt(document.body.dataset.csvLimit) || 15;

let csvData = [];
let observationCount = 1;


async function sendMetric(eventName, eventData = {}) {
    try {
        // Отправляем событие на backend для логирования
        await fetch('/api/metrics/event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event: eventName,
                timestamp: new Date().toISOString(),
                ...eventData
            })
        });
    } catch (error) {
        console.warn('Failed to send metric:', error);
    }
}

// Переключение табов
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        

        sendMetric('tab_switched', { tab: tab });
        
        // Переключаем активные табы
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`${tab}-tab`).classList.add('active');
    });
});

// CSV Upload - Drag & Drop
const dropzone = document.getElementById('dropzone');
const csvFileInput = document.getElementById('csvFile');

if (dropzone && csvFileInput) {
    dropzone.addEventListener('click', () => {
        sendMetric('dropzone_clicked');
        csvFileInput.click();
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.csv')) {
            sendMetric('file_dropped', { fileName: file.name, fileSize: file.size });
            handleCsvFile(file);
        } else {
            sendMetric('invalid_file_dropped', { fileName: file?.name });
            alert('Please upload a CSV file');
        }
    });

    csvFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            sendMetric('file_selected', { fileName: file.name, fileSize: file.size });
            handleCsvFile(file);
        }
    });
}

// Обработка CSV файла
function handleCsvFile(file) {
    const reader = new FileReader();
    
    reader.onload = (e) => {
        const text = e.target.result;
        const lines = text.trim().split('\n');
        const rowCount = lines.length - 1; // -1 для header
        
        console.log(`CSV file: ${rowCount} observations`);
        

        sendMetric('csv_file_loaded', { 
            observations: rowCount,
            parseMethod: rowCount <= CSV_CLIENT_PARSE_LIMIT ? 'client' : 'server'
        });
        
        // Проверяем лимит
        if (rowCount <= CSV_CLIENT_PARSE_LIMIT) {
            // Маленький файл - парсим на клиенте
            parseCSVClient(text);
        } else {
            // Большой файл - отправляем на сервер
            parseCSVServer(file);
        }
    };
    
    reader.readAsText(file);
}

// Парсинг на клиенте (для маленьких файлов)
function parseCSVClient(csvText) {
    console.log('Parsing on client...');
    const startTime = performance.now();
    
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    
    csvData = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        const obs = {
            obs_time: values[0],
            ra_deg: parseFloat(values[1]),
            dec_deg: parseFloat(values[2]),
            station: values[3] || '500',
            catalog: values[4] || 'Gaia2'
        };
        csvData.push(obs);
    }
    
    const parseTime = performance.now() - startTime;
    

    sendMetric('csv_parsed_client', {
        observations: csvData.length,
        parseTime: parseTime
    });
    
    displayCSVPreview();
}

// Парсинг на сервере (для больших файлов)
async function parseCSVServer(file) {
    console.log('Parsing on server...');
    const startTime = performance.now();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/parse-csv', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        const parseTime = performance.now() - startTime;
        
        if (result.success) {
            csvData = result.observations;
            

            sendMetric('csv_parsed_server', {
                observations: csvData.length,
                parseTime: parseTime,
                hasErrors: result.errors?.length > 0
            });
            
            displayCSVPreview();
        } else {
            sendMetric('csv_parse_error', { error: result.error });
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        sendMetric('csv_parse_error', { error: error.message });
        console.error('Error parsing CSV:', error);
        alert('Failed to parse CSV file');
    }
}

// Отображение preview
function displayCSVPreview() {
    const preview = document.getElementById('csvPreview');
    const table = document.getElementById('csvTable').getElementsByTagName('tbody')[0];
    const count = document.getElementById('csvCount');
    const processBtn = document.getElementById('processCsvBtn');
    
    // Очищаем таблицу
    table.innerHTML = '';
    
    // Заполняем данными (максимум 100 строк для preview)
    const displayLimit = Math.min(csvData.length, 100);
    for (let i = 0; i < displayLimit; i++) {
        const obs = csvData[i];
        const row = table.insertRow();
        
        row.insertCell(0).textContent = obs.obs_time;
        row.insertCell(1).textContent = obs.ra_deg.toFixed(4);
        row.insertCell(2).textContent = obs.dec_deg.toFixed(4);
        row.insertCell(3).textContent = obs.station;
        row.insertCell(4).textContent = obs.catalog;
    }
    
    if (csvData.length > 100) {
        const row = table.insertRow();
        const cell = row.insertCell(0);
        cell.colSpan = 5;
        cell.style.textAlign = 'center';
        cell.style.color = 'var(--text-secondary)';
        cell.textContent = `... and ${csvData.length - 100} more observations`;
    }
    
    count.textContent = csvData.length;
    preview.style.display = 'block';
    processBtn.disabled = false;
}

// Clear CSV
const clearCsvBtn = document.getElementById('clearCsv');
if (clearCsvBtn) {
    clearCsvBtn.addEventListener('click', () => {
        sendMetric('csv_cleared', { observations: csvData.length });
        csvData = [];
        csvFileInput.value = '';
        document.getElementById('csvPreview').style.display = 'none';
        document.getElementById('processCsvBtn').disabled = true;
    });
}

// Process CSV observations
const processCsvBtn = document.getElementById('processCsvBtn');
if (processCsvBtn) {
    processCsvBtn.addEventListener('click', async () => {
        const objectName = document.getElementById('csvObjectName').value.trim();
        
        if (!objectName) {
            sendMetric('process_failed', { reason: 'no_object_name' });
            alert('Please enter object name');
            return;
        }
        
        if (csvData.length === 0) {
            sendMetric('process_failed', { reason: 'no_observations' });
            alert('No observations to process');
            return;
        }
        
        sendMetric('processing_started', {
            objectName: objectName,
            observations: csvData.length
        });
        
        await processObservations(objectName, csvData);
    });
}

// Обработка наблюдений (общая функция)
async function processObservations(objectName, observations) {
    const statusBox = document.getElementById('processingStatus');
    const startTime = performance.now();
    
    statusBox.className = 'status-box processing';
    statusBox.innerHTML = '<p>⏳ Processing observations...</p>';
    
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                object_name: objectName,
                observations: observations
            })
        });
        
        const result = await response.json();
        const processingTime = performance.now() - startTime;
        
        console.log('Full API Response:', result);
        console.log('Orbit data:', result.orbit);
        console.log('Risk data:', result.risk);
        
        if (result.success && result.orbit && result.risk) {
            // Безопасное извлечение значений с fallback
            const semiMajorAU = result.orbit.a_au || result.orbit.a || 0;
            const eccentricity = result.orbit.e || result.orbit.ecc || 0;
            const inclination = result.orbit.i_deg || result.orbit.i || result.orbit.inc || 0;
            
            const riskLevel = result.risk.risk_level || 'unknown';
            const moid = result.risk.moid_earth_au || result.risk.moid || 0;
            

            sendMetric('processing_success', {
                objectName: objectName,
                observations: observations.length,
                processingTime: processingTime,
                riskLevel: riskLevel,
                moid: moid
            });
            
            console.log('Extracted values:', { semiMajorAU, eccentricity, inclination, riskLevel, moid });
            
            statusBox.className = 'status-box success';
            statusBox.innerHTML = `
                <h3>✅ Success!</h3>
                <div class="result-container">
                    <div class="result-section">
                        <h5>Orbit Elements</h5>
                        <div class="result-item">
                            <span class="result-label">Semi-major axis:</span>
                            <span class="result-value">${(semiMajorAU * 149597870.7).toFixed(0)} km (${semiMajorAU.toFixed(6)} AU)</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Eccentricity:</span>
                            <span class="result-value">${eccentricity.toFixed(6)}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">Inclination:</span>
                            <span class="result-value">${inclination.toFixed(2)}°</span>
                        </div>
                    </div>
                    <div class="result-section">
                        <h5>Risk Assessment</h5>
                        <div class="result-item">
                            <span class="result-label">Risk Level:</span>
                            <span class="result-value">${riskLevel.toUpperCase()}</span>
                        </div>
                        <div class="result-item">
                            <span class="result-label">MOID:</span>
                            <span class="result-value">${moid.toFixed(6)} AU</span>
                        </div>
                    </div>
                </div>
            `;
        } else {

            sendMetric('processing_failed', {
                objectName: objectName,
                observations: observations.length,
                processingTime: processingTime,
                error: result.error
            });
            
            statusBox.className = 'status-box error';
            statusBox.innerHTML = `<h3>❌ Error</h3><p>${result.error || 'No orbit data returned'}</p>`;
        }
    } catch (error) {

        sendMetric('processing_error', {
            objectName: objectName,
            observations: observations.length,
            error: error.message
        });
        
        console.error('Error:', error);
        statusBox.className = 'status-box error';
        statusBox.innerHTML = `<h3>❌ Error</h3><p>Failed to process observations: ${error.message}</p>`;
    }
}
