/* ─────────────────────────────────────────
   OS Algorithm Solver — Frontend JS
───────────────────────────────────────── */

let currentType = null;
let rowCount = 1;

// ── TYPE SELECTION ──────────────────────

function selectType(type) {
  currentType = type;

  // highlight active button
  ['cpu', 'memory', 'disk'].forEach(t => {
    document.getElementById(`btn-${t}`).classList.toggle('active', t === type);
  });

  // hide all sub-forms, show the right one
  ['cpu', 'memory', 'disk'].forEach(t => {
    document.getElementById(`form-${t}`).classList.add('hidden');
  });
  document.getElementById(`form-${type}`).classList.remove('hidden');

  // show step 2
  document.getElementById('step2').classList.remove('hidden');
  document.getElementById('step2').scrollIntoView({ behavior: 'smooth', block: 'start' });

  // hide old result
  document.getElementById('step3').classList.add('hidden');
}

// ── CPU PROCESS ROWS ────────────────────

function addRow() {
  rowCount++;
  const container = document.getElementById('cpu-rows');
  const div = document.createElement('div');
  div.className = 'process-row';
  div.dataset.idx = rowCount - 1;
  div.innerHTML = `
    <span class="pid-label">P${rowCount}</span>
    <label>Arrival<input type="number" class="arr" min="0" value="0"/></label>
    <label>Burst<input type="number" class="bst" min="1" value="3"/></label>
    <button class="remove-btn" onclick="removeRow(this)">✕</button>
  `;
  container.appendChild(div);
}

function removeRow(btn) {
  const rows = document.querySelectorAll('#cpu-rows .process-row');
  if (rows.length <= 1) { alert('Need at least one process.'); return; }
  btn.closest('.process-row').remove();
  // re-label remaining rows
  document.querySelectorAll('#cpu-rows .process-row').forEach((row, i) => {
    row.querySelector('.pid-label').textContent = `P${i + 1}`;
  });
}

// ── SOLVE ───────────────────────────────

async function solve() {
  if (!currentType) { alert('Please select a problem type first.'); return; }

  let payload = { type: currentType };

  if (currentType === 'cpu') {
    const rows = document.querySelectorAll('#cpu-rows .process-row');
    const processes = [];
    for (const row of rows) {
      const arrival = parseInt(row.querySelector('.arr').value) || 0;
      const burst   = parseInt(row.querySelector('.bst').value) || 1;
      processes.push({ arrival, burst });
    }
    payload.processes = processes;
    payload.quantum   = parseInt(document.getElementById('quantum').value) || 0;

  } else if (currentType === 'memory') {
    payload.pages  = document.getElementById('pages').value.trim();
    payload.frames = parseInt(document.getElementById('frames').value) || 3;

  } else if (currentType === 'disk') {
    payload.requests = document.getElementById('requests').value.trim();
    payload.head     = parseInt(document.getElementById('head').value) || 0;
  }

  // show loading
  const step3 = document.getElementById('step3');
  const output = document.getElementById('output');
  step3.classList.remove('hidden');
  output.innerHTML = '<p style="color:var(--muted);font-family:var(--mono);font-size:.85rem">Computing…</p>';
  step3.scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const res  = await fetch('/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.error) {
      output.innerHTML = `<div class="error-box">⚠ ${data.error}</div>`;
      return;
    }

    output.innerHTML = renderResult(data);

  } catch (err) {
    output.innerHTML = `<div class="error-box">⚠ Network error: ${err.message}</div>`;
  }
}

// ── RENDER RESULT ────────────────────────

function renderResult(d) {
  let html = '';

  // Algorithm name badge
  html += `<div class="algo-badge">✦ ${d.algorithm}</div>`;

  // Explanation grid
  html += `
  <div class="info-grid">
    <div class="info-box why">
      <div class="info-title">Why this algorithm?</div>
      <p>${d.why}</p>
    </div>
    <div class="info-box what">
      <div class="info-title">What does it do?</div>
      <p>${d.what}</p>
    </div>
    <div class="info-box others">
      <div class="info-title">Why not the others?</div>
      <p>${d.others}</p>
    </div>
  </div>`;

  // Type-specific output
  if (d.type === 'cpu_table') {
    html += renderCpuTable(d);
  } else if (d.type === 'cpu_rr') {
    html += renderCpuRR(d);
  } else if (d.type === 'memory') {
    html += renderMemory(d);
  } else if (d.type === 'disk') {
    html += renderDisk(d);
  }

  return html;
}

// ── CPU TABLE (FCFS / SJF) ───────────────

function renderCpuTable(d) {
  let html = `
  <div class="stats-row">
    <div class="stat-chip"><div class="sv">${d.avg_wait}</div><div class="sl">Avg Wait (ms)</div></div>
    <div class="stat-chip"><div class="sv">${d.avg_turnaround}</div><div class="sl">Avg Turnaround (ms)</div></div>
    <div class="stat-chip"><div class="sv">${d.steps.length}</div><div class="sl">Processes</div></div>
  </div>`;

  // Gantt chart
  html += `<div class="gantt-wrap"><div class="gantt-title">Gantt Chart</div><div class="gantt">`;
  d.steps.forEach(s => {
    html += `<div class="gantt-block">
      <div class="gantt-bar">${s.pid}</div>
      <div class="gantt-time">${s.start}–${s.finish}</div>
    </div>`;
  });
  html += '</div></div>';

  // Table
  html += `
  <div class="tbl-wrap">
  <table>
    <thead><tr>
      <th>Process</th><th>Arrival</th><th>Burst</th>
      <th>Start</th><th>Finish</th><th>Waiting</th><th>Turnaround</th>
    </tr></thead>
    <tbody>`;
  d.steps.forEach(s => {
    html += `<tr>
      <td>${s.pid}</td><td>${s.arrival}</td><td>${s.burst}</td>
      <td>${s.start}</td><td>${s.finish}</td>
      <td style="color:var(--accent)">${s.waiting}</td>
      <td style="color:var(--accent2)">${s.turnaround}</td>
    </tr>`;
  });
  html += '</tbody></table></div>';
  return html;
}

