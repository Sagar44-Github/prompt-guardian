/**
 * dashboard.js — Prompt Guardian Threat Intelligence Center
 * Reads pg_history from chrome.storage.local and renders full analytics.
 */

// ── COLOR PALETTE FOR ATTACK TYPES ──────────────────────────────────────────
const ATTACK_COLORS = {
  'jailbreak':            '#EF4444',
  'instruction_override': '#F59E0B',
  'prompt_extraction':    '#3B82F6',
  'data_extraction':      '#8B5CF6',
  'role_override':        '#EC4899',
  'encoded_injection':    '#06B6D4',
  'indirect_injection':   '#F97316',
  'social_engineering':   '#84CC16',
  'privilege_escalation': '#A78BFA',
  'harmful_content':      '#FB7185',
  'other':                '#64748B',
};

// Normalize attack type key
function normalizeKey(type) {
  if (!type || type === 'Unknown' || type === 'None') return null;
  return type.toLowerCase().replace(/\s+/g, '_');
}

// Get color for attack type
function colorFor(type) {
  const k = normalizeKey(type);
  return k && ATTACK_COLORS[k] ? ATTACK_COLORS[k] : ATTACK_COLORS['other'];
}

// Safe HTML escape
function escapeHtml(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Truncate string
function truncate(str, len) {
  if (!str) return '—';
  return str.length > len ? str.slice(0, len) + '…' : str;
}

// Format ISO timestamp to local time string
function fmtTime(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// Format ISO timestamp to full locale string
function fmtFull(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString();
}

// ── ANIMATED COUNTER ────────────────────────────────────────────────────────
function animateCounter(el, target, isDecimal = false, duration = 900) {
  const start = performance.now();
  const startVal = 0;

  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = startVal + (target - startVal) * eased;

    el.textContent = isDecimal ? current.toFixed(1) : Math.round(current).toString();

    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = isDecimal ? target.toFixed(1) : target.toString();
  }

  requestAnimationFrame(step);
}

// ── THREAT LOG TABLE ────────────────────────────────────────────────────────
function renderTable(history) {
  const tbody = document.getElementById('log-table-body');
  const recent = history.slice(0, 20);

  if (recent.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:#475569;padding:24px;">No entries to display</td></tr>`;
    return;
  }

  tbody.innerHTML = recent.map(entry => {
    const action = entry.action || 'ALLOW';
    const rowClass = action === 'BLOCK' ? 'row-block' : action === 'WARN' ? 'row-warn' : 'row-allow';
    const badgeClass = action === 'BLOCK' ? 'badge-block' : action === 'WARN' ? 'badge-warn' : 'badge-allow';

    const riskColor = action === 'BLOCK' ? '#EF4444' : action === 'WARN' ? '#F59E0B' : '#10B981';
    const attackLabel = entry.attack_type && entry.attack_type !== 'Unknown'
      ? entry.attack_type.replace(/_/g, ' ')
      : (action === 'ALLOW' ? 'Clean' : 'Unknown');

    return `
      <tr class="${rowClass}">
        <td style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#64748B;white-space:nowrap;">${fmtTime(entry.timestamp)}</td>
        <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(entry.prompt)}">${escapeHtml(truncate(entry.prompt, 55))}</td>
        <td class="risk-cell" style="color:${riskColor}">${(entry.risk_score || 0).toFixed(1)}%</td>
        <td style="font-size:12px;text-transform:capitalize;color:#94A3B8;">${escapeHtml(attackLabel)}</td>
        <td><span class="action-badge ${badgeClass}">${action}</span></td>
      </tr>`;
  }).join('');
}

// ── DONUT CHART ─────────────────────────────────────────────────────────────
function renderDonut(history) {
  const donut = document.getElementById('donut-chart');
  const legend = document.getElementById('chart-legend');

  // Count attack types (only from non-ALLOW entries)
  const counts = {};
  history.forEach(entry => {
    if (entry.action === 'ALLOW') return;
    const k = normalizeKey(entry.attack_type) || 'other';
    counts[k] = (counts[k] || 0) + 1;
  });

  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  if (total === 0) {
    donut.style.background = '#1E2D4A';
    legend.innerHTML = `<div style="color:#475569;font-size:12px;text-align:center;padding:20px;">No threats detected yet</div>`;
    return;
  }

  // Build conic-gradient segments
  let gradientParts = [];
  let currentDeg = 0;
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);

  const legendItems = entries.map(([type, count]) => {
    const color = ATTACK_COLORS[type] || ATTACK_COLORS['other'];
    const pct = (count / total) * 100;
    const deg = (count / total) * 360;

    gradientParts.push(`${color} ${currentDeg}deg ${currentDeg + deg}deg`);
    currentDeg += deg;

    const label = type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    return `
      <div class="legend-item">
        <div class="legend-dot" style="background:${color}"></div>
        <span class="legend-label">${label}</span>
        <span class="legend-count">${count}</span>
        <span class="legend-pct">(${pct.toFixed(0)}%)</span>
      </div>`;
  });

  donut.style.background = `conic-gradient(${gradientParts.join(', ')})`;
  donut.style.boxShadow = '0 0 30px rgba(96,165,250,0.1)';
  legend.innerHTML = legendItems.join('');
}

