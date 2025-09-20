async function api(path, opts={}) {
  const res = await fetch(path, {headers: {'Content-Type': 'application/json'}, ...opts});
  const data = await res.json().catch(()=>({error:'Invalid JSON'}));
  if (!res.ok) throw new Error(data?.error || res.statusText);
  return data;
}

function statusBadge(status) {
  const map = { 'New':'badge new', 'Updated':'badge updated', 'Action Required':'badge action' };
  return `<span class="${map[status]||'badge'}">${status}</span>`;
}

function cardHTML(p) {
  const pub = p.publication_date ? new Date(p.publication_date).toLocaleString() : 'N/A';
  const eff = p.effective_date ? new Date(p.effective_date).toLocaleDateString() : '—';
  return `
  <div class="card">
    <h3>${p.title}</h3>
    <div class="meta">${p.ministry} • ${pub}</div>
    <div class="badges">${statusBadge(p.status)}</div>
    <div class="details">
      <p><strong>What changed:</strong> ${p.details?.what_changed || '—'}</p>
      <p><strong>Who it affects:</strong> ${p.details?.who_affected || '—'}</p>
      <p><strong>What to do:</strong> ${p.details?.what_to_do || '—'}</p>
      <p><strong>Summary (EN):</strong> ${p.summary?.english || '—'}</p>
      <p><strong>Summary (NE):</strong> ${p.summary?.nepali || '—'}</p>
      <p class="source"><strong>Source:</strong> ${p.source_url ? `<a href="${p.source_url}" target="_blank">link</a>` : '—'}</p>
      <div class="gaps">
        <strong>Gaps:</strong>
        <span class="badge ${p.operational_gaps?.missing_dates?'action':''}">Missing dates: ${p.operational_gaps?.missing_dates? 'Yes':'No'}</span>
        <span class="badge ${p.operational_gaps?.missing_officer_info?'action':''}">Officer info: ${p.operational_gaps?.missing_officer_info? 'Missing':'Present'}</span>
        <span class="badge ${p.operational_gaps?.missing_urls?'action':''}">URLs: ${p.operational_gaps?.missing_urls? 'Missing':'Present'}</span>
      </div>
    </div>
  </div>`;
}

async function loadRecent(days=7){
  const cardsEl = document.getElementById('cards');
  cardsEl.innerHTML = '<div class="loading">Loading recent policies…</div>';
  try {
    const data = await api(`/api/policies/recent?days=${days}`);
    if (!data.policies?.length) {
      cardsEl.innerHTML = '<div>No policies found. Try Refresh Live.</div>';
      return;
    }
    cardsEl.innerHTML = data.policies.map(cardHTML).join('');
  } catch (e) {
    cardsEl.innerHTML = `<div class="error">${e.message}</div>`;
  }
}

async function refreshAll(){
  const btn = document.getElementById('btn-refresh');
  btn.disabled = true; btn.textContent = 'Refreshing…';
  try {
    const res = await api('/api/policies/refresh-all', {method:'POST'});
    alert(`Processed ${res.policies_processed} policies via live scraping + Gemini.`);
    await loadRecent(7);
  } catch(e){
    alert('Refresh failed: '+e.message);
  } finally {
    btn.disabled = false; btn.textContent = 'Refresh Live (Scrape + Gemini)';
  }
}

async function analyzeLive(){
  const url = document.getElementById('policy-url').value.trim();
  const text = document.getElementById('policy-text').value.trim();
  const title = document.getElementById('policy-title').value.trim();
  const ministry = document.getElementById('policy-ministry').value.trim();
  const out = document.getElementById('live-output');
  out.textContent = 'Analyzing…';
  const payload = url ? {source_url:url, metadata:{title, ministry}} : {policy_text:text, metadata:{title, ministry}};
  try {
    const res = await api('/api/policies/analyze-live', {method:'POST', body: JSON.stringify(payload)});
    out.textContent = JSON.stringify(res, null, 2);
  } catch(e){
    out.textContent = 'Error: '+e.message;
  }
}

async function verifySources(){
  const out = document.getElementById('live-output');
  out.textContent = 'Verifying sources…';
  try {
    const res = await api('/api/policies/verify-data-sources');
    out.textContent = JSON.stringify(res, null, 2);
  } catch(e){
    out.textContent = 'Error: '+e.message;
  }
}

// --- RTI Module Client ---
let RTI_STATE = { complaintId: null, rtiId: null };

async function rtiSubmit(){
  const url = document.getElementById('rti-url').value.trim();
  const complaint = document.getElementById('rti-complaint').value.trim();
  const out = document.getElementById('rti-output');
  out.textContent = 'Submitting complaint…';
  try{
    const res = await api('/api/rti/submit-complaint', {method:'POST', body: JSON.stringify({url, complaint})});
    RTI_STATE.complaintId = res.id;
    out.textContent = JSON.stringify(res, null, 2);
  }catch(e){ out.textContent = 'Error: '+e.message; }
}

async function rtiValidate(){
  const out = document.getElementById('rti-output');
  if (!RTI_STATE.complaintId){ out.textContent = 'Submit a complaint first.'; return; }
  out.textContent = 'Validating…';
  try{
    const res = await api(`/api/rti/validate/${RTI_STATE.complaintId}`);
    out.textContent = JSON.stringify(res, null, 2);
  }catch(e){ out.textContent = 'Error: '+e.message; }
}

async function rtiGenerate(){
  const out = document.getElementById('rti-output');
  if (!RTI_STATE.complaintId){ out.textContent = 'Submit a complaint first.'; return; }
  out.textContent = 'Generating RTI…';
  try{
    const res = await api(`/api/rti/generate/${RTI_STATE.complaintId}`, {method:'POST'});
    RTI_STATE.rtiId = res.rti_id;
    out.textContent = JSON.stringify(res, null, 2);
  }catch(e){ out.textContent = 'Error: '+e.message; }
}

async function rtiDownload(){
  const out = document.getElementById('rti-output');
  if (!RTI_STATE.rtiId){ out.textContent = 'Generate the RTI first.'; return; }
  try{
    window.location.href = `/api/rti/download/${RTI_STATE.rtiId}`;
  }catch(e){ out.textContent = 'Error: '+e.message; }
}

// Bindings
window.addEventListener('DOMContentLoaded', ()=>{
  document.getElementById('btn-analyze').addEventListener('click', analyzeLive);
  document.getElementById('btn-recent').addEventListener('click', ()=>loadRecent(7));
  document.getElementById('btn-refresh').addEventListener('click', refreshAll);
  document.getElementById('btn-verify').addEventListener('click', verifySources);
  document.getElementById('btn-rti-submit').addEventListener('click', rtiSubmit);
  document.getElementById('btn-rti-validate').addEventListener('click', rtiValidate);
  document.getElementById('btn-rti-generate').addEventListener('click', rtiGenerate);
  document.getElementById('btn-rti-download').addEventListener('click', rtiDownload);
  // Load immediately
  loadRecent(7);
});
