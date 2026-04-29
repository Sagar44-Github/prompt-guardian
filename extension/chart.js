/**
 * chart.js — Prompt Guardian Custom SVG Donut Chart Engine
 *
 * Reusable, dependency-free SVG donut chart with:
 *   - Animated arc drawing (stroke-dasharray technique)
 *   - Hover: scale arc outward, fade others, floating tooltip
 *   - Click: toggle glowing white highlight ring
 *   - Full mode: vertical legend synced to arc hover/click
 *   - Compact mode: chart only, no legend
 *
 * Usage:
 *   renderAttackChart(containerId, data, options)
 *
 *   data    = [{ name: 'Jailbreak', count: 5 }, ...]
 *   options = { size, mode, showCenterText, animationDuration }
 */

// ── ATTACK TYPE COLOR MAP ────────────────────────────────────────────────────
// Maps normalized attack type names → hex color
const CHART_COLORS = {
  'jailbreak':            '#EF4444',
  'instruction override': '#F59E0B',
  'instruction_override': '#F59E0B',
  'prompt extraction':    '#3B82F6',
  'prompt_extraction':    '#3B82F6',
  'data extraction':      '#8B5CF6',
  'data_extraction':      '#8B5CF6',
  'role override':        '#EC4899',
  'role_override':        '#EC4899',
  'encoded injection':    '#14B8A6',
  'encoded_injection':    '#14B8A6',
  'indirect injection':   '#F97316',
  'indirect_injection':   '#F97316',
  'social engineering':   '#84CC16',
  'social_engineering':   '#84CC16',
  'privilege escalation': '#A78BFA',
  'privilege_escalation': '#A78BFA',
  'harmful content':      '#FB7185',
  'harmful_content':      '#FB7185',
  'other':                '#64748B',
};

function getColor(name) {
  if (!name) return CHART_COLORS['other'];
  const key = name.toLowerCase().replace(/_/g, ' ');
  return CHART_COLORS[key] || CHART_COLORS[name.toLowerCase()] || CHART_COLORS['other'];
}

// ── SVG ARC MATH ─────────────────────────────────────────────────────────────
/**
 * Convert polar coordinates to SVG Cartesian (x, y).
 *
 * The SVG origin (0,0) is top-left, and angles in SVG go clockwise.
 * We use standard math angles (counterclockwise from +x), then negate y
 * because SVG y-axis is inverted.
 *
 * Formula:
 *   x = cx + r * cos(angle)       — horizontal offset from center
 *   y = cy - r * sin(angle)       — subtract because SVG y grows downward
 *
 * @param {number} cx - center x
 * @param {number} cy - center y
 * @param {number} r  - radius
 * @param {number} angleDeg - angle in degrees (0 = top, clockwise)
 */
function polarToCartesian(cx, cy, r, angleDeg) {
  // Convert degrees to radians, offset by -90° so 0° = top (12 o'clock)
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  };
}

/**
 * Build an SVG arc path string for a donut segment.
 *
 * Outer arc → straight line to inner → inner arc back → close path.
 * We use the SVG "A" (arc) command:
 *   A rx ry x-rotation large-arc-flag sweep-flag x y
 *
 * large-arc-flag = 1 if arc > 180°, else 0
 * sweep-flag     = 1 for clockwise (our direction)
 *
 * @param {number} cx, cy   - center of donut
 * @param {number} outerR   - outer radius
 * @param {number} innerR   - inner radius (hole)
 * @param {number} startDeg - start angle in degrees
 * @param {number} endDeg   - end angle in degrees
 */
function buildArcPath(cx, cy, outerR, innerR, startDeg, endDeg) {
  // Clamp to avoid full-circle path degeneration (SVG can't draw a full arc)
  const clampedEnd = Math.min(endDeg, startDeg + 359.99);

  const outerStart = polarToCartesian(cx, cy, outerR, startDeg);
  const outerEnd   = polarToCartesian(cx, cy, outerR, clampedEnd);
  const innerStart = polarToCartesian(cx, cy, innerR, clampedEnd);
  const innerEnd   = polarToCartesian(cx, cy, innerR, startDeg);

  const largeArc = (clampedEnd - startDeg) > 180 ? 1 : 0;

  // M = moveto, A = arc, L = lineto, Z = closepath
  return [
    `M ${outerStart.x} ${outerStart.y}`,
    `A ${outerR} ${outerR} 0 ${largeArc} 1 ${outerEnd.x} ${outerEnd.y}`,
    `L ${innerStart.x} ${innerStart.y}`,
    `A ${innerR} ${innerR} 0 ${largeArc} 0 ${innerEnd.x} ${innerEnd.y}`,
    'Z',
  ].join(' ');
}

