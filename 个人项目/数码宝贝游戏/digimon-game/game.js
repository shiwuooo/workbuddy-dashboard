// ================= 核心状态与养成逻辑 =================
const SAVE_KEY = "digimon_adv_save_v1";
let S = null; // 全局存档状态

function defaultState(pid) {
  const p = PARTNERS.find(x => x.id === pid);
  return {
    pid: pid,
    stage: 0,
    level: 1,
    exp: 0,
    // 属性上限
    maxHp: p.base.hp, maxMp: p.base.mp,
    atk: p.base.atk, def: p.base.def, spd: p.base.spd,
    // 当前值
    hp: p.base.hp, mp: p.base.mp,
    care: { hunger: 80, mood: 80, energy: 100, clean: 100 },
    sick: false,
    money: 100,
    items: { meat: 3, bigmeat: 0, snack: 2, potion: 2, mpot: 1, med: 1 },
    cleared: 0,           // 已通关章节数
    day: 1, tickCount: 0,
    lastSeen: Date.now(),
    log: []
  };
}

function partner() { return PARTNERS.find(x => x.id === S.pid); }
function curStage() { return partner().st[S.stage]; }
function expNeed(lv) { return lv * lv * 6 + lv * 14 + 30; }

function save() { S.lastSeen = Date.now(); localStorage.setItem(SAVE_KEY, JSON.stringify(S)); }
function load() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return false;
    S = JSON.parse(raw);
    applyOfflineDecay();
    return true;
  } catch (e) { return false; }
}

// 离线衰减（封顶，避免回来就饿死）
function applyOfflineDecay() {
  const mins = Math.min(720, (Date.now() - (S.lastSeen || Date.now())) / 60000);
  const t = Math.floor(mins / 5);
  if (t <= 0) return;
  S.care.hunger = Math.max(10, S.care.hunger - t * 2);
  S.care.clean = Math.max(10, S.care.clean - t * 1.5);
  S.care.mood = Math.max(15, S.care.mood - t);
  S.care.energy = Math.min(100, S.care.energy + t * 4);
  if (t > 3) addLog("你离开的这段时间，" + curStage().n + "一直在等你回来……");
}

// ================= 初始化 =================
window.addEventListener("DOMContentLoaded", () => {
  renderPartnerSelect();
  if (load()) { enterMain(); }
  setInterval(gameTick, 15000);
});

function renderPartnerSelect() {
  const grid = document.getElementById("partnerGrid");
  grid.innerHTML = PARTNERS.map(p => {
    const chain = p.st.map(s => s.n).join(" → ");
    return `<div class="partner-card" onclick="choosePartner('${p.id}')">
      <div class="pc-emoji">${p.st[1].e}</div>
      <div class="pc-name">${p.st[1].n}</div>
      <div class="pc-kid">${p.kid} 的搭档</div>
      <div class="pc-crest">${p.crest}</div>
      <div class="pc-line">${chain}</div>
    </div>`;
  }).join("");
}

function choosePartner(pid) {
  S = defaultState(pid);
  const p = partner();
  addLog("你与 " + p.st[0].n + " 相遇了！它将进化为 " + p.st[1].n + "，陪你踏上冒险之旅。");
  save();
  enterMain();
  showStory("相遇", "数码暴龙机发出耀眼的光芒——\n\n「我等你好久了！我是" + p.st[0].n + "，你就是我的搭档吧！」\n\n它是" + p.kid + "同款搭档数码宝贝的同伴，携带着「" + p.crest + "」的力量。\n\n先在【养成】页照顾好它，喂食、训练、升级，然后去【冒险】页开启第1章剧情吧！", null);
}

function enterMain() {
  document.getElementById("screen-start").classList.add("hidden");
  document.getElementById("screen-main").classList.remove("hidden");
  renderAll();
}

// ================= 渲染 =================
function pct(v, m) { return Math.max(0, Math.min(100, v / m * 100)) + "%"; }

