// ================= 回合制战斗系统 =================
let inBattle = false;
let B = null; // 战斗上下文

function battleStatMods() {
  // 养成状态影响战斗
  let mult = 1;
  if (S.sick) mult *= 0.7;
  if (S.care.hunger <= 10) mult *= 0.8;
  if (S.care.mood >= 80) mult *= 1.1;
  return mult;
}

function startChapter(idx, replay) {
  if (idx > S.cleared) return;
  const c = CHAPTERS[idx];
  showStory(c.name, c.pre, () => {
    beginBattle({
      mode: "story", idx: idx, replay: replay,
      title: c.name,
      enemy: {
        n: c.boss.n, e: c.boss.e,
        hp: c.boss.hp, maxHp: c.boss.hp,
        atk: c.boss.atk, def: c.boss.def, spd: c.boss.spd,
        skill: c.boss.s, mp: 999,
        exp: c.boss.exp, money: c.boss.money
      }
    });
  });
}

function startWildBattle() {
  const mob = WILD_MOBS[Math.floor(Math.random() * WILD_MOBS.length)];
  const lv = Math.max(1, S.level + Math.floor(Math.random() * 5) - 2);
  beginBattle({
    mode: "wild", title: "遭遇野生数码兽！",
    enemy: {
      n: mob.n + " Lv." + lv, e: mob.e,
      hp: 40 + lv * 13, maxHp: 40 + lv * 13,
      atk: 8 + lv * 3, def: 4 + lv * 1.6, spd: 6 + lv * 1.5,
      skill: ["突击", 1.4], mp: 999,
      exp: 30 + lv * 12, money: 12 + lv * 4
    }
  });
}

function beginBattle(cfg) {
  if (S.hp <= 1) { toast(curStage().n + " 已经站不起来了！先【休息】恢复HP吧。"); return; }
  inBattle = true;
  B = {
    cfg: cfg, enemy: cfg.enemy,
    defending: false, turn: 1, over: false
  };
  document.getElementById("screen-main").classList.add("hidden");
  document.getElementById("screen-battle").classList.remove("hidden");
  document.getElementById("bTitle").textContent = "⚔️ " + cfg.title;
  document.getElementById("bLog").innerHTML = "";
  blog("野生的气息逼近……<b>" + cfg.enemy.n + "</b> 出现了！");
  if (battleStatMods() < 1) blog("<span class='bad'>⚠️ 状态不佳（生病/饥饿），能力下降了……</span>");
  if (battleStatMods() > 1) blog("<span class='good'>💖 心情绝佳，能力提升！</span>");
  renderBattle();
  renderBattleActions(true);
}

function blog(html) {
  const box = document.getElementById("bLog");
  box.innerHTML += "<div>" + html + "</div>";
  box.scrollTop = box.scrollHeight;
}

function renderBattle() {
  const st = curStage(), e = B.enemy;
  document.getElementById("bEnemyName").textContent = e.e + " " + e.n;
  document.getElementById("bEnemyEmoji").textContent = e.e;
  document.getElementById("bEnemyHp").style.width = Math.max(0, e.hp / e.maxHp * 100) + "%";
  document.getElementById("bEnemyHpTxt").textContent = Math.max(0, Math.ceil(e.hp)) + " / " + e.maxHp;
  document.getElementById("bPetName").textContent = st.n + " Lv." + S.level;
  document.getElementById("bPetEmoji").textContent = st.e;
  document.getElementById("bPetHp").style.width = Math.max(0, S.hp / S.maxHp * 100) + "%";
  document.getElementById("bPetHpTxt").textContent = Math.max(0, Math.ceil(S.hp)) + " / " + S.maxHp + "　MP " + Math.ceil(S.mp) + "/" + S.maxMp;
  document.getElementById("bPetMp").style.width = Math.max(0, S.mp / S.maxMp * 100) + "%";
}