// ── TOOLTIP ──────────────────────────────────────────────────────────────────
let _tooltip = null;

function getTooltip() {
  if (!_tooltip) {
    _tooltip = document.createElement('div');
    _tooltip.id = 'pg-chart-tooltip';
    Object.assign(_tooltip.style, {
      position: 'fixed',
      background: '#0D1526',
      border: '1px solid #2D4070',
      borderRadius: '8px',
      padding: '8px 12px',
      fontSize: '12px',
      color: '#E2E8F0',
      pointerEvents: 'none',
      zIndex: '99999',
      display: 'none',
      fontFamily: "'Segoe UI', sans-serif",
      lineHeight: '1.6',
      boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
      minWidth: '140px',
    });
    document.body.appendChild(_tooltip);
  }
  return _tooltip;
}

function showTooltip(e, name, count, pct) {
  const tip = getTooltip();
  tip.innerHTML = `
    <div style="font-weight:700;color:#F1F5F9;margin-bottom:3px;">${name}</div>
    <div style="color:#94A3B8;">Count: <span style="color:#E2E8F0;font-family:monospace;">${count}</span></div>
    <div style="color:#94A3B8;">Share:  <span style="color:#E2E8F0;font-family:monospace;">${pct.toFixed(1)}%</span></div>
  `;
  tip.style.display = 'block';
  moveTooltip(e);
}

function moveTooltip(e) {
  const tip = getTooltip();
  tip.style.left = (e.clientX + 14) + 'px';
  tip.style.top  = (e.clientY - 10) + 'px';
}

function hideTooltip() {
  const tip = getTooltip();
  tip.style.display = 'none';
}

// ── MAIN RENDER FUNCTION ──────────────────────────────────────────────────────
/**
 * renderAttackChart — render an interactive SVG donut chart into a container.
 *
 * @param {string} containerId        - ID of the DOM element to render into
 * @param {Array}  data               - [{ name, count }, ...]
 * @param {Object} options
 *   @param {number}  options.size              - chart diameter in px (default 200)
 *   @param {string}  options.mode              - 'full' | 'compact' (default 'full')
 *   @param {boolean} options.showCenterText    - show total in donut center (default true)
 *   @param {number}  options.animationDuration - arc draw duration ms (default 800)
 */