// ── TIMELINE ────────────────────────────────────────────────────────────────
function renderTimeline(history) {
  const line = document.getElementById('timeline-line');
  const tlStart = document.getElementById('tl-start');
  const tlEnd   = document.getElementById('tl-end');

  if (history.length < 2) {
    line.innerHTML = `<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:11px;color:#475569;">Not enough data for timeline</div>`;
    return;
  }

  // Sort by timestamp
  const sorted = [...history].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  const earliest = new Date(sorted[0].timestamp).getTime();
  const latest   = new Date(sorted[sorted.length - 1].timestamp).getTime();
  const range    = latest - earliest || 1;

  tlStart.textContent = fmtTime(sorted[0].timestamp);
  tlEnd.textContent   = fmtTime(sorted[sorted.length - 1].timestamp);

  // Clamp to [2, 98] so dots don't fall off edges
  const dots = sorted.map(entry => {
    const t = new Date(entry.timestamp).getTime();
    const pct = Math.max(2, Math.min(98, ((t - earliest) / range) * 100));
    const action = entry.action || 'ALLOW';
    const cls = action === 'BLOCK' ? 'dot-block' : action === 'WARN' ? 'dot-warn' : 'dot-allow';
    const tip = `${fmtFull(entry.timestamp)} | Risk: ${(entry.risk_score||0).toFixed(1)}% | ${action}`;

    return `<div class="timeline-dot ${cls}" style="left:${pct}%" title="${escapeHtml(tip)}"></div>`;
  });

  line.innerHTML = dots.join('');
}

// ── FOOTER ──────────────────────────────────────────────────────────────────
function renderFooter(history) {
  const footerEl = document.getElementById('footer-session');
  if (!footerEl) return;

  if (history.length === 0) {
    footerEl.textContent = 'Session started: —';
    return;
  }

  const sorted = [...history].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  footerEl.textContent = `Session started: ${fmtFull(sorted[0].timestamp)}`;
}

// ── MAIN ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.local.get(['pg_history'], (data) => {
    const history = data.pg_history || [];

    // Show empty state if no data
    if (history.length === 0) {
      document.getElementById('main-grid').style.display = 'none';
      document.getElementById('empty-state').style.display = 'block';
      return;
    }

    // ── Calculate Stats ──────────────────────────────────────────────────
    const total    = history.length;
    const threats  = history.filter(e => e.action !== 'ALLOW').length;
    const safe     = total - threats;
    const avgRisk  = history.reduce((sum, e) => sum + (e.risk_score || 0), 0) / total;

    // ── Animate Counters ─────────────────────────────────────────────────
    animateCounter(document.getElementById('stat-total'),   total,   false, 900);
    animateCounter(document.getElementById('stat-threats'), threats, false, 900);
    animateCounter(document.getElementById('stat-safe'),    safe,    false, 900);
    animateCounter(document.getElementById('stat-avg'),     avgRisk, true,  900);

    // ── Render Sections ──────────────────────────────────────────────────
    renderTable(history);
    renderDonut(history);
    renderTimeline(history);
    renderFooter(history);
  });
});
