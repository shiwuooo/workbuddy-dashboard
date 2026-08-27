const MODULES = {}; // 由 /api/config 填充
let history = [];

function $(s) { return document.querySelector(s); }
function el(tag, cls, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

function switchTab(name) {
  document.querySelectorAll('.nav').forEach(n => n.classList.toggle('active', n.dataset.tab === name));
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.id === 'tab-' + name));
}

async function api(path, opt) {
  const r = await fetch(path, opt);
  return r.json();
}

function addMsg(role, text, sources) {
  const c = el('div', 'msg ' + (role === 'user' ? 'user' : 'bot'));
  c.textContent = text;
  if (sources && sources.length) {
    const box = el('div', 'src');
    box.innerHTML = '参考真题：' + sources.map(s => `${s.paper}（${MODULES[s.module] || s.module}）`).join('；');
    c.appendChild(box);
  }
  $('#chat').appendChild(c);
  $('#chat').scrollTop = $('#chat').scrollHeight;
}

async function sendMsg() {
  const v = $('#msg').value.trim();
  if (!v) return;
  $('#msg').value = '';
  addMsg('user', v);
  history.push({ role: 'user', content: v });
  const data = await api('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: v, history }) });
  addMsg('bot', data.reply, data.sources);
  history.push({ role: 'assistant', content: data.reply });
}

function renderWeak(weak) {
  const box = $('#weakBars');
  box.innerHTML = '';
  if (!weak.length) { box.innerHTML = '<p class="hint">还没有错题记录，做题遇到不会的发给教练并标记，这里会画出你的薄弱点。</p>'; return; }
  weak.forEach(w => {
    const pct = Math.round(w.wrongRate * 100);
    const row = el('div', 'bar');
    row.innerHTML = `<div class="name">${MODULES[w.module] || w.module}</div>
      <div class="track"><div class="fill" style="width:${pct}%"></div></div>
      <div class="val">${pct}% (${w.wrong}/${w.total})</div>`;
    box.appendChild(row);
  });
}

function renderMistakes(list) {
  const box = $('#mistakeList');
  box.innerHTML = '';
  if (!list.length) { box.innerHTML = '<p class="hint">暂无错题。</p>'; return; }
  list.slice().reverse().forEach(m => {
    const c = el('div', 'card');
    c.innerHTML = `<div class="meta">${new Date(m.ts).toLocaleString()} · ${MODULES[m.module] || m.module}${m.tag ? ' · 错因：' + m.tag : ''}</div>
      <div class="q">${m.note || '(已标记错题)'}</div>`;
    box.appendChild(c);
  });
}

function renderQuestions(list, withMark) {
  const box = $('#dailyList');
  box.innerHTML = '';
  if (!list.length) { box.innerHTML = '<p class="hint">没有可生成的题目，先去「教练」里做题并标记错题，教练才知道你的薄弱点。</p>'; return; }
  list.forEach(q => {
    const c = el('div', 'card');
    let html = `<div class="meta">${q.paper} · ${MODULES[q.module] || q.module}</div><div class="q">${q.q}</div>`;
    if (q.options && q.options.length) q.options.forEach((o, i) => { html += `<div class="opt">${i}. ${o}</div>`; });
    html += `<div class="ans">答案：${q.answer}</div><div class="ex">解析：${q.explain}</div>`;
    if (withMark) {
      html += `<div style="margin-top:8px"><button data-id="${q.id}" data-mod="${q.module}">标记我不会</button></div>`;
    }
    c.innerHTML = html;
    box.appendChild(c);
  });
  if (withMark) {
    box.querySelectorAll('button[data-id]').forEach(b => b.onclick = async () => {
      await api('/api/mistake', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ questionId: b.dataset.id, module: b.dataset.mod, note: '主动练习标记' }) });
      b.textContent = '已记录'; b.disabled = true;
      loadGraph();
    });
  }
}

async function loadGraph() {
  const [weak, mistakes] = await Promise.all([api('/api/weak'), api('/api/mistakes')]);
  renderWeak(weak); renderMistakes(mistakes);
}