// ── CPU ROUND ROBIN ──────────────────────

function renderCpuRR(d) {
  let html = `
  <div class="stats-row">
    <div class="stat-chip"><div class="sv">${d.avg_wait}</div><div class="sl">Avg Wait (ms)</div></div>
    <div class="stat-chip"><div class="sv">${d.avg_turnaround}</div><div class="sl">Avg Turnaround</div></div>
    <div class="stat-chip"><div class="sv">${d.quantum}</div><div class="sl">Quantum</div></div>
    <div class="stat-chip"><div class="sv">${d.timeline.length}</div><div class="sl">Time Slices</div></div>
  </div>`;

  // Gantt
  const colors = ['#f5a623','#4fc3f7','#66bb6a','#ce93d8','#ef9a9a','#80cbc4','#ffcc80'];
  const pidColor = {};
  let ci = 0;
  html += `<div class="gantt-wrap"><div class="gantt-title">Gantt Chart (time slices)</div><div class="gantt">`;
  d.timeline.forEach(s => {
    if (!pidColor[s.pid]) pidColor[s.pid] = colors[ci++ % colors.length];
    html += `<div class="gantt-block">
      <div class="gantt-bar" style="background:${pidColor[s.pid]};min-width:${Math.max(42, s.ran * 14)}px">${s.pid}</div>
      <div class="gantt-time">${s.start}–${s.end}</div>
    </div>`;
  });
  html += '</div></div>';

  // Summary table
  html += `<div class="tbl-wrap"><table>
    <thead><tr><th>Process</th><th>Arrival</th><th>Burst</th><th>Finish</th><th>Waiting</th><th>Turnaround</th></tr></thead>
    <tbody>`;
  d.steps.forEach(s => {
    html += `<tr>
      <td>${s.pid}</td><td>${s.arrival}</td><td>${s.burst}</td><td>${s.finish}</td>
      <td style="color:var(--accent)">${s.waiting}</td>
      <td style="color:var(--accent2)">${s.turnaround}</td>
    </tr>`;
  });
  html += '</tbody></table></div>';
  return html;
}

// ── MEMORY ───────────────────────────────

function renderMemory(d) {
  const hitRate = ((d.hits / d.total) * 100).toFixed(1);
  let html = `
  <div class="stats-row">
    <div class="stat-chip"><div class="sv" style="color:var(--red)">${d.faults}</div><div class="sl">Page Faults</div></div>
    <div class="stat-chip"><div class="sv" style="color:var(--green)">${d.hits}</div><div class="sl">Page Hits</div></div>
    <div class="stat-chip"><div class="sv">${d.total}</div><div class="sl">Total Refs</div></div>
    <div class="stat-chip"><div class="sv">${hitRate}%</div><div class="sl">Hit Rate</div></div>
  </div>`;

  const frameHeaders = Array.from({length: d.frames}, (_, i) => `<th>Frame ${i+1}</th>`).join('');
  html += `<div class="tbl-wrap"><table>
    <thead><tr><th>Ref</th>${frameHeaders}<th>Status</th><th>Evicted</th></tr></thead>
    <tbody>`;

  d.steps.forEach(s => {
    const cells = Array.from({length: d.frames}, (_, i) =>
      `<td>${s.memory[i] !== undefined ? s.memory[i] : '—'}</td>`
    ).join('');
    const status = s.fault
      ? '<span class="fault">FAULT</span>'
      : '<span class="hit">HIT</span>';
    const evicted = s.evicted !== null && s.evicted !== undefined ? s.evicted : '—';
    html += `<tr><td style="color:var(--accent);font-weight:700">${s.page}</td>${cells}<td>${status}</td><td>${evicted}</td></tr>`;
  });
  html += '</tbody></table></div>';
  return html;
}

// ── DISK ─────────────────────────────────

function renderDisk(d) {
  let html = `
  <div class="stats-row">
    <div class="stat-chip"><div class="sv" style="color:var(--accent)">${d.total_seek}</div><div class="sl">Total Seek Distance</div></div>
    <div class="stat-chip"><div class="sv">${d.head}</div><div class="sl">Initial Head</div></div>
    <div class="stat-chip"><div class="sv">${d.requests.length}</div><div class="sl">Requests</div></div>
  </div>`;

  html += `<div class="tbl-wrap"><table>
    <thead><tr><th>Step</th><th>From</th><th>To</th><th>Seek Distance</th></tr></thead>
    <tbody>`;
  d.steps.forEach((s, i) => {
    html += `<tr>
      <td>${i + 1}</td>
      <td style="color:var(--muted)">${s.from}</td>
      <td style="color:var(--accent2)">${s.to}</td>
      <td style="color:var(--accent)">${s.seek}</td>
    </tr>`;
  });
  html += `<tr style="border-top:2px solid var(--border)">
    <td colspan="3" style="text-align:right;color:var(--muted);font-family:var(--mono)">Total Seek Distance</td>
    <td style="color:var(--accent);font-weight:700;font-family:var(--mono)">${d.total_seek}</td>
  </tr>`;
  html += '</tbody></table></div>';
  return html;
}
