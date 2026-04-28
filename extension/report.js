/**
 * report.js — Prompt Guardian Forensic Report Renderer
 *
 * Reads pg_report_data from chrome.storage.local, populates all
 * {{ PLACEHOLDER }} markers in report.html, and generates the
 * dynamic sections (severity bars, attack table, timeline log, etc.)
 */

// ── HELPERS ──────────────────────────────────────────────────────────────────

function escapeHtml(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function truncate(str, len) {
  if (!str) return '—';
  return str.length > len ? str.slice(0, len) + '...' : str;
}

function formatTimestamp(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleString([], {
    year: 'numeric', month: 'short', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
}

function badgeClass(action) {
  if (action === 'BLOCK') return 'badge-block';
  if (action === 'WARN')  return 'badge-warn';
  return 'badge-allow';
}

function rowClass(action) {
  if (action === 'BLOCK') return 'row-block';
  if (action === 'WARN')  return 'row-warn';
  return '';
}

// ── PLACEHOLDER REPLACEMENT ───────────────────────────────────────────────────

function replacePlaceholders(report) {
  const ss = report.session_summary || {};
  const execPara = `During this session of ${ss.session_duration_minutes || 0} minutes, ` +
    `Prompt Guardian analyzed ${ss.total_prompts_analyzed || 0} prompts, ` +
    `blocked ${ss.threats_blocked || 0} threats (${ss.block_rate_percent || 0}% block rate), ` +
    `and recorded a peak risk score of ${ss.highest_risk_score || 0}%. ` +
    `${ss.user_overrides || 0} manual override(s) were logged by the user.`;

  const map = {
    '{{ REPORT_ID }}':           escapeHtml(report.report_id || '—'),
    '{{ GENERATED_AT }}':        formatTimestamp(report.generated_at),
    '{{ SESSION_START }}':       formatTimestamp(ss.session_start),
    '{{ SESSION_END }}':         formatTimestamp(ss.session_end),
    '{{ SESSION_DURATION }}':    (ss.session_duration_minutes || 0) + ' minutes',
    '{{ TOTAL_PROMPTS }}':       String(ss.total_prompts_analyzed || 0),
    '{{ THREATS_BLOCKED }}':     String(ss.threats_blocked || 0),
    '{{ SAFE_PROMPTS }}':        String(ss.safe_prompts || 0),
    '{{ BLOCK_RATE }}':          (ss.block_rate_percent || 0) + '%',
    '{{ AVG_RISK }}':            (ss.average_risk_score || 0) + '%',
    '{{ PEAK_RISK }}':           (ss.highest_risk_score || 0) + '%',
    '{{ USER_OVERRIDES }}':      String(ss.user_overrides || 0),
    '{{ USER_SANITIZED }}':      String(ss.user_sanitized || 0),
    '{{ EXECUTIVE_PARAGRAPH }}': execPara,
  };

  let html = document.body.innerHTML;
  for (const [placeholder, value] of Object.entries(map)) {
    // Replace all occurrences
    html = html.split(placeholder).join(value);
  }
  document.body.innerHTML = html;

  // Sync print bar report ID (re-query after innerHTML set)
  const barId = document.getElementById('bar-report-id');
  if (barId) barId.textContent = report.report_id || '—';
}

// ── SECTION: SEVERITY BARS ────────────────────────────────────────────────────

function renderSeverityBars(sev) {
  const container = document.getElementById('severity-bars');
  if (!container) return;

  const levels = [
    { key: 'critical', label: 'CRITICAL', color: '#DC2626' },
    { key: 'high',     label: 'HIGH',     color: '#D97706' },
    { key: 'medium',   label: 'MEDIUM',   color: '#1E40AF' },
    { key: 'low',      label: 'LOW',      color: '#6B7280' },
  ];

  const maxVal = Math.max(...levels.map(l => sev[l.key] || 0), 1);

  container.innerHTML = levels.map(l => {
    const count = sev[l.key] || 0;
    const pct   = Math.round((count / maxVal) * 100);
    return `
      <div class="sev-row">
        <span class="sev-label" style="color:${l.color}">${l.label}</span>
        <div class="sev-bar-wrap">
          <div class="sev-bar" style="width:${pct}%;background:${l.color};"></div>
        </div>
        <span class="sev-count" style="color:${l.color}">${count}</span>
      </div>`;
  }).join('');
}

// ── SECTION: ATTACK CATEGORY TABLE ───────────────────────────────────────────

function renderAttackTable(breakdown) {
  const tbody = document.getElementById('attack-category-tbody');
  if (!tbody) return;

  const entries = Object.entries(breakdown || {}).sort((a, b) => b[1].count - a[1].count);
  if (entries.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:#9CA3AF;padding:16px;">No attack categories detected.</td></tr>`;
    return;
  }

  const maxCount = Math.max(...entries.map(e => e[1].count), 1);

  tbody.innerHTML = entries.map(([cat, info]) => {
    const barWidth = Math.round((info.count / maxCount) * 100);
    return `
      <tr>
        <td><strong>${escapeHtml(cat)}</strong></td>
        <td style="font-family:monospace;font-weight:700;">${info.count}</td>
        <td>
          ${info.percentage}%
          <span class="mini-bar-wrap"><span class="mini-bar" style="width:${barWidth}%;"></span></span>
        </td>
        <td style="font-family:monospace;color:#DC2626;">${info.highest_risk}%</td>
      </tr>`;
  }).join('');
}

// ── SECTION: TOP 5 THREATS ────────────────────────────────────────────────────

function renderTopThreats(threats) {
  const container = document.getElementById('top-threats-list');
  if (!container) return;

  if (!threats || threats.length === 0) {
    container.innerHTML = '<p style="color:#9CA3AF;text-align:center;padding:20px;">No high-risk threats in this session.</p>';
    return;
  }

  container.innerHTML = threats.slice(0, 5).map((t, i) => {
    const cls = badgeClass(t.action_taken);
    return `
      <div class="threat-card">
        <div class="threat-card-top">
          <div style="display:flex;align-items:center;">
            <span class="threat-risk-badge">${t.risk_score}%</span>
            <span class="threat-type">${escapeHtml(t.attack_type)}</span>
          </div>
          <span class="threat-ts">${formatTimestamp(t.timestamp)}</span>
        </div>
        <div class="threat-prompt">${escapeHtml(truncate(t.prompt_snippet, 200))}</div>
        <div class="threat-meta">
          Action: <span class="badge ${cls}">${escapeHtml(t.action_taken)}</span>
          &nbsp;&nbsp;User Decision: <strong>${escapeHtml(t.user_decision)}</strong>
        </div>
      </div>`;
  }).join('');
}

// ── SECTION: FULL TIMELINE LOG ────────────────────────────────────────────────

function renderTimeline(events) {
  const tbody = document.getElementById('timeline-log-tbody');
  if (!tbody) return;

  if (!events || events.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#9CA3AF;padding:16px;">No session events recorded.</td></tr>`;
    return;
  }

  tbody.innerHTML = events.map((ev, i) => {
    const rc  = rowClass(ev.action_taken);
    const cls = badgeClass(ev.action_taken);
    return `
      <tr class="${rc}">
        <td style="font-family:monospace;color:#6B7280;">${i + 1}</td>
        <td style="font-family:monospace;font-size:11px;white-space:nowrap;">${formatTimestamp(ev.timestamp)}</td>
        <td style="font-family:monospace;font-size:11px;max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
            title="${escapeHtml(ev.prompt_snippet)}">${escapeHtml(truncate(ev.prompt_snippet, 60))}</td>
        <td style="font-family:monospace;font-weight:700;color:#DC2626;">${ev.risk_score}%</td>
        <td>${escapeHtml(ev.attack_type)}</td>
        <td><span class="badge ${cls}">${escapeHtml(ev.action_taken)}</span></td>
        <td style="color:#6B7280;">${escapeHtml(ev.user_decision)}</td>
      </tr>`;
  }).join('');
}

// ── SECTION: RECOMMENDATIONS ──────────────────────────────────────────────────

function renderRecommendations(recs) {
  const container = document.getElementById('recommendations-list');
  if (!container) return;

  if (!recs || recs.length === 0) {
    container.innerHTML = '<p style="color:#9CA3AF;">No recommendations generated.</p>';
    return;
  }

  container.innerHTML = recs.map(r => `
    <div class="rec-item">
      <span class="rec-check">✓</span>
      <span>${escapeHtml(r)}</span>
    </div>`).join('');
}

// ── SECTION: COMPLIANCE ───────────────────────────────────────────────────────

function renderCompliance(notes) {
  if (!notes) return;

  const owaspEl = document.getElementById('owasp-list');
  if (owaspEl) owaspEl.textContent = notes.owasp_llm_top_10 || '—';

  const mitreEl = document.getElementById('mitre-list');
  if (mitreEl) {
    mitreEl.innerHTML = (notes.mitre_atlas_techniques || [])
      .map(t => `<li>${escapeHtml(t)}</li>`).join('');
  }

  const dhEl = document.getElementById('data-handling');
  if (dhEl) dhEl.textContent = notes.data_handling || '—';

  const atEl = document.getElementById('audit-trail');
  if (atEl) atEl.textContent = notes.audit_trail || '—';
}

// ── SECTION: ENGINE METADATA ──────────────────────────────────────────────────

function renderEngineMetadata(meta) {
  const tbody = document.getElementById('engine-metadata-tbody');
  if (!tbody || !meta) return;

  const rows = [
    ['Detection Layers',     Array.isArray(meta.detection_layers) ? meta.detection_layers.join(' → ') : meta.detection_layers],
    ['Regex Patterns',       meta.regex_patterns_loaded],
    ['LLM Model',            meta.llm_model],
    ['Scoring Formula',      meta.scoring_formula],
    ['Threshold — BLOCK',    meta.thresholds?.BLOCK || '—'],
    ['Threshold — WARN',     meta.thresholds?.WARN  || '—'],
    ['Threshold — ALLOW',    meta.thresholds?.ALLOW || '—'],
  ];

  tbody.innerHTML = rows.map(([k, v]) => `
    <tr>
      <td>${escapeHtml(String(k))}</td>
      <td>${escapeHtml(String(v ?? '—'))}</td>
    </tr>`).join('');
}

// ── MAIN ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Wire up print button FIRST (before innerHTML swap)
  const printBtn = document.getElementById('print-btn');
  if (printBtn) printBtn.onclick = () => window.print();

  chrome.storage.local.get(['pg_report_data'], (result) => {
    const report = result.pg_report_data;

    if (!report) {
      document.body.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;
                    height:100vh;font-family:sans-serif;text-align:center;background:#F8FAFC;">
          <div>
            <div style="font-size:48px;margin-bottom:16px;">⚠️</div>
            <h2 style="color:#1E40AF;margin-bottom:8px;">No Report Data Found</h2>
            <p style="color:#6B7280;">Please regenerate the report from the extension popup or dashboard.</p>
          </div>
        </div>`;
      return;
    }

    // 1. Replace all {{ PLACEHOLDER }} markers in the static HTML
    replacePlaceholders(report);

    // 2. Populate dynamic sections (re-query elements after innerHTML replacement)
    renderSeverityBars(report.severity_distribution || {});
    renderAttackTable(report.attack_category_breakdown || {});
    renderTopThreats(report.top_threats || []);
    renderTimeline(report.timeline_events || []);
    renderRecommendations(report.recommendations || []);
    renderCompliance(report.compliance_notes || {});
    renderEngineMetadata(report.engine_metadata || {});

    // 3. Re-attach print button (innerHTML swap wiped it)
    const btn = document.getElementById('print-btn');
    if (btn) btn.onclick = () => window.print();

    // 4. Clean up stale report from storage
    chrome.storage.local.remove(['pg_report_data']);
  });
});