async function init() {
  const cfg = await api('/api/config');
  Object.assign(MODULES, cfg.modules);
  $('#goalBox').textContent = '目标：' + (await api('/api/profile')).goal;

  document.querySelectorAll('.nav').forEach(n => n.onclick = () => switchTab(n.dataset.tab));
  $('#send').onclick = sendMsg;
  $('#msg').addEventListener('keydown', e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) sendMsg(); });

  $('#genDaily').onclick = async () => renderQuestions(await api('/api/daily?n=5'), true);
  $('#genReview').onclick = async () => {
    const r = await api('/api/review');
    let txt = `目标：${r.goal}\n累计错题：${r.totalWrong} 道\n\n【最薄弱模块】\n`;
    r.weak.slice(0, 5).forEach(w => txt += `- ${MODULES[w.module] || w.module}：错 ${w.wrong}/${w.total}（${Math.round(w.wrongRate * 100)}%）\n`);
    txt += `\n【高频错因】\n`;
    if (r.topTags.length) r.topTags.forEach(t => txt += `- ${t[0]}：${t[1]} 次\n`);
    else txt += '（暂无标签，标记错题时可加错因）\n';
    txt += `\n建议：优先猛攻上面最弱的模块，每天用「今日练习」巩固。`;
    $('#reviewBox').textContent = txt;
  };

  // settings
  const prof = await api('/api/profile');
  $('#llmEnabled').checked = cfg.llmEnabled;
  $('#baseURL').value = 'https://api.deepseek.com/v1';
  $('#apiKey').value = '';
  $('#model').value = 'deepseek-chat';
  $('#goal').value = prof.goal || '';
  $('#saveSettings').onclick = async () => {
    await api('/api/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({
      llm: { enabled: $('#llmEnabled').checked, baseURL: $('#baseURL').value, apiKey: $('#apiKey').value || '在此填入你的 API Key', model: $('#model').value },
      goal: $('#goal').value
    }) });
    $('#goalBox').textContent = '目标：' + $('#goal').value;
    $('#settingsMsg').textContent = '已保存（填了 Key 才会真正调用大模型，需重启服务生效）。';
  };

  $('#gradeBtn').onclick = gradeEssay;
  loadGraph();
  addMsg('bot', '我是你的公考一对一私教。把做题遇到的问题、任何想法发给我，我会结合真题库给你讲。目标冲上岸，咱们一步步来。');
}

const DIMMAX = { 规范度: 30, 结构: 30, 论据: 20, 母题契合: 20 };

async function gradeEssay() {
  const v = $('#essay').value.trim();
  if (!v) { $('#gradeMsg').textContent = '先粘贴你的申论作答。'; return; }
  $('#gradeMsg').textContent = '批改中…';
  const r = await api('/api/shenlun', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: v }) });
  $('#gradeMsg').textContent = '';
  renderGrade(r);
}

function renderGrade(r) {
  const box = $('#gradeResult');
  let html = `<div class="grade-total">总分 <b>${r.total}</b> / 100</div>`;
  html += '<div class="dims">';
  for (const k of Object.keys(r.dims)) {
    const v = r.dims[k];
    const pct = Math.round(v / DIMMAX[k] * 100);
    html += `<div class="dim"><span class="dname">${k}</span><span class="track" style="flex:1;display:inline-block"><span class="fill" style="width:${pct}%"></span></span><span class="dval">${v}</span></div>`;
  }
  html += '</div>';
  if (r.motif) html += `<p class="hint">${r.relateMsg}</p>`;
  if (r.hits.length) {
    html += `<h3>命中规范表述（${r.hits.length}）</h3><ul class="norms">`;
    r.hits.forEach(h => html += `<li><b>${h.word}</b><br><span class="hint">适用：${h.use}</span></li>`);
    html += '</ul>';
  }
  if (r.suggestions.length) {
    html += '<h3>改进建议</h3><ul class="adv">';
    r.suggestions.forEach(s => html += `<li>${s}</li>`);
    html += '</ul>';
  }
  if (r.recommend.frames.length) {
    html += '<h3>可借鉴框架</h3>';
    r.recommend.frames.forEach(f => {
      html += `<div class="card"><div class="meta">${f.title}</div>`;
      (f.points || []).forEach(p => html += `<div class="q">· ${p}</div>`);
      if (f.up) html += `<div class="hint">升华：${f.up}</div>`;
      html += '</div>';
    });
  }
  box.innerHTML = html;
}

init();