function renderBattleActions(enabled) {
  const st = curStage();
  const box = document.getElementById("bActions");
  if (!enabled) { box.innerHTML = "<p class='tip' style='grid-column:1/-1;text-align:center'>……</p>"; return; }
  const skill = st.s;
  const canSkill = S.mp >= skill[2];
  box.innerHTML = `
    <button class="act-btn" onclick="playerAct('attack')">👊 攻击<small>普通攻击 MP+5</small></button>
    <button class="act-btn ${canSkill ? "" : "disabled"}" onclick="playerAct('skill')">💥 ${skill[0]}<small>威力×${skill[1]} 消耗MP${skill[2]}</small></button>
    <button class="act-btn" onclick="playerAct('defend')">🛡️ 防御<small>伤害减半 MP+10</small></button>
    <button class="act-btn" onclick="playerAct('item')">🎒 道具<small>胶囊恢复</small></button>
    ${B.cfg.mode === "wild" ? `<button class="act-btn" onclick="playerAct('run')">🏃 逃跑<small>结束战斗</small></button>` : ""}
  `;
}

function dmgCalc(atk, mult, def) {
  let d = atk * mult - def * 0.5;
  d *= 0.85 + Math.random() * 0.3;
  let crit = Math.random() < 0.1;
  if (crit) d *= 1.5;
  return { d: Math.max(1, Math.round(d)), crit: crit };
}

function animHit(who) {
  const el = document.getElementById(who === "enemy" ? "bEnemyEmoji" : "bPetEmoji");
  el.classList.remove("hit"); void el.offsetWidth; el.classList.add("hit");
}
function animAct(who) {
  const el = document.getElementById(who === "enemy" ? "bEnemyEmoji" : "bPetEmoji");
  el.classList.remove("act"); void el.offsetWidth; el.classList.add("act");
}

function playerAct(action) {
  if (B.over) return;
  const st = curStage();
  const mod = battleStatMods();

  if (action === "run") {
    blog("你带着 " + st.n + " 成功脱离了战斗！");
    return endBattle("run");
  }
  if (action === "item") {
    const opts = [];
    if ((S.items.potion || 0) > 0) opts.push("potion");
    if ((S.items.mpot || 0) > 0) opts.push("mpot");
    if (!opts.length) { blog("<span class='bad'>背包里没有可用的胶囊！</span>"); return; }
    const box = document.getElementById("bActions");
    box.innerHTML = opts.map(k =>
      `<button class="act-btn" onclick="useBattleItem('${k}')">${ITEMS[k].e} ${ITEMS[k].n} ×${S.items[k]}<small>${ITEMS[k].desc}</small></button>`
    ).join("") + `<button class="act-btn" onclick="renderBattleActions(true)">↩️ 返回</button>`;
    return;
  }

  renderBattleActions(false);
  B.defending = false;
  let playerFirst = S.spd >= B.enemy.spd || Math.random() < 0.5;

  const playerMove = () => {
    if (B.over) return;
    animAct("player");
    if (action === "attack") {
      const r = dmgCalc(S.atk * mod, 1.0, B.enemy.def);
      B.enemy.hp -= r.d;
      S.mp = Math.min(S.maxMp, S.mp + 5);
      animHit("enemy");
      blog(st.n + " 发起攻击！造成 <b>" + r.d + "</b> 伤害" + (r.crit ? "<span class='crit'>（会心一击！）</span>" : ""));
    } else if (action === "skill") {
      if (S.mp < st.s[2]) { blog("<span class='bad'>MP不足！改为普通攻击。</span>"); return playerActFallback(mod); }
      S.mp -= st.s[2];
      const r = dmgCalc(S.atk * mod, st.s[1], B.enemy.def);
      B.enemy.hp -= r.d;
      animHit("enemy");
      blog("💥 " + st.n + " 使出【" + st.s[0] + "】！造成 <b>" + r.d + "</b> 伤害" + (r.crit ? "<span class='crit'>（会心一击！）</span>" : ""));
    } else if (action === "defend") {
      B.defending = true;
      S.mp = Math.min(S.maxMp, S.mp + 10);
      blog(st.n + " 摆出防御姿态，MP回复10。");
    }
    renderBattle();
  };

  const enemyMove = () => {
    if (B.over || B.enemy.hp <= 0) return;
    animAct("enemy");
    const e = B.enemy;
    const useSkill = Math.random() < 0.35;
    const mult = useSkill ? e.skill[1] : 1.0;
    const r = dmgCalc(e.atk, mult, S.def);
    let dmg = r.d;
    if (B.defending) { dmg = Math.max(1, Math.round(dmg / 2)); }
    S.hp -= dmg;
    animHit("player");
    blog(e.n + (useSkill ? " 使出【" + e.skill[0] + "】！" : " 发起攻击！") + "造成 <b>" + dmg + "</b> 伤害" +
      (r.crit ? "<span class='crit'>（会心！）</span>" : "") + (B.defending ? "<span class='good'>（防御减半）</span>" : ""));
    renderBattle();
  };

  // 按速度决定顺序，带一点延迟表现回合感
  const seq = playerFirst ? [playerMove, enemyMove] : [enemyMove, playerMove];
  seq[0]();
  if (checkBattleEnd()) return;
  setTimeout(() => {
    seq[1]();
    if (checkBattleEnd()) return;
    B.turn++;
    renderBattleActions(true);
  }, 650);
}

