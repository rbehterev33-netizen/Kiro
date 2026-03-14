const API_BASE = '';

// --- Fetch ---
async function api(path, method = 'GET', body = null) {
  try {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API_BASE + path, opts);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('API error:', path, e);
    toast(e.message, 'error');
    return null;
  }
}

// --- Toast уведомления ---
function toast(msg, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  container.appendChild(t);
  requestAnimationFrame(() => t.classList.add('show'));
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, duration);
}

// --- Спиннер ---
function setLoading(id, cols = 1) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `<tr><td colspan="${cols}" class="loading"><span class="spinner"></span> Загрузка...</td></tr>`;
}

// --- Экспорт в CSV ---
function exportCSV(data, filename) {
  if (!data || !data.length) { toast('Нет данных для экспорта', 'error'); return; }
  const keys = Object.keys(data[0]);
  const rows = [keys.join(','), ...data.map(r => keys.map(k => `"${r[k] ?? ''}"`).join(','))];
  const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  toast(`Экспортировано: ${filename}`, 'success');
}

// --- Форматирование ---
function fmt(n, digits = 4) {
  if (n == null) return '—';
  return parseFloat(n).toFixed(digits);
}
function fmtNum(n) {
  if (n == null) return '—';
  return parseFloat(n).toLocaleString('ru');
}

// --- RSI шкала ---
function rsiBar(rsi) {
  if (rsi == null) return '<span class="muted">—</span>';
  const cls = rsi > 70 ? 'rsi-high' : rsi < 30 ? 'rsi-low' : 'rsi-mid';
  const label = rsi > 70 ? 'перекуплен' : rsi < 30 ? 'перепродан' : 'норма';
  return `<div class="rsi-wrap">
    <div class="rsi-track"><div class="rsi-fill ${cls}" style="width:${rsi}%"></div></div>
    <span class="rsi-val">${rsi.toFixed(1)} <span class="rsi-label ${cls}">${label}</span></span>
  </div>`;
}

// --- Спарклайн (mini SVG) ---
function sparkline(values, color = '#4f8ef7') {
  if (!values || values.length < 2) return '';
  const w = 80, h = 28, pad = 2;
  const min = Math.min(...values), max = Math.max(...values);
  const range = max - min || 1;
  const pts = values.map((v, i) => {
    const x = pad + (i / (values.length - 1)) * (w - pad * 2);
    const y = pad + (1 - (v - min) / range) * (h - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
  const trend = values[values.length - 1] > values[0];
  const c = trend ? '#22c55e' : '#ef4444';
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
    <polyline points="${pts}" fill="none" stroke="${c}" stroke-width="1.5" stroke-linejoin="round"/>
  </svg>`;
}

// --- Активный пункт меню ---
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });
});

// Алиас для совместимости
const showToast = toast;