function renderAll() {
  if (!S) return;
  const st = curStage();
  document.getElementById("hdDay").textContent = "📅 第" + S.day + "天";
  document.getElementById("hdMoney").textContent = "💰 " + S.money;
  document.getElementById("petStage").textContent = STAGE_NAMES[S.stage];
  document.getElementById("petEmoji").textContent = st.e;
  document.getElementById("petName").textContent = st.n;
  document.getElementById("petKid").textContent = partner().kid + "的搭档 · " + partner().crest;
  document.getElementById("petLv").textContent = "Lv." + S.level;
  document.getElementById("sickBadge").classList.toggle("hidden", !S.sick);

  document.getElementById("expBar").style.width = pct(S.exp, expNeed(S.level));
  document.getElementById("expTxt").textContent = S.exp + "/" + expNeed(S.level);
  document.getElementById("hpBar").style.width = pct(S.hp, S.maxHp);
  document.getElementById("hpTxt").textContent = Math.ceil(S.hp) + "/" + S.maxHp;
  document.getElementById("mpBar").style.width = pct(S.mp, S.maxMp);
  document.getElementById("mpTxt").textContent = Math.ceil(S.mp) + "/" + S.maxMp;

  document.getElementById("statGrid").innerHTML =
    `<div class="stat-cell">攻击<b>${S.atk}</b></div>
     <div class="stat-cell">防御<b>${S.def}</b></div>
     <div class="stat-cell">速度<b>${S.spd}</b></div>`;

  document.getElementById("hungerBar").style.width = pct(S.care.hunger, 100);
  document.getElementById("moodBar").style.width = pct(S.care.mood, 100);
  document.getElementById("energyBar").style.width = pct(S.care.energy, 100);
  document.getElementById("cleanBar").style.width = pct(S.care.clean, 100);

  renderEvo(); renderFood(); renderChapters(); renderShop(); renderDex(); renderLog();
}

function renderEvo() {
  const btn = document.getElementById("evoBtn");
  const hint = document.getElementById("evoHint");
  if (S.stage >= 4) { btn.classList.add("hidden"); hint.textContent = "已达到究极体，这就是羁绊的终点！"; return; }
  const req = EVO_REQ[S.stage + 1];
  const next = partner().st[S.stage + 1];
  const okLv = S.level >= req.lv, okCh = S.cleared >= req.ch, okMood = S.care.mood >= 40;
  if (okLv && okCh && okMood && !S.sick) {
    btn.classList.remove("hidden");
    hint.textContent = "可以进化为【" + next.n + "】了！";
  } else {
    btn.classList.add("hidden");
    const needs = [];
    if (!okLv) needs.push("等级" + req.lv + "（当前" + S.level + "）");
    if (!okCh) needs.push("通关第" + req.ch + "章（当前" + S.cleared + "章）");
    if (!okMood) needs.push("心情≥40");
    if (S.sick) needs.push("治愈疾病");
    hint.textContent = "进化为【" + next.n + "】需要：" + needs.join("、");
  }
}

function renderFood() {
  const box = document.getElementById("foodList");
  const foods = ["meat", "bigmeat", "snack"];
  box.innerHTML = foods.map(k => {
    const it = ITEMS[k], num = S.items[k] || 0;
    return `<div class="item-chip ${num ? "" : "disabled"}" onclick="doFeed('${k}')">
      <span class="ic-emoji">${it.e}</span><span>${it.n} ×${num}</span><span class="ic-sub">${it.desc}</span>
    </div>`;
  }).join("");
}

function renderLog() {
  document.getElementById("homeLog").innerHTML = (S.log || []).slice(0, 30).map(x => "· " + x).join("<br>");
}
function addLog(msg) {
  if (!S.log) S.log = [];
  S.log.unshift(msg);
  S.log = S.log.slice(0, 40);
}

function renderChapters() {
  const box = document.getElementById("chapterList");
  box.innerHTML = CHAPTERS.map((c, i) => {
    const cleared = i < S.cleared;
    const unlocked = i <= S.cleared;
    let btn;
    if (cleared) btn = `<button class="ch-btn replay" onclick="startChapter(${i}, true)">重温</button>`;
    else if (unlocked) btn = `<button class="ch-btn" onclick="startChapter(${i}, false)">挑战</button>`;
    else btn = `<button class="ch-btn" disabled>未解锁</button>`;
    return `<div class="chapter-card ${cleared ? "cleared" : ""} ${unlocked ? "" : "locked"}">
      <div class="ch-emoji">${c.emoji}</div>
      <div class="ch-info">
        <div class="ch-name">${c.name} ${cleared ? "✅" : ""}</div>
        <div class="ch-boss">BOSS：${c.boss.e} ${c.boss.n}　奖励：${c.boss.exp}经验 / ${c.boss.money}币</div>
      </div>${btn}</div>`;
  }).join("");
}