function playerActFallback(mod) {
  const st = curStage();
  const r = dmgCalc(S.atk * mod, 1.0, B.enemy.def);
  B.enemy.hp -= r.d;
  animHit("enemy");
  blog(st.n + " 发起攻击！造成 <b>" + r.d + "</b> 伤害");
  renderBattle();
}

function useBattleItem(k) {
  if (!S.items[k]) return;
  S.items[k]--;
  if (k === "potion") { S.hp = Math.min(S.maxHp, S.hp + S.maxHp * 0.6); blog("🧪 使用恢复胶囊，HP大幅回复！"); }
  if (k === "mpot") { S.mp = Math.min(S.maxMp, S.mp + S.maxMp * 0.6); blog("💙 使用MP胶囊，MP大幅回复！"); }
  renderBattle();
  // 使用道具不消耗回合太亏? 敌人行动一次
  setTimeout(() => {
    if (B.enemy.hp > 0) {
      const e = B.enemy;
      const r = dmgCalc(e.atk, 1.0, S.def);
      S.hp -= r.d;
      animHit("player");
      blog(e.n + " 趁机攻击！造成 <b>" + r.d + "</b> 伤害");
      renderBattle();
      if (checkBattleEnd()) return;
    }
    renderBattleActions(true);
  }, 500);
}

function checkBattleEnd() {
  if (B.enemy.hp <= 0) { endBattle("win"); return true; }
  if (S.hp <= 0) { S.hp = 1; endBattle("lose"); return true; }
  return false;
}

function endBattle(result) {
  B.over = true;
  inBattle = false;
  const e = B.enemy;
  const isStory = B.cfg.mode === "story";

  setTimeout(() => {
    document.getElementById("screen-battle").classList.add("hidden");
    document.getElementById("screen-main").classList.remove("hidden");

    if (result === "win") {
      let exp = e.exp, money = e.money;
      if (isStory && B.cfg.replay) { exp = Math.round(exp / 2); money = Math.round(money / 2); }
      S.money += money;
      gainExp(exp);
      let drop = "";
      if (Math.random() < 0.35) { S.items.meat = (S.items.meat || 0) + 1; drop = "\n战利品：🍖肉×1"; }
      S.care.mood = Math.min(100, S.care.mood + 5);
      addLog("⚔️ 战胜了 " + e.n + "！获得" + exp + "经验、" + money + "数码币。");

      if (isStory && !B.cfg.replay) {
        const c = CHAPTERS[B.cfg.idx];
        S.cleared = Math.max(S.cleared, B.cfg.idx + 1);
        save(); renderAll();
        showStory(c.name + " · 通关！", c.post + "\n\n🏆 获得：" + exp + "经验、" + money + "数码币" + drop, null);
      } else {
        save(); renderAll();
        showStory("🎉 胜利！", "打倒了 " + e.e + " " + e.n + "！\n\n获得：" + exp + "经验、" + money + "数码币" + drop, null);
      }
    } else if (result === "lose") {
      S.care.mood = Math.max(0, S.care.mood - 15);
      addLog("💔 被 " + e.n + " 打败了……先休息、训练，变强再来！");
      save(); renderAll();
      showStory("💔 战败……", curStage().n + " 倒下了……\n\n不过没关系，被选召的孩子是不会认输的！\n回去【休息】恢复状态、多做【训练】提升属性，或先打【自由对战】练级，再来挑战吧！", null);
    } else {
      save(); renderAll();
    }
  }, 700);
}
