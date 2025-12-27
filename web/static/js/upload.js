let observationCount = 1;

// Add new observation form
function addObservation() {
    const container = document.getElementById('observationsContainer');
    const newIndex = observationCount++;
    
    const observationDiv = document.createElement('div');
    observationDiv.className = 'observation-item';
    observationDiv.dataset.index = newIndex;
    
    observationDiv.innerHTML = `
        <div class="observation-header">
            <span class="observation-number">Observation #${newIndex + 1}</span>
            <button type="button" class="remove-observation" onclick="removeObservation(${newIndex})">×</button>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Time (UTC)</label>
                <input type="datetime-local" name="obs_time_${newIndex}" required>
            </div>
            <div class="form-group">
                <label>RA (degrees)</label>
                <input type="number" name="ra_deg_${newIndex}" step="0.000001" required placeholder="0-360">
            </div>
            <div class="form-group">
                <label>Dec (degrees)</label>
                <input type="number" name="dec_deg_${newIndex}" step="0.000001" required placeholder="-90 to 90">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Station</label>
                <input type="text" name="station_${newIndex}" value="500" required>
            </div>
            <div class="form-group">
                <label>Catalog</label>
                <select name="catalog_${newIndex}" required>
                    <option value="Gaia2">Gaia DR2</option>
                    <option value="Gaia3">Gaia DR3</option>
                    <option value="UCAC4">UCAC4</option>
                </select>
            </div>
        </div>
    `;
    
    container.appendChild(observationDiv);
}

// Remove observation
function removeObservation(index) {
    const item = document.querySelector(`.observation-item[data-index="${index}"]`);
    if (item && document.querySelectorAll('.observation-item').length > 1) {
        item.remove();
    } else {
        showNotification('Need at least one observation', 'warning');
    }
}

// Handle form submission
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const objectName = formData.get('object_name');
        
        // Collect observations
        const observations = [];
        const items = document.querySelectorAll('.observation-item');
        
        items.forEach((item, idx) => {
            const index = item.dataset.index || idx;
            observations.push({
                obs_time: formData.get(`obs_time_${index}`) + ':00.000Z',
                ra_deg: parseFloat(formData.get(`ra_deg_${index}`)),
                dec_deg: parseFloat(formData.get(`dec_deg_${index}`)),
                station: formData.get(`station_${index}`),
                catalog: formData.get(`catalog_${index}`)
            });
        });
        
        if (observations.length < 3) {
            showNotification('Need at least 3 observations', 'warning');
            return;
        }
        
        // Show processing status
        updateStatus('processing', 'Processing observations...');
        
        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    object_name: objectName,
                    observations: observations
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                updateStatus('success', `Successfully processed ${objectName}`);
                displayResults(result);
                showNotification(`Object ${objectName} processed successfully!`, 'low');
            } else {
                updateStatus('error', `Error: ${result.error}`);
                showNotification(`Error: ${result.error}`, 'high');
            }
        } catch (error) {
            updateStatus('error', `Network error: ${error.message}`);
            showNotification('Network error occurred', 'high');
        }
    });
});

// Update processing status
function updateStatus(type, message) {
    const statusBox = document.getElementById('processingStatus');
    if (!statusBox) return;
    
    statusBox.className = `status-box ${type}`;
    statusBox.innerHTML = `<p>${message}</p>`;
}

// Display results
function displayResults(result) {
    const container = document.getElementById('resultContainer');
    if (!container) return;
    
    container.style.display = 'block';
    
    // Orbit results
    if (result.orbit) {
        const orbitDiv = document.getElementById('orbitResults');
        orbitDiv.innerHTML = `
            <div class="result-section">
                <h5>Orbital Elements</h5>
                <div class="result-item">
                    <span class="result-label">Semi-major axis (a)</span>
                    <span class="result-value">${result.orbit.a_au.toFixed(4)} AU</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Eccentricity (e)</span>
                    <span class="result-value">${result.orbit.e.toFixed(6)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Inclination (i)</span>
                    <span class="result-value">${result.orbit.i_deg.toFixed(2)}°</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Arg. of perihelion (ω)</span>
                    <span class="result-value">${result.orbit.omega_deg.toFixed(2)}°</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Long. of asc. node (Ω)</span>
                    <span class="result-value">${result.orbit.big_omega_deg.toFixed(2)}°</span>
                </div>
            </div>
        `;
    }
    
    // Risk results
    if (result.risk) {
        const riskDiv = document.getElementById('riskResults');
        riskDiv.innerHTML = `
            <div class="result-section">
                <h5>Risk Assessment</h5>
                <div class="result-item">
                    <span class="result-label">Risk Level</span>
                    <span class="result-value risk-${result.risk.risk_level}">${result.risk.risk_level.toUpperCase()}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">MOID (Earth)</span>
                    <span class="result-value">${result.risk.moid_earth_au.toFixed(6)} AU</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Potential Impact</span>
                    <span class="result-value">${result.risk.potential_impact ? 'Yes ⚠️' : 'No ✓'}</span>
                </div>
            </div>
        `;
    }
}