window.renderAttackChart = function renderAttackChart(containerId, data, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.warn(`[chart.js] Container #${containerId} not found`);
    return;
  }

  // ── Options ────────────────────────────────────────────────────────────────
  const size     = options.size              ?? 200;
  const mode     = options.mode              ?? 'full';
  const showCtr  = options.showCenterText    ?? true;
  const duration = options.animationDuration ?? 800;

  // ── Filter & sort data ─────────────────────────────────────────────────────
  const filtered = (data || []).filter(d => d && d.count > 0);
  const total    = filtered.reduce((s, d) => s + d.count, 0);

  // ── Geometry ───────────────────────────────────────────────────────────────
  const cx     = size / 2;
  const cy     = size / 2;
  const outerR = size * 0.44;   // outer radius = 44% of size
  const innerR = size * 0.27;   // inner radius = 27% of size (donut hole ~60% of outer)
  const gap    = 1.2;           // degrees of gap between arcs for visual separation

  // ── Build wrapper ──────────────────────────────────────────────────────────
  container.innerHTML = '';
  const wrapper = document.createElement('div');
  wrapper.style.cssText = `
    display:flex;
    align-items:center;
    gap:${mode === 'compact' ? '0' : '24px'};
    flex-wrap:wrap;
    justify-content:${mode === 'compact' ? 'center' : 'flex-start'};
  `;
  container.appendChild(wrapper);

  // ── SVG ────────────────────────────────────────────────────────────────────
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('width',  size);
  svg.setAttribute('height', size);
  svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
  svg.style.cssText = 'flex-shrink:0;overflow:visible;';

  // ── Empty state ────────────────────────────────────────────────────────────
  if (filtered.length === 0 || total === 0) {
    // Draw an empty gray ring
    const emptyCircle = document.createElementNS(svgNS, 'circle');
    emptyCircle.setAttribute('cx', cx);
    emptyCircle.setAttribute('cy', cy);
    emptyCircle.setAttribute('r',  (outerR + innerR) / 2);
    emptyCircle.setAttribute('fill', 'none');
    emptyCircle.setAttribute('stroke', '#1E2D4A');
    emptyCircle.setAttribute('stroke-width', outerR - innerR);
    svg.appendChild(emptyCircle);

    // Center text
    const msg = document.createElementNS(svgNS, 'text');
    msg.setAttribute('x', cx);
    msg.setAttribute('y', cy);
    msg.setAttribute('text-anchor', 'middle');
    msg.setAttribute('dominant-baseline', 'middle');
    msg.setAttribute('fill', '#475569');
    msg.setAttribute('font-size', size < 150 ? '10' : '12');
    msg.setAttribute('font-family', 'Segoe UI, sans-serif');
    msg.textContent = 'No attacks';
    svg.appendChild(msg);

    wrapper.appendChild(svg);
    container.appendChild(wrapper);
    return;
  }

  // ── Arc group ─────────────────────────────────────────────────────────────
  const arcGroup = document.createElementNS(svgNS, 'g');
  svg.appendChild(arcGroup);

  // Track selected arc for click-highlight
  let selectedIndex = -1;
  const paths = [];
  const legendItems = [];

  // ── Draw arcs ─────────────────────────────────────────────────────────────
  let currentDeg = 0;

  filtered.forEach((item, i) => {
    const sliceDeg = (item.count / total) * 360;
    const startDeg = currentDeg + gap / 2;
    const endDeg   = currentDeg + sliceDeg - gap / 2;
    currentDeg    += sliceDeg;

    const color = getColor(item.name);
    const pct   = (item.count / total) * 100;

    // Compute outward-push transform origin (center of arc midpoint)
    const midDeg = startDeg + (endDeg - startDeg) / 2;
    const pushDist = size * 0.04;   // scale-out distance
    const pushPt = polarToCartesian(cx, cy, pushDist, midDeg);
    const transformStr = `translate(${pushPt.x - cx} ${pushPt.y - cy})`;

    // Build path
    const d = buildArcPath(cx, cy, outerR, innerR, startDeg, endDeg);
    const path = document.createElementNS(svgNS, 'path');
    path.setAttribute('d', d);
    path.setAttribute('fill', color);
    path.setAttribute('stroke', 'transparent');
    path.setAttribute('stroke-width', '2');
    path.style.cssText = `cursor:pointer;transition:opacity 0.2s,filter 0.2s;`;
    arcGroup.appendChild(path);
    paths.push(path);

    // ── Animation: stroke-dasharray trick on the filled path ──────────────
    // We animate a transparent overlay path using stroke-dashoffset
    const animPath = document.createElementNS(svgNS, 'path');
    animPath.setAttribute('d', d);
    animPath.setAttribute('fill', 'none');
    animPath.setAttribute('stroke', color);

    // Approximate arc circumference for animation length
    const arcLen = ((endDeg - startDeg) / 360) * 2 * Math.PI * ((outerR + innerR) / 2);
    animPath.setAttribute('stroke-width', outerR - innerR);
    animPath.setAttribute('stroke-dasharray', arcLen);
    animPath.setAttribute('stroke-dashoffset', arcLen);
    animPath.style.cssText = 'pointer-events:none;';

    // Stagger animation per arc
    const delay = (i / filtered.length) * (duration * 0.4);
    const animDur = duration * 0.6;
    animPath.style.transition = `stroke-dashoffset ${animDur}ms ease ${delay}ms`;
    arcGroup.appendChild(animPath);

    // Trigger animation on next frame
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        animPath.setAttribute('stroke-dashoffset', '0');
      });
    });

    // ── Hover events ────────────────────────────────────────────────────────
    path.addEventListener('mouseenter', (e) => {
      // Fade all others
      paths.forEach((p, j) => {
        if (j !== i) p.style.opacity = '0.3';
      });
      legendItems.forEach((li, j) => {
        if (li && j !== i) li.style.opacity = '0.4';
      });
      // Push current arc outward
      path.setAttribute('transform', transformStr);
      showTooltip(e, item.name, item.count, pct);
    });

    path.addEventListener('mousemove', moveTooltip);

    path.addEventListener('mouseleave', () => {
      paths.forEach(p => { p.style.opacity = '1'; });
      legendItems.forEach(li => { if (li) li.style.opacity = '1'; });
      path.removeAttribute('transform');
      hideTooltip();
    });

    // ── Click: toggle glowing highlight ────────────────────────────────────
    path.addEventListener('click', () => {
      if (selectedIndex === i) {
        // Deselect
        path.setAttribute('stroke', 'transparent');
        path.setAttribute('stroke-width', '2');
        selectedIndex = -1;
      } else {
        // Deselect previous
        if (selectedIndex >= 0) {
          paths[selectedIndex].setAttribute('stroke', 'transparent');
          paths[selectedIndex].setAttribute('stroke-width', '2');
        }
        // Select current
        path.setAttribute('stroke', '#FFFFFF');
        path.setAttribute('stroke-width', '3');
        path.style.filter = `drop-shadow(0 0 6px ${color})`;
        selectedIndex = i;
      }
    });
  });

  // ── Center text ────────────────────────────────────────────────────────────
  if (showCtr) {
    const fontSize     = Math.max(12, size * 0.13);
    const labelSize    = Math.max(9, size * 0.07);

    const totalText = document.createElementNS(svgNS, 'text');
    totalText.setAttribute('x', cx);
    totalText.setAttribute('y', cy - fontSize * 0.25);
    totalText.setAttribute('text-anchor', 'middle');
    totalText.setAttribute('dominant-baseline', 'middle');
    totalText.setAttribute('fill', '#F1F5F9');
    totalText.setAttribute('font-size', fontSize);
    totalText.setAttribute('font-family', 'Courier New, monospace');
    totalText.setAttribute('font-weight', '700');
    totalText.textContent = total;
    svg.appendChild(totalText);

    const labelText = document.createElementNS(svgNS, 'text');
    labelText.setAttribute('x', cx);
    labelText.setAttribute('y', cy + fontSize * 0.75);
    labelText.setAttribute('text-anchor', 'middle');
    labelText.setAttribute('dominant-baseline', 'middle');
    labelText.setAttribute('fill', '#64748B');
    labelText.setAttribute('font-size', labelSize);
    labelText.setAttribute('font-family', 'Segoe UI, sans-serif');
    labelText.textContent = 'Total Threats';
    svg.appendChild(labelText);
  }

  wrapper.appendChild(svg);

  // ── Legend (full mode only) ────────────────────────────────────────────────
  if (mode === 'full') {
    const legendEl = document.createElement('div');
    legendEl.style.cssText = `
      display:flex;flex-direction:column;gap:8px;flex:1;min-width:140px;
    `;

    filtered.forEach((item, i) => {
      const color = getColor(item.name);
      const pct   = ((item.count / total) * 100).toFixed(1);
      const label = (item.name || 'Other').length > 20
        ? item.name.slice(0, 20) + '…'
        : item.name;

      const li = document.createElement('div');
      li.style.cssText = `
        display:flex;align-items:center;gap:8px;
        font-size:12px;color:#94A3B8;cursor:pointer;
        transition:opacity 0.2s;padding:3px 0;
      `;
      li.innerHTML = `
        <div style="width:10px;height:10px;border-radius:50%;background:${color};flex-shrink:0;"></div>
        <span style="flex:1;color:#CBD5E1;">${label}</span>
        <span style="font-family:monospace;color:#E2E8F0;font-weight:600;">${item.count}</span>
        <span style="color:#64748B;font-size:11px;margin-left:2px;">(${pct}%)</span>
      `;

      // Legend hover syncs with arc
      li.addEventListener('mouseenter', () => {
        paths.forEach((p, j) => { if (j !== i) p.style.opacity = '0.3'; });
        legendItems.forEach((l, j) => { if (l && j !== i) l.style.opacity = '0.4'; });
        const midDeg = /* recompute */ (() => {
          let deg = 0;
          for (let k = 0; k < i; k++) deg += (filtered[k].count / total) * 360;
          return deg + ((filtered[i].count / total) * 360) / 2;
        })();
        const pushDist = size * 0.04;
        const pushPt = polarToCartesian(cx, cy, pushDist, midDeg);
        paths[i].setAttribute('transform', `translate(${pushPt.x - cx} ${pushPt.y - cy})`);
      });

      li.addEventListener('mouseleave', () => {
        paths.forEach(p => { p.style.opacity = '1'; });
        legendItems.forEach(l => { if (l) l.style.opacity = '1'; });
        paths[i].removeAttribute('transform');
      });

      legendEl.appendChild(li);
      legendItems.push(li);
    });

    wrapper.appendChild(legendEl);
  } else {
    // compact — no legend
    legendItems.push(...filtered.map(() => null));
  }
};