function renderShop() {
  const shop = document.getElementById("shopList");
  shop.innerHTML = Object.keys(ITEMS).map(k => {
    const it = ITEMS[k];
    return `<div class="item-chip" onclick="buyItem('${k}')">
      <span class="ic-emoji">${it.e}</span><span>${it.n}</span>
      <span class="ic-sub">${it.desc}</span><span class="ic-price">💰${it.price}</span>
    </div>`;
  }).join("");
  const bag = document.getElementById("bagList");
  const owned = Object.keys(S.items).filter(k => S.items[k] > 0);
  bag.innerHTML = owned.length
    ? owned.map(k => `<div class="item-chip"><span class="ic-emoji">${ITEMS[k].e}</span><span>${ITEMS[k].n} ×${S.items[k]}</span></div>`).join("")
    : "<p class='tip'>背包空空如也……</p>";
}

function renderDex() {
  const box = document.getElementById("dexList");
  box.innerHTML = PARTNERS.map(p => {
    const mine = p.id === S.pid;
    const chain = p.st.map((s, i) => {
      const now = mine && i === S.stage;
      return `<div class="dex-node ${now ? "now" : ""}">
        <div class="dn-emoji">${s.e}</div><div class="dn-name">${s.n}</div>
        <div class="dn-stage">${STAGE_NAMES[i]}</div><div class="dn-skill">${s.s[0]}</div>
      </div>` + (i < 4 ? "<span class='dex-arrow'>▶</span>" : "");
    }).join("");
    return `<div class="dex-block">
      <div class="dex-head">${p.st[1].e} ${p.st[1].n} 系 <span class="crest">${p.kid} · ${p.crest}${mine ? " · ★我的搭档" : ""}</span></div>
      <div class="dex-chain">${chain}</div></div>`;
  }).join("");
}

function switchTab(t) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.toggle("active", b.dataset.tab === t));
  document.querySelectorAll(".tab-page").forEach(pg => pg.classList.add("hidden"));
  document.getElementById("tab-" + t).classList.remove("hidden");
}

// ================= 养成动作 =================
function toast(msg) { addLog(msg); renderAll(); save(); }

function doFeed(k) {
  if (!S.items[k]) { toast("没有" + ITEMS[k].n + "了，去商店买一点吧！"); return; }
  S.items[k]--;
  if (k === "meat") { S.care.hunger = Math.min(100, S.care.hunger + 35); S.hp = Math.min(S.maxHp, S.hp + S.maxHp * 0.1); }
  if (k === "bigmeat") { S.care.hunger = 100; S.care.mood = Math.min(100, S.care.mood + 10); S.hp = Math.min(S.maxHp, S.hp + S.maxHp * 0.25); }
  if (k === "snack") { S.care.mood = Math.min(100, S.care.mood + 25); S.care.hunger = Math.min(100, S.care.hunger + 10); }
  toast(curStage().n + " 开心地吃掉了" + ITEMS[k].n + "！");
}

function doPlay() {
  if (S.care.energy < 10) { toast(curStage().n + " 太累了，先休息一下吧。"); return; }
  S.care.mood = Math.min(100, S.care.mood + 20);
  S.care.energy -= 10;
  S.care.hunger = Math.max(0, S.care.hunger - 5);
  toast("你和 " + curStage().n + " 玩了一会儿球，它超开心！");
}

function doRest() {
  S.care.energy = 100;
  S.hp = S.maxHp; S.mp = S.maxMp;
  S.care.hunger = Math.max(0, S.care.hunger - 10);
  toast(curStage().n + " 睡了个好觉，体力和HP/MP全部恢复了！");
}

function doCleanUp() {
  S.care.clean = 100;
  S.care.mood = Math.min(100, S.care.mood + 5);
  toast("你把周围打扫得干干净净，" + curStage().n + " 神清气爽！");
}

function doCure() {
  if (!S.sick) { toast(curStage().n + " 很健康，不需要吃药。"); return; }
  if (!S.items.med) { toast("没有万能药了！快去商店买。"); return; }
  S.items.med--; S.sick = false;
  toast(curStage().n + " 的病治好了！");
}

function doTrain(type) {
  if (S.sick) { toast(curStage().n + " 生病了，不能训练！先喂万能药。"); return; }
  if (S.care.energy < 20) { toast("体力不足20，先休息吧。"); return; }
  if (S.care.hunger <= 5) { toast(curStage().n + " 饿得没力气了，先喂点吃的！"); return; }
  S.care.energy -= 20;
  S.care.hunger = Math.max(0, S.care.hunger - 10);
  S.care.mood = Math.max(0, S.care.mood - 5);
  const moodMult = S.care.mood >= 60 ? 1.2 : 1;
  let msg = "";
  if (type === "atk") { S.atk += 2; msg = "力量训练完成，攻击+2！"; }
  if (type === "def") { S.def += 2; msg = "防御训练完成，防御+2！"; }
  if (type === "spd") { S.spd += 2; msg = "速度训练完成，速度+2！"; }
  let exp = Math.round((type === "exp" ? 20 + S.level * 8 : 10 + S.level * 3) * moodMult);
  if (type === "exp") msg = "综合特训完成！";
  msg += " 获得" + exp + "经验" + (moodMult > 1 ? "（心情好，效果提升！）" : "");
  gainExp(exp);
  toast(msg);
}

function gainExp(n) {
  S.exp += n;
  while (S.exp >= expNeed(S.level)) {
    S.exp -= expNeed(S.level);
    S.level++;
    S.maxHp += 8; S.maxMp += 4; S.atk += 3; S.def += 2; S.spd += 2;
    S.hp = S.maxHp; S.mp = S.maxMp;
    addLog("🎉 升级了！" + curStage().n + " 达到 Lv." + S.level + "，全属性提升，状态全满！");
  }
}

function doEvolve() {
  if (S.stage >= 4) return;
  const req = EVO_REQ[S.stage + 1];
  if (S.level < req.lv || S.cleared < req.ch || S.care.mood < 40 || S.sick) return;
  const from = curStage().n;
  S.stage++;
  const b = EVO_BONUS[S.stage];
  S.maxHp += b.hp; S.maxMp += b.mp; S.atk += b.atk; S.def += b.def; S.spd += b.spd;
  S.hp = S.maxHp; S.mp = S.maxMp;
  const to = curStage();
  addLog("✨✨ " + from + " 进化——" + to.n + "！！学会了新技能【" + to.s[0] + "】！");
  save(); renderAll();
  showStory("✨ 进化！", from + " 身上迸发出耀眼的光芒——\n\n「" + from + "，进化——" + to.n + "！！」\n\n" + to.e + " " + to.n + "（" + STAGE_NAMES[S.stage] + "）诞生了！\n习得新技能【" + to.s[0] + "】（威力×" + to.s[1] + "）\n全属性大幅提升，HP/MP已回满！", null);
}

// ================= 周期 tick =================
function gameTick() {
  if (!S || inBattle) return;
  S.tickCount++;
  S.care.hunger = Math.max(0, S.care.hunger - 2);
  S.care.clean = Math.max(0, S.care.clean - 1.5);
  let moodDrop = 1;
  if (S.care.hunger < 20) moodDrop += 2;
  if (S.care.clean < 20) moodDrop += 2;
  S.care.mood = Math.max(0, S.care.mood - moodDrop);
  S.care.energy = Math.min(100, S.care.energy + 4);
  if (!S.sick && (S.care.hunger < 15 || S.care.clean < 15) && Math.random() < 0.08) {
    S.sick = true;
    addLog("😨 " + curStage().n + " 生病了！快用万能药治疗它！");
  }
  if (S.tickCount % 20 === 0) { S.day++; addLog("📅 数码世界迎来了第" + S.day + "天。"); }
  save(); renderAll();
}

// ================= 商店 =================
function buyItem(k) {
  const it = ITEMS[k];
  if (S.money < it.price) { toast("数码币不够！去自由对战赚点钱吧。"); return; }
  S.money -= it.price;
  S.items[k] = (S.items[k] || 0) + 1;
  toast("购买了 " + it.e + it.n + "。");
}

// ================= 剧情弹窗 =================
function showStory(title, text, onClose) {
  document.getElementById("storyTitle").textContent = title;
  document.getElementById("storyText").textContent = text;
  const modal = document.getElementById("storyModal");
  modal.classList.remove("hidden");
  document.getElementById("storyBtn").onclick = () => {
    modal.classList.add("hidden");
    if (onClose) onClose();
  };
}

// ================= 存档管理 =================
function exportSave() {
  document.getElementById("saveBox").value = JSON.stringify(S);
  toast("存档已导出到文本框，请自行复制保存。");
}
function importSave() {
  try {
    const raw = document.getElementById("saveBox").value.trim();
    const data = JSON.parse(raw);
    if (!data.pid) throw new Error("bad");
    S = data; save(); renderAll();
    toast("存档导入成功！");
  } catch (e) { alert("存档数据无效，导入失败。"); }
}
function resetGame() {
  if (!confirm("确定要删除存档、重新开始吗？此操作不可恢复！")) return;
  localStorage.removeItem(SAVE_KEY);
  location.reload();
}
